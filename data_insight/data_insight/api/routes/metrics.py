#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标路由模块
==========

提供系统监控指标的导出接口，支持Prometheus格式。
"""

from fastapi import APIRouter, Request, Response
from data_insight.utils.metrics import get_metrics_registry

router = APIRouter(prefix="/metrics", tags=["监控指标"])

@router.get("/", summary="获取Prometheus格式的监控指标", 
            description="获取所有系统和应用监控指标，使用Prometheus格式")
async def prometheus_metrics(request: Request) -> Response:
    """
    获取Prometheus格式的监控指标。
    
    返回:
        Response: 包含Prometheus格式监控指标的响应
    """
    registry = get_metrics_registry()
    metrics_data = registry.get_prometheus_metrics()
    
    return Response(
        content=metrics_data,
        media_type="text/plain"
    )

@router.get("/json", summary="获取JSON格式的监控指标", 
            description="获取所有系统和应用监控指标，使用JSON格式")
async def json_metrics(request: Request) -> dict:
    """
    获取JSON格式的监控指标。
    
    返回:
        dict: 包含所有监控指标的字典
    """
    registry = get_metrics_registry()
    return registry.get_all_metrics()

@router.post("/reset", summary="重置所有监控指标", 
             description="重置所有监控指标为初始值")
async def reset_metrics(request: Request) -> dict:
    """
    重置所有监控指标为初始值。
    
    返回:
        dict: 操作结果
    """
    registry = get_metrics_registry()
    registry.reset()
    
    return {
        "success": True,
        "message": "所有监控指标已重置"
    } 