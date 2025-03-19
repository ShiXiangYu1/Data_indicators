#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API速率限制中间件
=============

提供API速率限制功能，防止API滥用，包括基于IP、令牌和API密钥的限流功能。
"""

import time
import logging
import functools
from typing import Dict, List, Any, Callable, Optional, Tuple, Union
from collections import defaultdict

from flask import request, jsonify, current_app, g
from werkzeug.exceptions import TooManyRequests

from data_insight.api.utils.response_formatter import format_error_response


class RateLimiter:
    """速率限制器基类"""
    
    def __init__(self, limit: int = 100, window: int = 3600):
        """
        初始化速率限制器
        
        参数:
            limit (int, optional): 时间窗口内允许的最大请求数，默认为100
            window (int, optional): 时间窗口（秒），默认为3600（1小时）
        """
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)
    
    def get_key(self, request) -> str:
        """
        获取请求的唯一标识符
        
        参数:
            request: 当前请求对象
            
        返回:
            str: 请求的唯一标识符
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def is_allowed(self, request) -> Tuple[bool, int, int]:
        """
        检查请求是否被允许
        
        参数:
            request: 当前请求对象
            
        返回:
            Tuple[bool, int, int]: (是否允许, 剩余可用请求数, 重置时间)
        """
        key = self.get_key(request)
        now = time.time()
        
        # 清理过期的请求记录
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window]
        
        # 检查是否超出限制
        if len(self.requests[key]) >= self.limit:
            reset_time = int(self.requests[key][0] + self.window - now)
            return False, 0, reset_time
        
        # 记录当前请求
        self.requests[key].append(now)
        
        # 计算剩余可用请求数和重置时间
        remaining = self.limit - len(self.requests[key])
        if self.requests[key]:
            reset_time = int(self.requests[key][0] + self.window - now)
        else:
            reset_time = self.window
        
        return True, remaining, reset_time


class IPRateLimiter(RateLimiter):
    """基于IP的速率限制器"""
    
    def get_key(self, request) -> str:
        """
        获取请求的IP地址
        
        参数:
            request: 当前请求对象
            
        返回:
            str: 请求的IP地址
        """
        return request.remote_addr


class TokenRateLimiter(RateLimiter):
    """基于令牌的速率限制器"""
    
    def get_key(self, request) -> str:
        """
        获取请求的令牌
        
        参数:
            request: 当前请求对象
            
        返回:
            str: 请求的令牌，如果没有则返回IP地址
        """
        token = request.headers.get('X-API-Token')
        if token:
            return token
        return request.remote_addr


class APIKeyRateLimiter(RateLimiter):
    """基于API密钥的速率限制器"""
    
    def __init__(self, limit: int = 100, window: int = 3600, api_key_field: str = 'X-API-Key'):
        """
        初始化API密钥速率限制器
        
        参数:
            limit (int, optional): 时间窗口内允许的最大请求数，默认为100
            window (int, optional): 时间窗口（秒），默认为3600（1小时）
            api_key_field (str, optional): API密钥请求头字段名，默认为'X-API-Key'
        """
        super().__init__(limit, window)
        self.api_key_field = api_key_field
    
    def get_key(self, request) -> str:
        """
        获取请求的API密钥
        
        参数:
            request: 当前请求对象
            
        返回:
            str: 请求的API密钥，如果没有则返回IP地址
        """
        api_key = request.headers.get(self.api_key_field)
        if api_key:
            return api_key
        return request.remote_addr


class PathRateLimiter(RateLimiter):
    """基于路径的速率限制器"""
    
    def get_key(self, request) -> str:
        """
        获取请求的路径
        
        参数:
            request: 当前请求对象
            
        返回:
            str: 请求的路径
        """
        return f"{request.remote_addr}:{request.path}"


class RateLimiterManager:
    """速率限制器管理器"""
    
    def __init__(self, app=None):
        """
        初始化速率限制器管理器
        
        参数:
            app: Flask应用实例
        """
        self.limiters = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化应用
        
        参数:
            app: Flask应用实例
        """
        app.rate_limiter_manager = self
    
    def add_limiter(self, name: str, limiter: RateLimiter):
        """
        添加速率限制器
        
        参数:
            name (str): 速率限制器名称
            limiter (RateLimiter): 速率限制器实例
        """
        self.limiters[name] = limiter
    
    def get_limiter(self, name: str) -> Optional[RateLimiter]:
        """
        获取速率限制器
        
        参数:
            name (str): 速率限制器名称
            
        返回:
            Optional[RateLimiter]: 速率限制器实例，如果不存在则返回None
        """
        return self.limiters.get(name)


def rate_limit(limiter_name: str = 'default') -> Callable:
    """
    速率限制装饰器
    
    如果请求超出速率限制，则返回429错误
    
    参数:
        limiter_name (str, optional): 速率限制器名称，默认为'default'
        
    用法:
        @app.route('/api/resource')
        @rate_limit('ip')
        def resource():
            return "This is a rate-limited resource"
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
    def decorated(*args, **kwargs):
            try:
                # 获取速率限制器
                limiter = current_app.rate_limiter_manager.get_limiter(limiter_name)
                if not limiter:
                    # 如果速率限制器不存在，则继续执行被装饰的函数
            return f(*args, **kwargs)
        
                # 检查请求是否被允许
                allowed, remaining, reset_time = limiter.is_allowed(request)
                
                # 设置响应头
                response = None
                
                # 如果请求被允许，则继续执行被装饰的函数
                if allowed:
                    response = f(*args, **kwargs)
                else:
                    # 如果请求超出速率限制，则返回429错误
                    response = jsonify(format_error_response(
                        message="API速率限制已达到，请稍后再试",
                        status_code=429
                    ))
                    response.status_code = 429
            
            # 设置速率限制响应头
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(limiter.limit)
                    response.headers['X-RateLimit-Remaining'] = str(remaining)
                    response.headers['X-RateLimit-Reset'] = str(reset_time)
                
                return response
            
            except Exception as e:
                # 记录错误
                current_app.logger.error(f"速率限制错误: {str(e)}")
                
                # 返回500错误
                response = jsonify(format_error_response(
                    message=f"速率限制处理错误: {str(e)}",
                    status_code=500
                ))
                response.status_code = 500
                return response
        
        return decorated
    
    return decorator


def configure_rate_limiter(app):
    """
    配置速率限制器
    
    参数:
        app: Flask应用实例
    """
    # 初始化速率限制器管理器
    manager = RateLimiterManager(app)
    
    # 添加基于IP的速率限制器
    manager.add_limiter('ip', IPRateLimiter(
        limit=app.config.get('IP_RATE_LIMIT', 100),
        window=app.config.get('IP_RATE_WINDOW', 3600)
    ))
    
    # 添加基于令牌的速率限制器
    manager.add_limiter('token', TokenRateLimiter(
        limit=app.config.get('TOKEN_RATE_LIMIT', 1000),
        window=app.config.get('TOKEN_RATE_WINDOW', 3600)
    ))
    
    # 添加基于API密钥的速率限制器
    manager.add_limiter('api_key', APIKeyRateLimiter(
        limit=app.config.get('API_KEY_RATE_LIMIT', 5000),
        window=app.config.get('API_KEY_RATE_WINDOW', 3600),
        api_key_field=app.config.get('API_KEY_FIELD', 'X-API-Key')
    ))
    
    # 添加基于路径的速率限制器
    manager.add_limiter('path', PathRateLimiter(
        limit=app.config.get('PATH_RATE_LIMIT', 10),
        window=app.config.get('PATH_RATE_WINDOW', 60)
    ))
    
    # 设置默认速率限制器
    default_limiter_name = app.config.get('DEFAULT_RATE_LIMITER', 'ip')
    if default_limiter_name in manager.limiters:
        manager.add_limiter('default', manager.get_limiter(default_limiter_name))
    else:
        manager.add_limiter('default', IPRateLimiter(
            limit=app.config.get('DEFAULT_RATE_LIMIT', 100),
            window=app.config.get('DEFAULT_RATE_WINDOW', 3600)
        )) 