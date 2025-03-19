#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务模块
======

提供各种服务功能的访问接口。
"""

import logging
from typing import Dict, Any

# 导入服务
from .async_task_service import get_async_task_service, AsyncTaskService, TaskPriority, TaskStatus

# 设置日志记录器
logger = logging.getLogger(__name__)


def init_services(config: Dict[str, Any] = None) -> bool:
    """
    初始化所有服务
    
    参数:
        config (Dict[str, Any], optional): 服务配置
        
    返回:
        bool: 初始化是否成功
    """
    logger.info("初始化服务...")
    
    # 初始化异步任务服务
    async_task_service = get_async_task_service()
    logger.info("异步任务服务已初始化")
    
    logger.info("所有服务初始化完成")
    
    return True


__all__ = [
    'get_async_task_service',
    'AsyncTaskService',
    'TaskPriority',
    'TaskStatus',
    'init_services',
] 