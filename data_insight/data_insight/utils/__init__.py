#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模块
======

提供各种实用工具函数和类。
"""

import logging
from typing import Dict, Any

# 导入缓存管理器
from .cache_manager import CacheManager

# 创建日志记录器
logger = logging.getLogger(__name__)

# 全局变量，保存单例实例
_cache_manager = None


def get_cache_manager(config: Dict[str, Any] = None) -> CacheManager:
    """
    获取缓存管理器实例（单例模式）
    
    参数:
        config (Dict[str, Any], optional): 缓存配置
        
    返回:
        CacheManager: 缓存管理器实例
    """
    global _cache_manager
    
    # 如果缓存管理器尚未初始化，则创建一个新实例
    if _cache_manager is None:
        logger.info("初始化缓存管理器")
        _cache_manager = CacheManager(config)
    
    return _cache_manager

"""
工具函数模块
==========

包含用于数据处理和文本处理的工具函数。

子模块:
    data_utils: 数据处理工具函数
    text_utils: 文本处理工具函数
""" 