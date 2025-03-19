#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web视图模块
==========

提供系统Web界面的路由和视图函数。
"""

import os
import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

# 创建路由器
web_bp = APIRouter(prefix="/web", tags=["Web界面"])

# 创建日志记录器
logger = logging.getLogger(__name__)

# 确定模板目录路径
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "static")

# 创建模板引擎
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@web_bp.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Web首页
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "数据指标分析系统"
        }
    )


@web_bp.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """
    仪表盘页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "分析仪表盘"
        }
    )


@web_bp.get("/trend-analysis", response_class=HTMLResponse)
async def trend_analysis(request: Request) -> HTMLResponse:
    """
    趋势分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "trend_analysis.html",
        {
            "request": request,
            "title": "趋势分析"
        }
    )


@web_bp.get("/correlation-analysis", response_class=HTMLResponse)
async def correlation_analysis(request: Request) -> HTMLResponse:
    """
    相关性分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "correlation_analysis.html",
        {
            "request": request,
            "title": "相关性分析"
        }
    )


@web_bp.get("/attribution-analysis", response_class=HTMLResponse)
async def attribution_analysis(request: Request) -> HTMLResponse:
    """
    归因分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "attribution_analysis.html",
        {
            "request": request,
            "title": "归因分析"
        }
    )


@web_bp.get("/reason-analysis", response_class=HTMLResponse)
async def reason_analysis(request: Request) -> HTMLResponse:
    """
    原因分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "reason_analysis.html",
        {
            "request": request,
            "title": "原因分析"
        }
    )


@web_bp.get("/root-cause-analysis", response_class=HTMLResponse)
async def root_cause_analysis(request: Request) -> HTMLResponse:
    """
    根因分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "root_cause_analysis.html",
        {
            "request": request,
            "title": "根因分析"
        }
    )


@web_bp.get("/prediction-analysis", response_class=HTMLResponse)
async def prediction_analysis(request: Request) -> HTMLResponse:
    """
    预测分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "prediction_analysis.html",
        {
            "request": request,
            "title": "预测分析"
        }
    )


@web_bp.get("/metric-analysis", response_class=HTMLResponse)
async def metric_analysis(request: Request) -> HTMLResponse:
    """
    指标分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "metric_analysis.html",
        {
            "request": request,
            "title": "指标分析"
        }
    )


@web_bp.get("/chart-analysis", response_class=HTMLResponse)
async def chart_analysis(request: Request) -> HTMLResponse:
    """
    图表分析页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "chart_analysis.html",
        {
            "request": request,
            "title": "图表分析"
        }
    )


@web_bp.get("/export", response_class=HTMLResponse)
async def export_page(request: Request) -> HTMLResponse:
    """
    导出页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "export.html",
        {
            "request": request,
            "title": "导出分析结果"
        }
    )


@web_bp.get("/api-documentation", response_class=HTMLResponse)
async def api_documentation(request: Request) -> HTMLResponse:
    """
    API文档页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "api_documentation.html",
        {
            "request": request,
            "title": "API文档"
        }
    )


@web_bp.get("/user-guide", response_class=HTMLResponse)
async def user_guide(request: Request) -> HTMLResponse:
    """
    用户指南页面
    
    返回:
        HTMLResponse: 渲染后的HTML响应
    """
    return templates.TemplateResponse(
        "user_guide.html",
        {
            "request": request,
            "title": "用户指南"
        }
    )


def register_web_views(app) -> None:
    """
    注册Web视图路由
    
    参数:
        app: FastAPI应用实例
    """
    # 挂载静态文件目录
    if os.path.exists(STATIC_DIR):
        app.mount("/web/static", StaticFiles(directory=STATIC_DIR), name="web_static")
    
    # 包含Web路由
    app.include_router(web_bp)
    
    logger.info("Web视图路由已注册") 