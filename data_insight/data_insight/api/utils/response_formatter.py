#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API响应格式化工具
=============

提供统一的API响应格式化功能。
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def format_success_response(
    data: Any = None,
    message: str = "操作成功",
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化成功响应
    
    参数:
        data (Any, optional): 响应数据，默认为None
        message (str, optional): 响应消息，默认为"操作成功"
        status_code (int, optional): 状态码，默认为200
        metadata (Optional[Dict[str, Any]], optional): 元数据，默认为None
        
    返回:
        Dict[str, Any]: 格式化后的响应数据
    """
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加元数据
    if metadata:
        response["metadata"] = metadata
    
    return response


def format_error_response(
    message: str = "操作失败",
    status_code: int = 400,
    error_type: Optional[str] = None,
    error_detail: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    格式化错误响应
    
    参数:
        message (str, optional): 错误消息，默认为"操作失败"
        status_code (int, optional): 状态码，默认为400
        error_type (Optional[str], optional): 错误类型，默认为None
        error_detail (Optional[Dict[str, Any]], optional): 错误详情，默认为None
        request_id (Optional[str], optional): 请求ID，默认为None
        
    返回:
        Dict[str, Any]: 格式化后的响应数据
    """
    response = {
        "success": False,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加错误类型
    if error_type:
        response["error_type"] = error_type
    
    # 添加错误详情
    if error_detail:
        response["error_detail"] = error_detail
    
    # 添加请求ID
    if request_id:
        response["request_id"] = request_id
    
    return response


def format_paginated_response(
    data: List[Any],
    page: int = 1,
    page_size: int = 10,
    total: int = 0,
    message: str = "查询成功",
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化分页响应
    
    参数:
        data (List[Any]): 当前页数据
        page (int, optional): 当前页码，默认为1
        page_size (int, optional): 每页大小，默认为10
        total (int, optional): 总记录数，默认为0
        message (str, optional): 响应消息，默认为"查询成功"
        status_code (int, optional): 状态码，默认为200
        metadata (Optional[Dict[str, Any]], optional): 元数据，默认为None
        
    返回:
        Dict[str, Any]: 格式化后的响应数据
    """
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    # 构建分页信息
    pagination = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    # 构建响应
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "data": data,
        "pagination": pagination,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加元数据
    if metadata:
        response["metadata"] = metadata
    
    return response


def format_batch_response(
    results: List[Dict[str, Any]],
    failed_count: int = 0,
    success_count: int = 0,
    message: str = "批处理完成",
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化批处理响应
    
    参数:
        results (List[Dict[str, Any]]): 批处理结果列表
        failed_count (int, optional): 失败计数，默认为0
        success_count (int, optional): 成功计数，默认为0
        message (str, optional): 响应消息，默认为"批处理完成"
        status_code (int, optional): 状态码，默认为200
        metadata (Optional[Dict[str, Any]], optional): 元数据，默认为None
        
    返回:
        Dict[str, Any]: 格式化后的响应数据
    """
    # 构建批处理信息
    batch_info = {
        "total_count": len(results),
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": f"{(success_count / len(results) * 100) if results else 0:.2f}%"
    }
    
    # 构建响应
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "batch_info": batch_info,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加元数据
    if metadata:
        response["metadata"] = metadata
    
    return response


def format_export_response(
    file_url: str,
    file_name: str,
    file_size: int,
    file_type: str,
    expires_at: Optional[str] = None,
    message: str = "导出成功",
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化导出响应
    
    参数:
        file_url (str): 文件URL
        file_name (str): 文件名称
        file_size (int): 文件大小（字节）
        file_type (str): 文件类型
        expires_at (Optional[str], optional): 过期时间，默认为None
        message (str, optional): 响应消息，默认为"导出成功"
        status_code (int, optional): 状态码，默认为200
        metadata (Optional[Dict[str, Any]], optional): 元数据，默认为None
        
    返回:
        Dict[str, Any]: 格式化后的响应数据
    """
    # 构建文件信息
    file_info = {
        "file_url": file_url,
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "created_at": datetime.now().isoformat()
    }
    
    # 添加过期时间
    if expires_at:
        file_info["expires_at"] = expires_at
    
    # 构建响应
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "file_info": file_info,
        "timestamp": datetime.now().isoformat()
    }
    
    # 添加元数据
    if metadata:
        response["metadata"] = metadata
    
    return response 