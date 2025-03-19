#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
请求验证工具
==========

提供用于验证API请求参数的工具函数。
"""

from typing import Dict, Any, List, Union, Optional
from werkzeug.exceptions import BadRequest
import json


def validate_request_data(data: Dict[str, Any], required_fields: List[str], field_types: Optional[Dict[str, type]] = None) -> None:
    """
    验证请求数据中是否包含所有必要字段，并验证字段类型
    
    参数:
        data (Dict[str, Any]): 请求数据
        required_fields (List[str]): 必要字段列表
        field_types (Dict[str, type], optional): 字段类型字典，键为字段名，值为类型
        
    异常:
        BadRequest: 当缺少必要字段或字段类型不正确时
    """
    # 验证必要字段
    for field in required_fields:
        if field not in data:
            raise BadRequest(f"缺少必要字段: {field}")
    
    # 验证字段类型
    if field_types:
        for field, field_type in field_types.items():
            if field in data and not isinstance(data[field], field_type):
                actual_type = type(data[field]).__name__
                expected_type = field_type.__name__
                raise BadRequest(f"字段 '{field}' 类型错误: 期望 {expected_type}，实际为 {actual_type}")


def validate_numeric_range(data: Dict[str, Any], field: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> None:
    """
    验证数值字段是否在指定范围内
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 数值字段名
        min_value (float, optional): 最小值
        max_value (float, optional): 最大值
        
    异常:
        BadRequest: 当字段值不在指定范围内时
    """
    if field not in data:
        return
    
    value = data[field]
    if not isinstance(value, (int, float)):
        raise BadRequest(f"字段 '{field}' 必须是数值类型")
    
    if min_value is not None and value < min_value:
        raise BadRequest(f"字段 '{field}' 值不能小于 {min_value}")
    
    if max_value is not None and value > max_value:
        raise BadRequest(f"字段 '{field}' 值不能大于 {max_value}")


def validate_string_length(data: Dict[str, Any], field: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> None:
    """
    验证字符串字段长度是否在指定范围内
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 字符串字段名
        min_length (int, optional): 最小长度
        max_length (int, optional): 最大长度
        
    异常:
        BadRequest: 当字段长度不在指定范围内时
    """
    if field not in data:
        return
    
    value = data[field]
    if not isinstance(value, str):
        raise BadRequest(f"字段 '{field}' 必须是字符串类型")
    
    if min_length is not None and len(value) < min_length:
        raise BadRequest(f"字段 '{field}' 长度不能小于 {min_length}")
    
    if max_length is not None and len(value) > max_length:
        raise BadRequest(f"字段 '{field}' 长度不能大于 {max_length}")


def validate_list_length(data: Dict[str, Any], field: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> None:
    """
    验证列表字段长度是否在指定范围内
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 列表字段名
        min_length (int, optional): 最小长度
        max_length (int, optional): 最大长度
        
    异常:
        BadRequest: 当字段长度不在指定范围内时
    """
    if field not in data:
        return
    
    value = data[field]
    if not isinstance(value, list):
        raise BadRequest(f"字段 '{field}' 必须是列表类型")
    
    if min_length is not None and len(value) < min_length:
        raise BadRequest(f"字段 '{field}' 长度不能小于 {min_length}")
    
    if max_length is not None and len(value) > max_length:
        raise BadRequest(f"字段 '{field}' 长度不能大于 {max_length}")


def validate_enum_value(data: Dict[str, Any], field: str, allowed_values: List[Any]) -> None:
    """
    验证字段值是否在允许的值列表中
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 字段名
        allowed_values (List[Any]): 允许的值列表
        
    异常:
        BadRequest: 当字段值不在允许的值列表中时
    """
    if field not in data:
        return
    
    value = data[field]
    if value not in allowed_values:
        allowed_str = ", ".join([str(v) for v in allowed_values])
        raise BadRequest(f"字段 '{field}' 的值必须是以下之一: {allowed_str}")


def validate_json_format(data: str) -> Dict[str, Any]:
    """
    验证JSON格式是否正确
    
    参数:
        data (str): JSON字符串
        
    返回:
        Dict[str, Any]: 解析后的JSON对象
        
    异常:
        BadRequest: 当JSON格式不正确时
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise BadRequest(f"无效的JSON格式: {str(e)}")


def validate_date_format(data: Dict[str, Any], field: str, format_hint: str = "YYYY-MM-DD") -> None:
    """
    验证日期字段格式是否正确
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 日期字段名
        format_hint (str, optional): 日期格式提示
        
    异常:
        BadRequest: 当日期格式不正确时
    """
    if field not in data:
        return
    
    from datetime import datetime
    
    value = data[field]
    if not isinstance(value, str):
        raise BadRequest(f"字段 '{field}' 必须是字符串类型")
    
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise BadRequest(f"字段 '{field}' 的日期格式不正确，应为 {format_hint}")


def validate_email_format(data: Dict[str, Any], field: str) -> None:
    """
    验证邮箱字段格式是否正确
    
    参数:
        data (Dict[str, Any]): 请求数据
        field (str): 邮箱字段名
        
    异常:
        BadRequest: 当邮箱格式不正确时
    """
    if field not in data:
        return
    
    import re
    
    value = data[field]
    if not isinstance(value, str):
        raise BadRequest(f"字段 '{field}' 必须是字符串类型")
    
    # 简单的邮箱格式验证
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, value):
        raise BadRequest(f"字段 '{field}' 的邮箱格式不正确")


def validate_request_size(data: Dict[str, Any], max_size_mb: float = 10.0) -> None:
    """
    验证请求数据大小是否超过限制
    
    参数:
        data (Dict[str, Any]): 请求数据
        max_size_mb (float, optional): 最大允许大小（MB）
        
    异常:
        BadRequest: 当请求数据大小超过限制时
    """
    import sys
    
    # 计算数据大小（MB）
    data_size = sys.getsizeof(json.dumps(data)) / (1024 * 1024)
    
    if data_size > max_size_mb:
        raise BadRequest(f"请求数据大小（{data_size:.2f}MB）超过限制（{max_size_mb}MB）") 