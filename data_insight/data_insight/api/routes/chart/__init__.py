"""
图表API路由模块
============

提供图表分析和图表对比相关的API端点。
"""

from flask import Blueprint

# 创建图表蓝图
bp = Blueprint('chart', __name__, url_prefix='/api/chart')

# 导入视图函数
from data_insight.api.routes.chart.analysis import *
from data_insight.api.routes.chart.comparison import *

__all__ = ['bp'] 