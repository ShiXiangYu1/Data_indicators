#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API文档路由模块
=============

提供API文档访问和Swagger/ReDoc UI。
"""

import os
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/docs", tags=["API文档"])

# API端点信息
API_ENDPOINTS = {
    "trend": {
        "title": "趋势分析API",
        "description": "分析时间序列数据的变化趋势，识别上升、下降、周期性和季节性模式。",
        "endpoints": [
            {
                "path": "/api/v1/trend/analyze",
                "method": "POST",
                "summary": "分析时间序列数据的变化趋势"
            },
            {
                "path": "/api/v1/trend/analyze-async",
                "method": "POST",
                "summary": "异步分析时间序列数据的变化趋势"
            }
        ],
        "doc_url": "/docs/api/trend"
    },
    "attribution": {
        "title": "归因分析API",
        "description": "分析指标变化的归因因素，确定哪些因素对指标变化贡献最大。",
        "endpoints": [
            {
                "path": "/api/v1/attribution",
                "method": "POST",
                "summary": "分析指标变化的归因因素"
            },
            {
                "path": "/api/v1/attribution-async",
                "method": "POST",
                "summary": "异步分析指标变化的归因因素"
            }
        ],
        "doc_url": "/docs/api/attribution"
    },
    "root-cause": {
        "title": "根因分析API",
        "description": "深入挖掘指标变化的根本原因，通过多层次因果分析找出深层次原因。",
        "endpoints": [
            {
                "path": "/api/v1/root-cause",
                "method": "POST",
                "summary": "分析指标变化的根本原因"
            },
            {
                "path": "/api/v1/root-cause-async",
                "method": "POST",
                "summary": "异步分析指标变化的根本原因"
            }
        ],
        "doc_url": "/docs/api/root-cause"
    },
    "correlation": {
        "title": "相关性分析API",
        "description": "分析指标之间的相关性，识别强相关、弱相关和无相关的指标对。",
        "endpoints": [
            {
                "path": "/api/v1/correlation",
                "method": "POST",
                "summary": "分析指标之间的相关性"
            },
            {
                "path": "/api/v1/correlation-async",
                "method": "POST",
                "summary": "异步分析指标之间的相关性"
            }
        ],
        "doc_url": "/docs/api/correlation"
    },
    "prediction": {
        "title": "预测分析API",
        "description": "预测指标的未来走势，支持时间序列预测和异常检测。",
        "endpoints": [
            {
                "path": "/api/v1/forecast",
                "method": "POST",
                "summary": "预测指标未来值"
            },
            {
                "path": "/api/v1/forecast-async",
                "method": "POST",
                "summary": "异步预测指标未来值"
            },
            {
                "path": "/api/v1/anomaly",
                "method": "POST",
                "summary": "检测时间序列中的异常值"
            },
            {
                "path": "/api/v1/anomaly-async",
                "method": "POST",
                "summary": "异步检测时间序列中的异常值"
            }
        ],
        "doc_url": "/docs/api/prediction"
    },
    "metric": {
        "title": "指标分析API",
        "description": "分析单个指标的特征和变化，并比较多个指标之间的差异和关系。",
        "endpoints": [
            {
                "path": "/api/v1/analyze",
                "method": "POST",
                "summary": "分析单个指标的特征和变化"
            },
            {
                "path": "/api/v1/analyze-async",
                "method": "POST",
                "summary": "异步分析单个指标的特征和变化"
            },
            {
                "path": "/api/v1/compare",
                "method": "POST",
                "summary": "比较多个指标之间的差异和关系"
            }
        ],
        "doc_url": "/docs/api/metric"
    },
    "chart": {
        "title": "图表分析API",
        "description": "分析图表数据，自动生成适合数据特征的可视化图表。",
        "endpoints": [
            {
                "path": "/api/v1/chart/analyze",
                "method": "POST",
                "summary": "分析图表数据"
            },
            {
                "path": "/api/v1/chart/generate",
                "method": "POST",
                "summary": "生成可视化图表"
            }
        ],
        "doc_url": "/docs/api/chart"
    }
}

@router.get("/", summary="API文档首页", 
            description="展示API文档首页，列出所有可用的API端点")
async def docs_index() -> Dict[str, Any]:
    """
    API文档首页。
    
    返回:
        Dict[str, Any]: 包含API文档信息的字典。
    """
    return {
        "title": "数据指标分析API文档",
        "version": "1.0.0",
        "description": "提供数据指标分析相关的API，包括趋势分析、归因分析、根因分析、相关性分析、预测分析和指标分析。",
        "apis": API_ENDPOINTS
    }

@router.get("/api/{api_name}", summary="获取特定API文档", 
            description="获取特定API的详细文档信息")
async def api_docs(api_name: str) -> Dict[str, Any]:
    """
    获取特定API的详细文档信息。
    
    参数:
        api_name (str): API名称
        
    返回:
        Dict[str, Any]: 包含API文档信息的字典。
    """
    if api_name not in API_ENDPOINTS:
        return JSONResponse(
            status_code=404,
            content={"error": f"未找到API: {api_name}"}
        )
    
    return API_ENDPOINTS[api_name]

@router.get("/endpoints", summary="获取所有API端点列表", 
            description="获取所有可用的API端点列表")
async def endpoints_list() -> Dict[str, Any]:
    """
    获取所有可用的API端点列表。
    
    返回:
        Dict[str, Any]: 包含所有API端点信息的字典。
    """
    all_endpoints = []
    
    for api_group in API_ENDPOINTS.values():
        all_endpoints.extend(api_group["endpoints"])
    
    return {
        "total": len(all_endpoints),
        "endpoints": all_endpoints
    }

@router.get("/health", summary="获取健康检查API文档", 
            description="获取健康检查API的详细文档信息")
async def health_docs() -> Dict[str, Any]:
    """
    获取健康检查API的详细文档信息。
    
    返回:
        Dict[str, Any]: 包含健康检查API文档信息的字典。
    """
    return {
        "title": "健康检查API",
        "description": "检查API服务的健康状态，包括组件健康状态、活跃性和就绪性检查。",
        "endpoints": [
            {
                "path": "/health",
                "method": "GET",
                "summary": "检查系统健康状态"
            },
            {
                "path": "/health/liveness",
                "method": "GET",
                "summary": "活跃性检查"
            },
            {
                "path": "/health/readiness",
                "method": "GET",
                "summary": "就绪性检查"
            }
        ]
    } 