"""
推荐器接口定义
===========

定义所有推荐器和建议生成器组件必须实现的接口，确保组件之间的一致性和可替换性。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class RecommenderInterface(ABC):
    """
    推荐器接口
    
    所有推荐器和建议生成器必须实现的基础接口，定义推荐器的基本行为。
    """
    
    @abstractmethod
    def recommend(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None,
                  limit: int = 5) -> Dict[str, Any]:
        """
        基于数据和上下文生成推荐或建议
        
        参数:
            data (Dict[str, Any]): 数据
            context (Dict[str, Any], optional): 上下文信息
            limit (int, optional): 返回建议的最大数量，默认为5
            
        返回:
            Dict[str, Any]: 推荐结果，包括建议列表、置信度等
            
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
    def get_recommendation_types(self) -> List[str]:
        """
        获取推荐器支持的建议类型列表
        
        返回:
            List[str]: 支持的建议类型列表
        """
        pass
    
    @abstractmethod
    def set_recommendation_type(self, recommendation_type: str) -> bool:
        """
        设置推荐类型
        
        参数:
            recommendation_type (str): 推荐类型
            
        返回:
            bool: 是否成功设置推荐类型
            
        异常:
            ValueError: 如果推荐类型不受支持
        """
        pass
    
    @abstractmethod
    def prioritize(self, recommendations: List[Dict[str, Any]], 
                   priority_factors: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        对推荐结果进行优先级排序
        
        参数:
            recommendations (List[Dict[str, Any]]): 推荐结果列表
            priority_factors (Dict[str, float], optional): 优先级因子权重
            
        返回:
            List[Dict[str, Any]]: 排序后的推荐结果列表
        """
        pass
    
    @abstractmethod
    def evaluate_recommendation(self, recommendation: Dict[str, Any], 
                                feedback: Dict[str, Any]) -> Dict[str, float]:
        """
        评估推荐效果
        
        参数:
            recommendation (Dict[str, Any]): 推荐结果
            feedback (Dict[str, Any]): 反馈信息
            
        返回:
            Dict[str, float]: 评估指标
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取推荐器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、支持的推荐类型等
        """
        pass 