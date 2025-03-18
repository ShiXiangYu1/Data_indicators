"""
预测分析器
=========

实现时间序列预测功能，包括趋势预测和异常预测。
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression

from data_insight.core.base_analyzer import BaseAnalyzer
from data_insight.utils.data_utils import detect_seasonal_pattern


class Predictor(BaseAnalyzer):
    """
    预测分析器
    
    实现时间序列预测功能，包括：
    1. 趋势预测：使用Holt-Winters方法进行时间序列预测
    2. 异常预测：基于历史异常模式预测未来可能的异常
    3. 季节性预测：考虑季节性因素进行预测
    """
    
    def __init__(self):
        """
        初始化预测分析器
        """
        super().__init__()
        # 预测参数
        self.forecast_periods = 3  # 预测未来3个周期
        self.confidence_level = 0.95  # 预测置信度
        self.min_history_length = 12  # 最小历史数据长度
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据并生成预测结果
        
        参数:
            data (Dict[str, Any]): 输入数据，应包含以下字段:
                - values: 历史值列表
                - time_periods: 时间周期列表
                - current_value: 当前值
                - current_period: 当前时间周期
                - unit: 单位(可选)
                - name: 指标名称(可选)
            
        返回:
            Dict[str, Any]: 预测结果
        """
        # 验证必要字段
        required_fields = ["values", "time_periods", "current_value", "current_period"]
        self.validate_input(data, required_fields)
        
        # 提取数据
        values = data["values"]
        time_periods = data["time_periods"]
        current_value = data["current_value"]
        current_period = data["current_period"]
        unit = data.get("unit", "")
        name = data.get("name", "指标")
        
        # 检查数据长度
        if len(values) < self.min_history_length:
            return {
                "预测结果": {
                    "状态": "数据不足",
                    "原因": f"历史数据长度({len(values)})小于最小要求({self.min_history_length})",
                    "建议": "收集更多历史数据以提高预测准确性"
                }
            }
        
        # 检测季节性
        seasonality, seasonal_strength = detect_seasonal_pattern(values)
        
        # 进行预测
        forecast_result = self._forecast(values, seasonality)
        
        # 预测异常
        anomaly_forecast = self._forecast_anomaly(values, current_value)
        
        # 整合结果
        result = {
            "基本信息": {
                "指标名称": name,
                "当前值": current_value,
                "当前周期": current_period,
                "单位": unit,
                "历史数据长度": len(values)
            },
            "预测结果": {
                "预测值": forecast_result["forecast"],
                "预测区间": forecast_result["intervals"],
                "预测周期": forecast_result["periods"],
                "置信度": self.confidence_level,
                "季节性": {
                    "是否存在": seasonality is not None,
                    "周期": seasonality,
                    "强度": seasonal_strength
                }
            },
            "异常预测": anomaly_forecast
        }
        
        return result
    
    def _forecast(self, values: List[float], seasonality: Optional[int] = None) -> Dict[str, Any]:
        """
        使用Holt-Winters方法进行时间序列预测
        
        参数:
            values (List[float]): 历史值列表
            seasonality (Optional[int]): 季节性周期
            
        返回:
            Dict[str, Any]: 预测结果
        """
        # 转换为numpy数组
        data = np.array(values)
        
        # 创建预测模型
        if seasonality is not None:
            model = ExponentialSmoothing(
                data,
                seasonal_periods=seasonality,
                trend='add',
                seasonal='add'
            )
        else:
            model = ExponentialSmoothing(
                data,
                trend='add',
                seasonal=None
            )
        
        # 拟合模型
        fitted_model = model.fit()
        
        # 生成预测
        forecast = fitted_model.forecast(self.forecast_periods)
        
        # 计算预测区间
        intervals = fitted_model.get_prediction(
            start=len(data),
            end=len(data) + self.forecast_periods - 1
        ).conf_int(alpha=1-self.confidence_level)
        
        # 生成预测周期
        periods = [f"T+{i+1}" for i in range(self.forecast_periods)]
        
        return {
            "forecast": forecast.tolist(),
            "intervals": intervals.tolist(),
            "periods": periods
        }
    
    def _forecast_anomaly(self, values: List[float], current_value: float) -> Dict[str, Any]:
        """
        预测未来可能的异常情况
        
        参数:
            values (List[float]): 历史值列表
            current_value (float): 当前值
            
        返回:
            Dict[str, Any]: 异常预测结果
        """
        # 计算历史统计量
        mean = np.mean(values)
        std = np.std(values)
        
        # 计算当前值的z分数
        current_z = (current_value - mean) / std
        
        # 基于当前趋势预测未来异常
        if abs(current_z) > 2:  # 当前值异常
            trend = "上升" if current_z > 0 else "下降"
            risk_level = "高" if abs(current_z) > 3 else "中"
        else:
            trend = "稳定"
            risk_level = "低"
        
        return {
            "风险等级": risk_level,
            "异常趋势": trend,
            "建议": self._get_anomaly_suggestion(risk_level, trend)
        }
    
    def _get_anomaly_suggestion(self, risk_level: str, trend: str) -> str:
        """
        根据风险等级和趋势生成建议
        
        参数:
            risk_level (str): 风险等级
            trend (str): 异常趋势
            
        返回:
            str: 建议文本
        """
        suggestions = {
            "高": {
                "上升": "建议立即进行调查，采取干预措施",
                "下降": "建议立即进行调查，采取干预措施",
                "稳定": "建议密切关注，准备应对措施"
            },
            "中": {
                "上升": "建议加强监控，关注发展趋势",
                "下降": "建议加强监控，关注发展趋势",
                "稳定": "建议保持关注，定期检查"
            },
            "低": {
                "上升": "建议保持关注，定期检查",
                "下降": "建议保持关注，定期检查",
                "稳定": "建议正常监控即可"
            }
        }
        
        return suggestions[risk_level][trend] 