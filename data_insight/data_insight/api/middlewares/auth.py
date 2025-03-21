#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API身份验证中间件
==============

提供API访问控制和身份验证功能，包括令牌验证、角色权限和IP白名单等。
"""

import os
import time
import hashlib
import hmac
import logging
import functools
from typing import Dict, Any, List, Optional, Callable, Union, Set, Tuple

from flask import request, current_app, g, jsonify, Response
from werkzeug.exceptions import Unauthorized, Forbidden

from data_insight.api.utils.response_formatter import format_error_response


# 权限常量
class Permissions:
    """API权限常量"""
    READ = "read"              # 读取数据的权限
    WRITE = "write"            # 写入数据的权限
    ADMIN = "admin"            # 管理员权限


# 默认角色与权限映射
DEFAULT_ROLE_PERMISSIONS = {
    "viewer": {Permissions.READ},
    "editor": {Permissions.READ, Permissions.WRITE},
    "admin": {Permissions.READ, Permissions.WRITE, Permissions.ADMIN}
}


class AuthenticationError(Exception):
    """身份验证错误异常"""
    pass


def token_required(f: Callable) -> Callable:
    """
    验证API令牌的装饰器
    
    如果请求中没有有效的API令牌，则返回401未授权错误
    
    用法:
        @app.route('/api/protected')
        @token_required
        def protected_route():
            return "This is a protected route"
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 从请求头中获取令牌
            token = request.headers.get('X-API-Token')
            
            # 如果环境中未设置API令牌，则跳过验证
            if not current_app.config.get('API_TOKEN'):
                return f(*args, **kwargs)
            
            # 如果请求中没有令牌，则返回401错误
            if not token:
                response = jsonify(format_error_response(
                    message="未提供API令牌",
                    status_code=401
                ))
                response.status_code = 401
                return response
            
            # 验证令牌是否有效
            if token != current_app.config.get('API_TOKEN'):
                response = jsonify(format_error_response(
                    message="无效的API令牌",
                    status_code=401
                ))
                response.status_code = 401
                return response
            
            # 设置已验证标志
            g.authenticated = True
            
            # 如果令牌有效，则继续执行被装饰的函数
            return f(*args, **kwargs)
        
        except Exception as e:
            # 记录错误
            current_app.logger.error(f"身份验证错误: {str(e)}")
            
            # 返回401错误
            response = jsonify(format_error_response(
                message=f"身份验证失败: {str(e)}",
                status_code=401
            ))
            response.status_code = 401
            return response
    
    return decorated


def role_required(required_role: Union[str, List[str]]) -> Callable:
    """
    验证用户角色的装饰器
    
    如果用户没有所需的角色，则返回403禁止错误
    
    参数:
        required_role (Union[str, List[str]]): 所需的角色，可以是单个角色或角色列表
        
    用法:
        @app.route('/api/admin')
        @token_required
        @role_required('admin')
        def admin_route():
            return "This is an admin route"
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 验证用户是否已通过身份验证
                if not getattr(g, 'authenticated', False):
                    # 如果用户未通过身份验证，则返回401错误
                    response = jsonify(format_error_response(
                        message="未经过身份验证，请先获取有效的API令牌",
                        status_code=401
                    ))
                    response.status_code = 401
                    return response
                
                # 获取用户角色
                user_role = request.headers.get('X-User-Role', 'viewer')
                
                # 转换为列表
                if isinstance(required_role, str):
                    required_roles = [required_role]
                else:
                    required_roles = required_role
                
                # 验证用户是否具有所需角色
                if user_role not in required_roles:
                    # 如果用户没有所需角色，则返回403错误
                    response = jsonify(format_error_response(
                        message=f"没有权限访问此资源，需要角色: {', '.join(required_roles)}",
                        status_code=403
                    ))
                    response.status_code = 403
                    return response
                
                # 如果用户具有所需角色，则继续执行被装饰的函数
                return f(*args, **kwargs)
            
            except Exception as e:
                # 记录错误
                current_app.logger.error(f"角色验证错误: {str(e)}")
                
                # 返回403错误
                response = jsonify(format_error_response(
                    message=f"权限验证失败: {str(e)}",
                    status_code=403
                ))
                response.status_code = 403
                return response
        
        return decorated
    
    return decorator


def permission_required(required_permission: Union[str, List[str]]) -> Callable:
    """
    验证用户权限的装饰器
    
    如果用户没有所需的权限，则返回403禁止错误
    
    参数:
        required_permission (Union[str, List[str]]): 所需的权限，可以是单个权限或权限列表
        
    用法:
        @app.route('/api/admin')
        @token_required
        @permission_required(Permissions.ADMIN)
        def admin_route():
            return "This is an admin route"
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 验证用户是否已通过身份验证
                if not getattr(g, 'authenticated', False):
                    # 如果用户未通过身份验证，则返回401错误
                    response = jsonify(format_error_response(
                        message="未经过身份验证，请先获取有效的API令牌",
                        status_code=401
                    ))
                    response.status_code = 401
                    return response
                
                # 获取用户角色
                user_role = request.headers.get('X-User-Role', 'viewer')
                
                # 获取角色权限
                role_permissions = getattr(current_app, 'role_permissions', DEFAULT_ROLE_PERMISSIONS)
                user_permissions = role_permissions.get(user_role, set())
                
                # 转换为列表
                if isinstance(required_permission, str):
                    required_permissions = [required_permission]
                else:
                    required_permissions = required_permission
                
                # 验证用户是否具有所需权限
                if not any(perm in user_permissions for perm in required_permissions):
                    # 如果用户没有所需权限，则返回403错误
                    response = jsonify(format_error_response(
                        message=f"没有权限执行此操作，需要权限: {', '.join(required_permissions)}",
                        status_code=403
                    ))
                    response.status_code = 403
                    return response
                
                # 如果用户具有所需权限，则继续执行被装饰的函数
                return f(*args, **kwargs)
            
            except Exception as e:
                # 记录错误
                current_app.logger.error(f"权限验证错误: {str(e)}")
                
                # 返回403错误
                response = jsonify(format_error_response(
                    message=f"权限验证失败: {str(e)}",
                    status_code=403
                ))
                response.status_code = 403
                return response
        
        return decorated
    
    return decorator


def ip_whitelist(allowed_ips: Union[str, List[str]]) -> Callable:
    """
    IP白名单装饰器
    
    如果请求的IP地址不在允许的IP列表中，则返回403禁止错误
    
    参数:
        allowed_ips (Union[str, List[str]]): 允许的IP地址列表
        
    用法:
        @app.route('/api/admin')
        @ip_whitelist(['127.0.0.1', '192.168.1.1'])
        def admin_route():
            return "This is an admin route"
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 获取客户端IP地址
                client_ip = request.remote_addr
                
                # 转换为列表
                if isinstance(allowed_ips, str):
                    whitelist = [allowed_ips]
                else:
                    whitelist = allowed_ips
                
                # 验证IP地址是否在白名单中
                if client_ip not in whitelist:
                    # 如果IP地址不在白名单中，则返回403错误
                    response = jsonify(format_error_response(
                        message="IP地址不在白名单中",
                        status_code=403
                    ))
                    response.status_code = 403
                    return response
                
                # 如果IP地址在白名单中，则继续执行被装饰的函数
                return f(*args, **kwargs)
            
            except Exception as e:
                # 记录错误
                current_app.logger.error(f"IP白名单验证错误: {str(e)}")
                
                # 返回403错误
                response = jsonify(format_error_response(
                    message=f"IP验证失败: {str(e)}",
                    status_code=403
                ))
                response.status_code = 403
                return response
        
        return decorated
    
    return decorator


def hmac_auth(api_key_field: str = 'X-API-Key', signature_field: str = 'X-Signature') -> Callable:
    """
    HMAC身份验证装饰器
    
    验证请求中的HMAC签名是否有效
    
    参数:
        api_key_field (str, optional): API密钥请求头字段名，默认为'X-API-Key'
        signature_field (str, optional): 签名请求头字段名，默认为'X-Signature'
        
    用法:
        @app.route('/api/secure')
        @hmac_auth()
        def secure_route():
            return "This is a secure route"
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 获取API密钥和签名
                api_key = request.headers.get(api_key_field)
                signature = request.headers.get(signature_field)
                
                # 如果未提供API密钥或签名，则返回401错误
                if not api_key or not signature:
                    response = jsonify(format_error_response(
                        message=f"缺少身份验证信息，需要 {api_key_field} 和 {signature_field} 请求头",
                        status_code=401
                    ))
                    response.status_code = 401
                    return response
                
                # 获取API密钥对应的密钥
                api_secret = current_app.config.get('API_SECRETS', {}).get(api_key)
                if not api_secret:
                    response = jsonify(format_error_response(
                        message="无效的API密钥",
                        status_code=401
                    ))
                    response.status_code = 401
                    return response
                
                # 生成签名
                body = request.get_data()
                expected_signature = hmac.new(
                    api_secret.encode('utf-8'),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                # 验证签名
                if not hmac.compare_digest(signature, expected_signature):
                    response = jsonify(format_error_response(
                        message="无效的签名",
                        status_code=401
                    ))
                    response.status_code = 401
                    return response
                
                # 设置已验证标志
                g.authenticated = True
                g.api_key = api_key
                
                # 如果签名有效，则继续执行被装饰的函数
                return f(*args, **kwargs)
            
            except Exception as e:
                # 记录错误
                current_app.logger.error(f"HMAC身份验证错误: {str(e)}")
                
                # 返回401错误
                response = jsonify(format_error_response(
                    message=f"身份验证失败: {str(e)}",
                    status_code=401
                ))
                response.status_code = 401
                return response
        
        return decorated
    
    return decorator


class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self, app=None):
        # API密钥字典，键为API密钥，值为(密钥, 过期时间)元组
        self.api_keys = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        app.api_key_manager = self
    
    def create_key(self, expires_in: int = 86400) -> Tuple[str, str]:
        """
        创建新的API密钥和密钥
        
        参数:
            expires_in (int, optional): 过期时间（秒），默认为86400（1天）
            
        返回:
            Tuple[str, str]: API密钥和密钥
        """
        # 生成随机密钥
        api_key = hashlib.sha256(os.urandom(32)).hexdigest()
        api_secret = hashlib.sha256(os.urandom(32)).hexdigest()
        
        # 设置过期时间
        expires_at = int(time.time()) + expires_in
        
        # 存储API密钥
        self.api_keys[api_key] = (api_secret, expires_at)
        
        return api_key, api_secret
    
    def validate_key(self, api_key: str) -> bool:
        """
        验证API密钥是否有效
        
        参数:
            api_key (str): API密钥
            
        返回:
            bool: 如果API密钥有效，则返回True，否则返回False
        """
        # 检查API密钥是否存在
        if api_key not in self.api_keys:
            return False
        
        # 检查API密钥是否过期
        _, expires_at = self.api_keys[api_key]
        if int(time.time()) > expires_at:
            # 删除过期的API密钥
            del self.api_keys[api_key]
            return False
        
        return True
    
    def get_secret(self, api_key: str) -> Optional[str]:
        """
        获取API密钥对应的密钥
        
        参数:
            api_key (str): API密钥
            
        返回:
            Optional[str]: 如果API密钥有效，则返回对应的密钥，否则返回None
        """
        # 检查API密钥是否有效
        if not self.validate_key(api_key):
            return None
        
        # 返回API密钥对应的密钥
        api_secret, _ = self.api_keys[api_key]
        return api_secret
    
    def revoke_key(self, api_key: str) -> bool:
        """
        撤销API密钥
        
        参数:
            api_key (str): API密钥
            
        返回:
            bool: 如果API密钥已成功撤销，则返回True，否则返回False
        """
        # 检查API密钥是否存在
        if api_key not in self.api_keys:
            return False
        
        # 删除API密钥
        del self.api_keys[api_key]
        return True


def configure_auth(app):
    """配置认证中间件"""
    # 设置角色权限
    app.role_permissions = DEFAULT_ROLE_PERMISSIONS
    
    # 初始化API密钥管理器
    api_key_manager = APIKeyManager(app) 