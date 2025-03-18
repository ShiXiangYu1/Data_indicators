"""
Web界面模块
=========

为数据指标平台提供Web界面，包括指标分析、图表分析、多维对比和预测等功能的页面。

子模块:
    routes: Web路由定义
    visualizers: 可视化组件
    forms: 表单处理类
"""

from flask import Blueprint

# 创建Web蓝图
web_bp = Blueprint(
    'web',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 导入路由定义
from . import routes

__all__ = ['web_bp'] 