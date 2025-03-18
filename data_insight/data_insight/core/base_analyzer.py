"""
基础分析器
========

定义基础分析器抽象类，为各种具体分析器提供通用接口和功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAnalyzer(ABC):
    """
    基础分析器抽象类
    
    定义数据分析器的基本接口和通用功能，所有具体分析器都应继承此类。
    """
    
    def __init__(self):
        """
        初始化基础分析器
        """
        pass
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并生成洞察结果
        
        参数:
            data (Dict[str, Any]): 输入数据
            
        返回:
            Dict[str, Any]: 分析结果，包含洞察信息
        """
        pass
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证输入数据是否包含所需字段
        
        参数:
            data (Dict[str, Any]): 待验证的输入数据
            required_fields (List[str]): 必需的字段列表
            
        返回:
            bool: 数据是否有效
            
        异常:
            ValueError: 如果缺少必需字段，抛出异常
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
        return True
    
    def merge_results(self, *results: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并多个分析结果
        
        参数:
            *results (Dict[str, Any]): 多个分析结果字典
            
        返回:
            Dict[str, Any]: 合并后的结果
        """
        merged = {}
        for result in results:
            for key, value in result.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # 递归合并嵌套字典
                    merged[key] = self.merge_results(merged[key], value)
                else:
                    # 直接更新或添加键值对
                    merged[key] = value
        return merged 