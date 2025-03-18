"""
认证中间件
========

提供API认证功能。
"""

import os
from functools import wraps
from flask import request, jsonify, current_app


def require_api_token(f):
    """
    API令牌认证装饰器
    
    确保请求中包含有效的API令牌。
    
    参数:
        f (callable): 被装饰的函数
        
    返回:
        callable: 包装后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取令牌
        token = request.headers.get('X-API-Token')
        
        # 如果环境中没有设置API_TOKEN，或者处于调试模式，则跳过认证
        if not current_app.config.get('API_TOKEN') or current_app.debug:
            return f(*args, **kwargs)
        
        # 验证令牌
        if not token or token != current_app.config.get('API_TOKEN'):
            return jsonify({
                'error': '未授权访问',
                'message': '缺少有效的API令牌',
                'status_code': 401
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated


def check_api_token():
    """
    检查API令牌是否有效
    
    如果请求中包含有效的API令牌，返回True；否则返回False。
    
    返回:
        bool: 令牌是否有效
    """
    # 从请求头获取令牌
    token = request.headers.get('X-API-Token')
    
    # 如果环境中没有设置API_TOKEN，或者处于调试模式，则跳过认证
    if not current_app.config.get('API_TOKEN') or current_app.debug:
        return True
    
    # 验证令牌
    return token and token == current_app.config.get('API_TOKEN') 