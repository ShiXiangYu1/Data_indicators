"""
预测分析器
========

实现数据预测功能，包括时间序列预测、模型评估和预测结果分析。
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .base_analyzer import BaseAnalyzer


class PredictionAnalyzer(BaseAnalyzer):
    """
    预测分析器类
    
    用于数据预测和模型评估，包括：
    1. 时间序列预测
    2. 模型评估
    3. 预测结果分析
    """
    
    def __init__(self):
        """
        初始化预测分析器
        """
        super().__init__()
        self.min_data_points = 20  # 最小数据点数
        self.forecast_horizon = 7  # 预测步数
        self.confidence_level = 0.95  # 置信水平
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并生成预测
        
        参数:
            data (Dict[str, Any]): 输入数据，必须包含：
                - values: 历史数据
                - timestamps: 时间戳列表（可选）
                
        返回:
            Dict[str, Any]: 分析结果，包含：
                - forecast: 预测值
                - confidence_intervals: 置信区间
                - model_metrics: 模型评估指标
        """
        # 验证输入数据
        self.validate_input(data, ['values'])
        
        values = data['values']
        if len(values) < self.min_data_points:
            raise ValueError(f"数据点数不足，至少需要{self.min_data_points}个点")
        
        # 生成预测
        forecast = self._generate_forecast(values)
        
        # 计算置信区间
        confidence_intervals = self._calculate_confidence_intervals(forecast)
        
        # 评估模型性能
        model_metrics = self._evaluate_model(values, forecast)
        
        return {
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'model_metrics': model_metrics
        }
    
    def _generate_forecast(self, values: List[float]) -> List[float]:
        """
        生成预测值
        
        参数:
            values (List[float]): 历史数据
            
        返回:
            List[float]: 预测值列表
        """
        # 使用简单的时间序列模型
        # 1. 计算趋势
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # 2. 计算季节性
        seasonal_pattern = self._extract_seasonality(values)
        
        # 3. 生成预测
        forecast = []
        for i in range(self.forecast_horizon):
            # 趋势部分
            trend_value = slope * (len(values) + i) + intercept
            
            # 季节性部分
            seasonal_value = seasonal_pattern[i % len(seasonal_pattern)]
            
            # 组合预测值
            forecast.append(trend_value + seasonal_value)
        
        return forecast
    
    def _extract_seasonality(self, values: List[float]) -> List[float]:
        """
        提取季节性模式
        
        参数:
            values (List[float]): 历史数据
            
        返回:
            List[float]: 季节性模式
        """
        # 使用移动平均去除趋势
        window_size = 7
        ma = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        
        # 计算季节性
        seasonal = values[window_size-1:] - ma
        
        # 计算平均季节性模式
        seasonal_pattern = []
        for i in range(window_size):
            pattern = seasonal[i::window_size]
            if len(pattern) > 0:
                seasonal_pattern.append(np.mean(pattern))
            else:
                seasonal_pattern.append(0)
        
        return seasonal_pattern
    
    def _calculate_confidence_intervals(
        self,
        forecast: List[float]
    ) -> List[Dict[str, float]]:
        """
        计算预测值的置信区间
        
        参数:
            forecast (List[float]): 预测值列表
            
        返回:
            List[Dict[str, float]]: 置信区间列表
        """
        # 计算预测值的标准差
        std = np.std(forecast)
        
        # 计算z分数
        z_score = 1.96  # 95% 置信区间
        
        confidence_intervals = []
        for value in forecast:
            confidence_intervals.append({
                'lower_bound': value - z_score * std,
                'upper_bound': value + z_score * std
            })
        
        return confidence_intervals
    
    def _evaluate_model(
        self,
        actual: List[float],
        forecast: List[float]
    ) -> Dict[str, float]:
        """
        评估模型性能
        
        参数:
            actual (List[float]): 实际值
            forecast (List[float]): 预测值
            
        返回:
            Dict[str, float]: 模型评估指标
        """
        # 计算评估指标
        mse = np.mean((np.array(actual) - np.array(forecast)) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(np.array(actual) - np.array(forecast)))
        mape = np.mean(np.abs((np.array(actual) - np.array(forecast)) / np.array(actual))) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        } 