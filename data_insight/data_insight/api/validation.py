"""
API验证模块
==========

提供API请求验证的装饰器和辅助函数。
"""

import functools
from flask import request, jsonify

def validate_request_json(required_fields=None):
    """验证请求JSON数据的装饰器
    
    确保请求包含JSON数据，并且包含所有必需的字段
    
    Args:
        required_fields (list): 必需字段列表
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查Content-Type
            if not request.is_json:
                return jsonify({
                    'error': '请求必须包含JSON数据（Content-Type: application/json）'
                }), 400
            
            # 检查请求体是否为空
            if not request.data:
                return jsonify({
                    'error': '请求体不能为空'
                }), 400
            
            # 获取JSON数据
            data = request.json
            
            # 检查必需字段
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'缺少必需字段: {", ".join(missing_fields)}'
                    }), 400
            
            # 调用原始函数
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_query_params(required_params=None):
    """验证请求查询参数的装饰器
    
    确保请求包含所有必需的查询参数
    
    Args:
        required_params (list): 必需查询参数列表
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取查询参数
            params = request.args
            
            # 检查必需参数
            if required_params:
                missing_params = [param for param in required_params if param not in params]
                if missing_params:
                    return jsonify({
                        'error': f'缺少必需的查询参数: {", ".join(missing_params)}'
                    }), 400
            
            # 调用原始函数
            return func(*args, **kwargs)
        return wrapper
    return decorator 