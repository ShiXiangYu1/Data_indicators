#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康检查路由模块
==============

提供系统健康状态检查API。
"""

import time
import platform
import psutil
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from data_insight.utils.cache_manager import get_cache_manager
from data_insight.services.async_task_service import get_async_task_service

router = APIRouter(prefix="/health", tags=["健康检查"])

@router.get("/", summary="系统健康状态检查", 
            description="检查系统各组件的健康状态，包括API服务、缓存系统和异步任务服务")
async def health_check() -> Dict[str, Any]:
    """
    检查系统各组件的健康状态。
    
    返回:
        Dict[str, Any]: 包含系统状态信息的字典。
    """
    start_time = time.time()
    
    # 检查缓存系统状态
    cache_status = check_cache_status()
    
    # 检查异步任务服务状态
    task_service_status = check_task_service_status()
    
    # 检查系统资源状态
    system_status = check_system_status()
    
    # 构建响应
    response = {
        "status": "healthy" if all([
            cache_status.get("status") == "healthy",
            task_service_status.get("status") == "healthy",
            system_status.get("status") == "healthy"
        ]) else "unhealthy",
        "timestamp": time.time(),
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "components": {
            "cache": cache_status,
            "task_service": task_service_status,
            "system": system_status
        }
    }
    
    return response

@router.get("/liveness", summary="活跃性检查", 
            description="提供容器健康检查的活跃性检查端点，只检查API服务是否在运行")
async def liveness_check() -> Dict[str, str]:
    """
    提供容器健康检查的活跃性检查端点。
    
    返回:
        Dict[str, str]: 包含状态信息的字典。
    """
    return {"status": "alive"}

@router.get("/readiness", summary="就绪性检查", 
            description="提供容器健康检查的就绪性检查端点，检查系统是否准备好处理请求")
async def readiness_check() -> Dict[str, str]:
    """
    提供容器健康检查的就绪性检查端点。
    
    返回:
        Dict[str, str]: 包含状态信息的字典。
    """
    # 检查缓存系统状态
    cache_status = check_cache_status()
    
    # 检查异步任务服务状态
    task_service_status = check_task_service_status()
    
    # 检查结果
    if (cache_status.get("status") == "healthy" and 
        task_service_status.get("status") == "healthy"):
        return {"status": "ready"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务尚未就绪"
        )

def check_cache_status() -> Dict[str, Any]:
    """
    检查缓存系统状态。
    
    返回:
        Dict[str, Any]: 包含缓存状态信息的字典。
    """
    try:
        cache_manager = get_cache_manager()
        memory_cache = cache_manager.get_memory_cache()
        redis_cache = cache_manager.get_redis_cache()
        
        # 获取缓存统计信息
        memory_stats = memory_cache.get_stats() if memory_cache else None
        redis_stats = redis_cache.get_stats() if redis_cache else None
        
        # 检查Redis连接
        redis_available = False
        redis_info = None
        
        if redis_cache:
            try:
                redis_available = redis_cache.check_connection()
                if redis_available:
                    redis_info = redis_cache.get_info()
            except Exception:
                pass
        
        return {
            "status": "healthy",
            "memory_cache": {
                "available": True,
                "stats": memory_stats
            },
            "redis_cache": {
                "available": redis_available,
                "stats": redis_stats,
                "info": redis_info
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_task_service_status() -> Dict[str, Any]:
    """
    检查异步任务服务状态。
    
    返回:
        Dict[str, Any]: 包含任务服务状态信息的字典。
    """
    try:
        task_service = get_async_task_service()
        
        # 获取任务统计信息
        active_tasks = task_service.get_active_tasks()
        all_tasks = task_service.get_all_tasks()
        
        return {
            "status": "healthy",
            "is_running": task_service.is_running(),
            "active_tasks": len(active_tasks),
            "total_tasks": len(all_tasks),
            "max_workers": task_service.max_workers
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def check_system_status() -> Dict[str, Any]:
    """
    检查系统资源状态。
    
    返回:
        Dict[str, Any]: 包含系统资源状态信息的字典。
    """
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 判断系统状态
        is_healthy = (
            cpu_percent < 90 and
            memory.percent < 90 and
            disk.percent < 90
        )
        
        return {
            "status": "healthy" if is_healthy else "warning",
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "percent": disk.percent
            },
            "platform": {
                "system": platform.system(),
                "version": platform.version(),
                "python": platform.python_version()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 