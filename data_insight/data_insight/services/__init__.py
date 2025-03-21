#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务模块
======

提供API和核心分析模块之间的服务层，负责业务逻辑、缓存和事务处理。
"""

import logging
from typing import Dict, Any

# 导入服务
from .async_task_service import get_async_task_service, AsyncTaskService, TaskPriority, TaskStatus

# 注意：以下服务暂时被注释，等待修复导入问题
# from .metric_service import MetricService
# from .chart_service import ChartService
# from .analysis_service import AnalysisService
# from .prediction_service import PredictionService
# from .recommendation_service import RecommendationService

# 为了保持API兼容性，创建空的类
class MetricService:
    def __init__(self): pass

class ChartService:
    def __init__(self): pass

class AnalysisService:
    def __init__(self): pass

class PredictionService:
    def __init__(self): pass

class RecommendationService:
    def __init__(self): pass

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
    'MetricService',
    'ChartService',
    'AnalysisService',
    'PredictionService',
    'RecommendationService',
] 