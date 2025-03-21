"""
预测器接口定义
===========

定义所有预测器组件必须实现的接口，确保组件之间的一致性和可替换性。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


class PredictorInterface(ABC):
    """
    预测器接口
    
    所有数据预测器必须实现的基础接口，定义预测器的基本行为。
    """
    
    @abstractmethod
    def predict(self, data: Dict[str, Any], horizon: int = 1, 
                confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        基于历史数据进行预测
        
        参数:
            data (Dict[str, Any]): 历史数据
            horizon (int, optional): 预测步长，默认为1
            confidence_level (float, optional): 置信水平，默认为0.95
            
        返回:
            Dict[str, Any]: 预测结果，包括预测值、置信区间等
            
        异常:
            ValueError: 如果输入数据不足或格式不正确
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
    def get_supported_models(self) -> List[str]:
        """
        获取预测器支持的模型列表
        
        返回:
            List[str]: 支持的模型名称列表
        """
        pass
    
    @abstractmethod
    def set_model(self, model_name: str, model_params: Optional[Dict[str, Any]] = None) -> bool:
        """
        设置预测模型
        
        参数:
            model_name (str): 模型名称
            model_params (Dict[str, Any], optional): 模型参数
            
        返回:
            bool: 是否成功设置模型
            
        异常:
            ValueError: 如果模型名称不受支持
        """
        pass
    
    @abstractmethod
    def evaluate(self, test_data: Dict[str, Any], metrics: List[str]) -> Dict[str, float]:
        """
        评估预测模型性能
        
        参数:
            test_data (Dict[str, Any]): 测试数据
            metrics (List[str]): 评估指标列表
            
        返回:
            Dict[str, float]: 各评估指标的值
            
        异常:
            ValueError: 如果评估指标不受支持
        """
        pass
    
    @abstractmethod
    def detect_anomalies(self, data: Dict[str, Any], 
                          threshold: float = 0.05) -> Dict[str, Any]:
        """
        检测数据中的异常点
        
        参数:
            data (Dict[str, Any]): 数据
            threshold (float, optional): 异常阈值，默认为0.05
            
        返回:
            Dict[str, Any]: 异常检测结果
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取预测器的元数据信息
        
        返回:
            Dict[str, Any]: 元数据信息，包括名称、版本、支持的模型等
        """
        pass 