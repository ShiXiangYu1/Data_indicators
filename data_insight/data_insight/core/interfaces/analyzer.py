"""
分析器接口定义
===========

定义所有分析器组件必须实现的接口，确保组件之间的一致性和可替换性。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class AnalyzerInterface(ABC):
    """
    分析器接口
    
    所有数据分析器必须实现的基础接口，定义分析器的基本行为。
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取分析器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、描述等
        """
        pass
    
    @abstractmethod
    def supports_async(self) -> bool:
        """
        检查分析器是否支持异步处理
        
        返回:
            bool: 是否支持异步处理
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass 