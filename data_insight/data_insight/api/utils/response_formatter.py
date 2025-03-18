"""
API响应格式化工具
==============

提供统一的API响应格式化功能。
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json


def format_success_response(
    data: Any, 
    message: str = "操作成功", 
    status_code: int = 200
) -> Dict[str, Any]:
    """
    格式化成功响应
    
    参数:
        data (Any): 响应数据
        message (str, optional): 响应消息，默认为"操作成功"
        status_code (int, optional): HTTP状态码，默认为200
        
    返回:
        Dict[str, Any]: 格式化的响应
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }


def format_error_response(
    message: str, 
    error_code: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    格式化错误响应
    
    参数:
        message (str): 错误消息
        error_code (str, optional): 错误代码
        errors (List[Dict[str, Any]], optional): 详细错误列表
        status_code (int, optional): HTTP状态码，默认为400
        
    返回:
        Dict[str, Any]: 格式化的响应
    """
    response = {
        "success": False,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if errors:
        response["errors"] = errors
    
    return response


def format_validation_error(errors: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    格式化字段验证错误响应
    
    参数:
        errors (Dict[str, List[str]]): 字段错误字典，键为字段名，值为错误消息列表
        
    返回:
        Dict[str, Any]: 格式化的响应
    """
    error_list = []
    for field, messages in errors.items():
        for message in messages:
            error_list.append({
                "field": field,
                "message": message
            })
    
    return format_error_response(
        message="请求参数验证失败",
        error_code="VALIDATION_ERROR",
        errors=error_list,
        status_code=422
    )


def format_task_pending_response(task_id: str) -> Dict[str, Any]:
    """
    格式化任务等待响应
    
    参数:
        task_id (str): 任务ID
        
    返回:
        Dict[str, Any]: 格式化的响应
    """
    return format_success_response(
        data={
            "task_id": task_id,
            "status": "pending",
            "message": "任务已接受并正在处理中"
        },
        message="任务已接受",
        status_code=202  # Accepted
    )


def format_task_result_response(
    result: Any, 
    task_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    格式化任务结果响应
    
    参数:
        result (Any): 任务结果
        task_info (Dict[str, Any]): 任务信息
        
    返回:
        Dict[str, Any]: 格式化的响应
    """
    return format_success_response(
        data={
            "task_id": task_info["task_id"],
            "status": task_info["status"],
            "start_time": task_info["start_time"],
            "end_time": task_info["end_time"],
            "duration": task_info["duration"],
            "result": result
        },
        message="任务已完成",
        status_code=200
    )


class ApiJSONEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，支持更多类型的序列化
    """
    
    def default(self, obj):
        """
        重写default方法以支持更多类型
        
        参数:
            obj: 要序列化的对象
            
        返回:
            序列化后的对象
        """
        # 处理datetime对象
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # 处理bytes对象
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        
        # 处理集合对象
        if isinstance(obj, set):
            return list(obj)
        
        # 调用父类方法处理其他类型
        return super().default(obj) 