"""
API接口模块
==========

提供数据指标平台的RESTful API接口。

子模块:
    app: Flask应用程序实例
    routes: API路由定义
    controllers: API控制器
    middlewares: 中间件
    utils: 工具函数
"""

from .app import create_app

__all__ = ['create_app'] 