#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用入口模块
===========

FastAPI应用程序实例创建与配置。
"""

import os
import time
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from data_insight.api.middlewares.auth import token_required
from data_insight.api.routes.health import router as health_router
from data_insight.api.routes.docs import router as docs_router
from data_insight.api.routes.trend_api import router as trend_router
from data_insight.api.routes.analysis_api import router as analysis_router
from data_insight.api.routes.prediction_api import router as prediction_router
from data_insight.api.routes.metrics import router as metrics_router
from data_insight.api.routes.export import router as export_router
from data_insight.api.routes.suggestion import router as suggestion_router
from data_insight.api.routes.metric_api import router as metric_router
from data_insight.api.routes.chart_api import router as chart_router
from data_insight.utils.metrics import increment_request_count, record_request_duration
from data_insight.web import register_web_views
from data_insight.services import init_services
from data_insight.utils import get_cache_manager
from data_insight.utils.metrics import (
    get_metrics_registry
)

# 设置日志
logger = logging.getLogger(__name__)


def create_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """
    创建并配置FastAPI应用实例
    
    参数:
        config (Dict[str, Any], optional): 应用配置
        
    返回:
        FastAPI: 配置好的FastAPI应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(
        title="数据指标分析系统",
        description="提供指标分析、图表分析、趋势分析等功能的API",
        version="1.0.0",
        docs_url=None,  # 禁用默认的Swagger UI路径
        redoc_url=None,  # 禁用默认的ReDoc路径
        openapi_url="/openapi.json",
    )
    
    # 加载配置
    app_config = {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev_key"),
        "API_KEY": os.environ.get("API_KEY", None),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
        "LOG_FILE": os.environ.get("LOG_FILE", None),
        "CORS_ORIGINS": os.environ.get("CORS_ORIGINS", "*").split(","),
        "REDIS_HOST": os.environ.get("REDIS_HOST", "localhost"),
        "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
        "REDIS_PASSWORD": os.environ.get("REDIS_PASSWORD", None),
        "CACHE_TTL": int(os.environ.get("CACHE_TTL", 3600)),
        "MAX_WORKERS": int(os.environ.get("MAX_WORKERS", 4)),
        "ENVIRONMENT": os.environ.get("ENVIRONMENT", "development"),
        "DEFAULT_THROTTLE_RATE": int(os.environ.get("DEFAULT_THROTTLE_RATE", 100)),
    }
    
    # 合并自定义配置
    if config:
        app_config.update(config)
    
    # 将配置添加到应用状态
    app.state.config = app_config
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config["CORS_ORIGINS"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加处理时间中间件
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        # 排除指标路由本身，避免无限递归
        if not request.url.path.startswith("/metrics"):
            start_time = time.time()
            
        response = await call_next(request)
        
        if not request.url.path.startswith("/metrics"):
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # 记录请求计数和处理时间
            increment_request_count(request.url.path, request.method, response.status_code)
            record_request_duration(request.url.path, request.method, process_time)
        
        return response
    
    # 注册健康检查路由
    app.include_router(health_router, prefix="/health")
    
    # 注册API文档路由
    app.include_router(docs_router, prefix="/docs")
    
    # 注册分析API路由
    app.include_router(trend_router, prefix="/api/v1/trend")
    app.include_router(analysis_router, prefix="/api/v1/analysis")
    app.include_router(prediction_router, prefix="/api/v1/prediction")
    
    # 注册智能建议路由
    app.include_router(suggestion_router, prefix="/api/v1/suggestion")
    
    # 注册指标和图表API
    app.include_router(metric_router, prefix="/api/v1")
    app.include_router(chart_router, prefix="/api/v1")
    
    # 注册监控指标路由
    app.include_router(metrics_router)
    
    # 注册导出路由
    app.include_router(export_router, prefix="/api/v1")
    
    # 挂载静态文件
    app.mount("/static", StaticFiles(directory="data_insight/static"), name="static")
    
    # 注册Web视图
    register_web_views(app)
    
    # 自定义Swagger UI路由
    @app.get("/api/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="数据指标分析系统API文档",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
    
    # 自定义ReDoc路由
    @app.get("/api/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title="数据指标分析系统API文档 - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )
    
    # 根路由
    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse({
            "name": "数据指标分析系统",
            "version": "1.0.0",
            "description": "提供指标分析、图表分析、趋势分析等功能的API",
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "web": "/web",
            "health": "/health"
        })
    
    # 应用启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动时执行的操作"""
        logger.info("应用正在启动...")
        
        # 初始化缓存
        cache_manager = get_cache_manager(config)
        logger.info("缓存管理器已初始化")
        
        # 初始化服务
        if init_services(config):
            logger.info("所有服务已初始化")
        else:
            logger.error("服务初始化失败")
        
        # 初始化指标
        get_metrics_registry()
        
        logger.info("应用启动完成")
    
    # 应用关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时执行的操作"""
        logger.info("应用正在关闭...")
        
        # 在这里添加清理资源的代码
        
        logger.info("应用已关闭")
    
    return app


# 创建应用实例
app = create_app() 