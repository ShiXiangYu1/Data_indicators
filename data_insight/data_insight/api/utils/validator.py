"""
API请求验证工具
============

提供API请求参数验证功能。
"""

from typing import Dict, Any, List, Optional, Callable, Union, Type
from functools import wraps
from flask import request, jsonify, abort, current_app

from .response_formatter import format_validation_error


class ValidationError(Exception):
    """
    验证错误异常
    
    用于表示请求参数验证失败。
    """
    
    def __init__(self, errors: Dict[str, List[str]]):
        """
        初始化验证错误异常
        
        参数:
            errors (Dict[str, List[str]]): 字段错误字典，键为字段名，值为错误消息列表
        """
        self.errors = errors
        message = "; ".join([f"{field}: {', '.join(msgs)}" for field, msgs in errors.items()])
        super().__init__(message)


class Validator:
    """
    请求验证器
    
    提供请求参数验证功能。
    """
    
    @staticmethod
    def validate_request(schema: Dict[str, Dict[str, Any]]):
        """
        验证请求参数装饰器
        
        参数:
            schema (Dict[str, Dict[str, Any]]): 验证模式，格式为：
                {
                    "字段名": {
                        "type": 类型,
                        "required": 是否必需,
                        "enum": 枚举值列表,
                        "min": 最小值,
                        "max": 最大值,
                        "minlength": 最小长度,
                        "maxlength": 最大长度,
                        "pattern": 正则表达式,
                        "custom": 自定义验证函数
                    }
                }
                
        返回:
            callable: 包装后的函数
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # 获取请求数据
                if request.is_json:
                    data = request.json
                else:
                    data = request.form.to_dict()
                
                # 验证请求数据
                try:
                    Validator.validate_data(data, schema)
                except ValidationError as e:
                    # 返回验证错误响应
                    return jsonify(format_validation_error(e.errors)), 422
                
                # 调用原函数
                return f(*args, **kwargs)
                
            return wrapper
        
        return decorator
    
    @staticmethod
    def validate_data(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证数据
        
        参数:
            data (Dict[str, Any]): 要验证的数据
            schema (Dict[str, Dict[str, Any]]): 验证模式
            
        返回:
            Dict[str, Any]: 验证后的数据
            
        异常:
            ValidationError: 当验证失败时
        """
        errors = {}
        validated = {}
        
        # 检查所有必需字段
        for field, field_schema in schema.items():
            is_required = field_schema.get("required", False)
            
            # 检查字段是否存在
            if field in data:
                # 执行字段验证
                try:
                    value = data[field]
                    validated_value = Validator._validate_field(field, value, field_schema)
                    validated[field] = validated_value
                except ValueError as e:
                    errors.setdefault(field, []).append(str(e))
            elif is_required:
                errors.setdefault(field, []).append(f"字段'{field}'为必填项")
        
        # 如果有错误，抛出异常
        if errors:
            raise ValidationError(errors)
        
        return validated
    
    @staticmethod
    def _validate_field(field: str, value: Any, field_schema: Dict[str, Any]) -> Any:
        """
        验证单个字段
        
        参数:
            field (str): 字段名
            value (Any): 字段值
            field_schema (Dict[str, Any]): 字段验证模式
            
        返回:
            Any: 验证后的值
            
        异常:
            ValueError: 当验证失败时
        """
        # 检查类型
        expected_type = field_schema.get("type")
        if expected_type:
            # 处理特殊类型
            if expected_type == "array":
                if not isinstance(value, list):
                    raise ValueError(f"应该是数组类型")
            elif expected_type == "object":
                if not isinstance(value, dict):
                    raise ValueError(f"应该是对象类型")
            # 处理基本类型
            elif expected_type == "string" and not isinstance(value, str):
                raise ValueError(f"应该是字符串类型")
            elif expected_type == "number":
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"应该是数字类型")
            elif expected_type == "integer":
                if not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"应该是整数类型")
            elif expected_type == "boolean":
                if isinstance(value, bool):
                    pass
                elif isinstance(value, str):
                    if value.lower() in ("true", "1", "yes"):
                        value = True
                    elif value.lower() in ("false", "0", "no"):
                        value = False
                    else:
                        raise ValueError(f"应该是布尔类型")
                elif isinstance(value, (int, float)):
                    value = bool(value)
                else:
                    raise ValueError(f"应该是布尔类型")
        
        # 检查枚举值
        enum_values = field_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            enum_str = ", ".join([str(v) for v in enum_values])
            raise ValueError(f"值应该是以下之一: {enum_str}")
        
        # 检查数字范围
        if isinstance(value, (int, float)):
            min_value = field_schema.get("min")
            if min_value is not None and value < min_value:
                raise ValueError(f"不能小于{min_value}")
            
            max_value = field_schema.get("max")
            if max_value is not None and value > max_value:
                raise ValueError(f"不能大于{max_value}")
        
        # 检查字符串长度
        if isinstance(value, str):
            min_length = field_schema.get("minlength")
            if min_length is not None and len(value) < min_length:
                raise ValueError(f"长度不能小于{min_length}")
            
            max_length = field_schema.get("maxlength")
            if max_length is not None and len(value) > max_length:
                raise ValueError(f"长度不能大于{max_length}")
            
            # 检查正则表达式
            import re
            pattern = field_schema.get("pattern")
            if pattern is not None and not re.match(pattern, value):
                raise ValueError(f"格式不正确")
        
        # 检查数组长度
        if isinstance(value, list):
            min_length = field_schema.get("minlength")
            if min_length is not None and len(value) < min_length:
                raise ValueError(f"长度不能小于{min_length}")
            
            max_length = field_schema.get("maxlength")
            if max_length is not None and len(value) > max_length:
                raise ValueError(f"长度不能大于{max_length}")
            
            # 验证数组元素
            items_schema = field_schema.get("items")
            if items_schema:
                for i, item in enumerate(value):
                    try:
                        Validator._validate_field(f"{field}[{i}]", item, items_schema)
                    except ValueError as e:
                        raise ValueError(f"索引{i}的元素无效: {str(e)}")
        
        # 验证嵌套对象
        if isinstance(value, dict):
            properties = field_schema.get("properties")
            if properties:
                try:
                    Validator.validate_data(value, properties)
                except ValidationError as e:
                    raise ValueError(f"子字段验证失败: {str(e)}")
        
        # 自定义验证
        custom_validator = field_schema.get("custom")
        if custom_validator and callable(custom_validator):
            try:
                value = custom_validator(value)
            except Exception as e:
                raise ValueError(str(e))
        
        return value


# 常用验证模式
COMMON_SCHEMAS = {
    "id": {
        "type": "string",
        "required": True,
        "minlength": 1,
        "maxlength": 100
    },
    "page": {
        "type": "integer",
        "required": False,
        "min": 1,
        "default": 1
    },
    "limit": {
        "type": "integer",
        "required": False,
        "min": 1,
        "max": 100,
        "default": 20
    },
    "sort": {
        "type": "string",
        "required": False,
        "pattern": r"^[a-zA-Z0-9_\-\.]+$"
    },
    "order": {
        "type": "string",
        "required": False,
        "enum": ["asc", "desc"],
        "default": "asc"
    },
    "query": {
        "type": "string",
        "required": False,
        "maxlength": 100
    }
}


def validate_json_request(f):
    """
    验证JSON请求装饰器
    
    确保请求内容类型为JSON。
    
    参数:
        f (callable): 被装饰的函数
        
    返回:
        callable: 包装后的函数
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "请求必须是JSON格式",
                "error_code": "INVALID_CONTENT_TYPE",
                "status_code": 415
            }), 415
        return f(*args, **kwargs)
    return wrapper 