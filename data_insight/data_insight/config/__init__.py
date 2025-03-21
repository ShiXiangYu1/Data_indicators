"""
配置管理模块
=========

统一管理数据指标平台的配置项，包括基础设置、日志、数据库和API配置。
"""

from data_insight.config.settings import Settings

# 创建全局设置实例
settings = Settings()

__all__ = ['settings'] 