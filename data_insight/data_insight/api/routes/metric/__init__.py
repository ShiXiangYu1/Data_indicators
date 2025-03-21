"""
指标API路由模块
============

提供指标分析和指标对比相关的API端点。
"""

from flask import Blueprint

# 创建指标蓝图
bp = Blueprint('metric', __name__, url_prefix='/api/metric')

# 导入视图函数
from data_insight.api.routes.metric.analysis import *
from data_insight.api.routes.metric.comparison import *

__all__ = ['bp'] 