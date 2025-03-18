#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标解读API服务
===============

提供数据指标解读系统的Web API接口，包括指标分析、图表分析、原因分析和行动建议生成等功能。
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

from data_insight.core.metric_analyzer import MetricAnalyzer
from data_insight.core.chart_analyzer import ChartAnalyzer
from data_insight.core.metric_comparison_analyzer import MetricComparisonAnalyzer
from data_insight.core.reason_analyzer import ReasonAnalyzer
from data_insight.core.action_suggester import ActionSuggester
from data_insight.core.text_generator import TextGenerator
from data_insight.models.insight_model import MetricInsight
from data_insight.api.middlewares.error_handlers import register_error_handlers
from data_insight.api.middlewares.rate_limiter import RateLimiter
from data_insight.api.utils.response_formatter import format_success_response, format_error_response, ApiJSONEncoder


# 加载环境变量
load_dotenv()

def create_app(config=None):
    """
    创建Flask应用
    
    参数:
        config (dict, optional): 应用配置
        
    返回:
        Flask: Flask应用实例
    """
    # 创建Flask应用
    app = Flask('data_insight_api')
    
    # 配置JSON编码器，支持更多数据类型
    app.json_encoder = ApiJSONEncoder
    
    # 配置应用
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        DEBUG=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        API_TOKEN=os.environ.get('API_TOKEN', None),
        MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 限制请求体大小为10MB
    )
    
    # 应用自定义配置
    if config:
        app.config.update(config)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初始化速率限制器
    limit = int(os.environ.get('API_RATE_LIMIT', '60'))
    window = int(os.environ.get('API_RATE_WINDOW', '60'))
    app.rate_limiter = RateLimiter(limit=limit, window=window)
    
    # 注册错误处理函数
    register_error_handlers(app)
    
    # 注册请求前处理函数
    @app.before_request
    def before_request():
        # 记录请求开始时间，用于计算处理时间
        request.start_time = datetime.now()
    
    # 注册请求后处理函数
    @app.after_request
    def after_request(response):
        # 添加跨域支持
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Token')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        
        # 计算请求处理时间
        if hasattr(request, 'start_time'):
            process_time = (datetime.now() - request.start_time).total_seconds()
            # 将处理时间添加到响应头
            response.headers.add('X-Process-Time', str(process_time))
        
        return response
    
    # 注册路由蓝图
    register_blueprints(app)
    
    # 添加默认首页路由
    @app.route('/')
    def index():
        """API首页"""
        return jsonify(format_success_response(
            data={
                "name": "数据指标平台API",
                "version": "0.1.0",
                "description": "提供数据指标分析和洞察生成的API接口",
                "documentation": "/api/docs"
            },
            message="欢迎使用数据指标平台API"
        ))
    
    # 添加健康检查路由
    @app.route('/health')
    def health_check():
        """健康检查"""
        return jsonify(format_success_response(
            data={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "0.1.0"
            },
            message="服务运行正常"
        ))
    
    # 添加API文档路由
    @app.route('/api/docs')
    def api_docs():
        """API文档"""
        endpoints = []
        
        # 收集所有路由信息
        for rule in app.url_map.iter_rules():
            # 排除静态资源路由
            if not str(rule).startswith('/static'):
                endpoints.append({
                    "path": str(rule),
                    "methods": list(rule.methods - {'HEAD', 'OPTIONS'}),
                    "endpoint": rule.endpoint
                })
        
        # 按路径排序
        endpoints.sort(key=lambda x: x["path"])
        
        # 返回API文档
        return jsonify(format_success_response(
            data={
                "api_name": "数据指标平台API",
                "version": "0.1.0",
                "base_url": request.host_url.rstrip('/'),
                "endpoints": endpoints,
                "authentication": "通过X-API-Token请求头进行认证"
            },
            message="API文档"
        ))
    
    return app


def register_blueprints(app):
    """
    注册所有蓝图
    
    参数:
        app (Flask): Flask应用实例
    """
    # 导入蓝图
    from data_insight.api.routes.metric_api import bp as metric_bp
    from data_insight.api.routes.chart_api import bp as chart_bp
    from data_insight.api.routes.analysis_api import bp as analysis_bp
    from data_insight.api.routes.prediction_api import bp as prediction_bp
    
    # 注册蓝图
    app.register_blueprint(metric_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(prediction_bp)


# 设置默认导出
__all__ = ['create_app']


if __name__ == '__main__':
    # 获取端口配置，默认为5000
    port = int(os.environ.get("PORT", 5000))
    
    # 是否开启调试模式
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    # 启动服务
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=debug) 