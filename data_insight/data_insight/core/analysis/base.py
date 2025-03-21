"""
基础分析器
========

实现AnalyzerInterface接口，为所有具体分析器提供基础功能。
"""

import uuid
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

from data_insight.core.interfaces.analyzer import AnalyzerInterface


class BaseAnalyzer(AnalyzerInterface, ABC):
    """
    基础分析器
    
    为所有具体分析器提供通用功能的基类，实现AnalyzerInterface接口的通用方法。
    """
    
    def __init__(self, name: str = None, version: str = "1.0.0"):
        """
        初始化基础分析器
        
        参数:
            name (str, optional): 分析器名称，默认为类名
            version (str, optional): 分析器版本，默认为"1.0.0"
        """
        self.name = name or self.__class__.__name__
        self.version = version
        self.logger = logging.getLogger(f"data_insight.analyzers.{self.name}")
        self._async_tasks = {}  # 存储异步任务
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并返回分析结果
        
        参数:
            data (Dict[str, Any]): 需要分析的数据
            
        返回:
            Dict[str, Any]: 分析结果
            
        异常:
            ValueError: 如果输入数据格式不正确
            TypeError: 如果输入数据类型不支持
        """
        # 这是一个抽象方法，具体由子类实现
        pass
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证输入数据是否包含所有必需字段
        
        参数:
            data (Dict[str, Any]): 需要验证的数据
            required_fields (List[str]): 必需字段列表
            
        返回:
            bool: 验证是否通过
            
        异常:
            ValueError: 如果缺少必需字段
        """
        if not isinstance(data, dict):
            raise TypeError(f"输入数据必须是字典类型，但收到了 {type(data)}")
            
        # 检查所有必需字段
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
            
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取分析器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、描述等
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__doc__.strip() if self.__doc__ else "",
            "supports_async": self.supports_async()
        }
    
    def supports_async(self) -> bool:
        """
        检查分析器是否支持异步处理
        
        返回:
            bool: 是否支持异步处理
        """
        # 默认实现返回False，子类可以重写此方法
        return False
    
    def async_analyze(self, data: Dict[str, Any]) -> str:
        """
        异步分析数据，返回任务ID
        
        参数:
            data (Dict[str, Any]): 需要分析的数据
            
        返回:
            str: 任务ID，可用于后续查询结果
            
        异常:
            NotImplementedError: 如果分析器不支持异步处理
        """
        if not self.supports_async():
            raise NotImplementedError(f"分析器 {self.name} 不支持异步处理")
            
        # 创建任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        self._async_tasks[task_id] = {
            "status": "pending",
            "data": data,
            "result": None,
            "error": None
        }
        
        # 这里应该启动异步任务，但具体实现由子类提供
        # 子类应该更新 self._async_tasks[task_id] 的状态
        
        return task_id
    
    def get_async_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取异步分析任务的结果
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Dict[str, Any]: 任务结果，包括状态和分析结果
            
        异常:
            ValueError: 如果任务ID无效
            NotImplementedError: 如果分析器不支持异步处理
        """
        if not self.supports_async():
            raise NotImplementedError(f"分析器 {self.name} 不支持异步处理")
            
        if task_id not in self._async_tasks:
            raise ValueError(f"无效的任务ID: {task_id}")
            
        task = self._async_tasks[task_id]
        
        # 构建响应
        response = {
            "task_id": task_id,
            "status": task["status"]
        }
        
        if task["status"] == "completed":
            response["result"] = task["result"]
        elif task["status"] == "failed":
            response["error"] = task["error"]
            
        return response
    
    def cancel_async_task(self, task_id: str) -> bool:
        """
        取消异步分析任务
        
        参数:
            task_id (str): 任务ID
            
        返回:
            bool: 是否成功取消
            
        异常:
            ValueError: 如果任务ID无效
            NotImplementedError: 如果分析器不支持异步处理
        """
        if not self.supports_async():
            raise NotImplementedError(f"分析器 {self.name} 不支持异步处理")
            
        if task_id not in self._async_tasks:
            raise ValueError(f"无效的任务ID: {task_id}")
            
        task = self._async_tasks[task_id]
        
        # 如果任务已完成或已失败，无法取消
        if task["status"] in ["completed", "failed"]:
            return False
            
        # 更新任务状态
        task["status"] = "cancelled"
        
        # 这里应该实际取消任务，但具体实现由子类提供
        
        return True
    
    def _format_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化分析结果，添加元数据信息
        
        参数:
            data (Dict[str, Any]): 原始分析结果
            
        返回:
            Dict[str, Any]: 格式化后的分析结果
        """
        return {
            "metadata": {
                "analyzer": self.name,
                "version": self.version,
                "timestamp": self._get_timestamp()
            },
            "data": data
        }
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳
        
        返回:
            str: ISO 8601格式的时间戳
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() 