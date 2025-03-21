#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API文档路由
=========

提供API文档页面。
"""

import os
from flask import Blueprint, send_from_directory, redirect, url_for
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建蓝图
bp = Blueprint('api_docs', __name__, url_prefix='/api')

@bp.route('/docs')
def api_docs():
    """API文档页面"""
    # 返回静态HTML文件
    logger.info("访问API文档页面")
    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(os.path.dirname(os.path.dirname(module_dir)), 'api', 'static')
    return send_from_directory(static_dir, 'api_docs.html')

@bp.route('/docs/swagger')
def swagger_redirect():
    """重定向到API文档页面"""
    return redirect(url_for('api_docs.api_docs'))

@bp.route('/docs/redoc')
def redoc_redirect():
    """重定向到API文档页面"""
    return redirect(url_for('api_docs.api_docs'))

@bp.route('/docs/openapi.json')
def openapi_json():
    """OpenAPI规范JSON"""
    logger.info("访问OpenAPI规范JSON")
    # 在这里可以返回实际的OpenAPI规范
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "数据指标平台API",
            "description": "数据指标平台API文档",
            "version": "0.1.0"
        },
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "健康检查",
                    "description": "检查API服务是否正常运行",
                    "responses": {
                        "200": {
                            "description": "服务正常运行"
                        }
                    }
                }
            }
        }
    }
