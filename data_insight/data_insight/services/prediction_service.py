"""
预测服务
======

提供数据预测相关的服务功能，作为API和核心预测模块之间的桥梁。
"""

import logging
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache

from ..core.prediction.time_series import TimeSeriesPredictor
from ..core.generation.text import TextGenerator
from ..config import settings


class PredictionService:
    """
    预测服务
    
    封装数据预测相关功能，提供高级服务接口。
    """
    
    def __init__(self):
        """初始化预测服务"""
        self.logger = logging.getLogger("data_insight.services.prediction")
        self.time_series_predictor = TimeSeriesPredictor()
        self.text_generator = TextGenerator()
        
        # 设置缓存
        self.cache_enabled = True
        self.cache_size = 100
    
    @lru_cache(maxsize=100)
    def predict_time_series(self, data: Dict[str, Any], horizon: int = 7, 
                           confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        预测时间序列未来值
        
        参数:
            data (Dict[str, Any]): 时间序列数据
            horizon (int, optional): 预测步长，默认为7
            confidence_level (float, optional): 置信水平，默认为0.95
            
        返回:
            Dict[str, Any]: 预测结果，包括预测值和置信区间
        """
        try:
            self.logger.info(f"开始预测时间序列, 步长: {horizon}")
            
            # 准备预测数据
            prediction_data = {
                "time_series": data,
                "horizon": horizon,
                "confidence_level": confidence_level
            }
            
            # 预测时间序列
            prediction_result = self.time_series_predictor.predict(prediction_data)
            
            # 生成预测解读文本
            insight_text = self.text_generator.generate(prediction_result)
            
            # 构建结果
            result = {
                "prediction": prediction_result,
                "insight": insight_text
            }
            
            self.logger.info(f"时间序列预测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"时间序列预测异常: {str(e)}", exc_info=True)
            raise
    
    @lru_cache(maxsize=50)
    def predict_with_scenario(self, data: Dict[str, Any], scenario: Dict[str, Any], 
                             horizon: int = 7) -> Dict[str, Any]:
        """
        基于情景的预测
        
        参数:
            data (Dict[str, Any]): 时间序列数据
            scenario (Dict[str, Any]): 情景参数
            horizon (int, optional): 预测步长，默认为7
            
        返回:
            Dict[str, Any]: 预测结果，包括预测值和情景影响
        """
        try:
            self.logger.info(f"开始情景预测, 情景: {scenario.get('name', '未命名情景')}")
            
            # 准备预测数据
            prediction_data = {
                "time_series": data,
                "scenario": scenario,
                "horizon": horizon
            }
            
            # 情景预测
            prediction_result = self.time_series_predictor.predict_with_scenario(prediction_data)
            
            # 生成预测解读文本
            insight_text = self.text_generator.generate(prediction_result)
            
            # 构建结果
            result = {
                "prediction": prediction_result,
                "insight": insight_text,
                "scenario": scenario
            }
            
            self.logger.info(f"情景预测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"情景预测异常: {str(e)}", exc_info=True)
            raise
    
    def get_supported_models(self) -> List[str]:
        """
        获取支持的预测模型
        
        返回:
            List[str]: 支持的预测模型列表
        """
        return [
            "arima",
            "prophet",
            "lstm",
            "gru",
            "transformer"
        ]
    
    def validate_prediction_data(self, data: Dict[str, Any]) -> bool:
        """
        验证预测数据格式
        
        参数:
            data (Dict[str, Any]): 预测数据
            
        返回:
            bool: 数据格式是否有效
            
        异常:
            ValueError: 如果数据格式无效
        """
        # 基本字段验证
        required_fields = ["values", "timestamps"]
        
        if not isinstance(data, dict):
            raise ValueError("预测数据必须是字典类型")
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 检查值和时间戳
        values = data["values"]
        timestamps = data["timestamps"]
        
        if not isinstance(values, list):
            raise ValueError("values字段必须是列表类型")
            
        if not isinstance(timestamps, list):
            raise ValueError("timestamps字段必须是列表类型")
            
        if len(values) != len(timestamps):
            raise ValueError("values和timestamps列表长度必须相同")
            
        if len(values) < 10:
            self.logger.warning("数据点数量较少，可能影响预测准确性")
        
        return True 