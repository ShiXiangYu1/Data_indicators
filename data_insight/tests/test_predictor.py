"""
预测分析器测试
===========

测试predictor模块中的Predictor类。
"""

import pytest
import numpy as np
from data_insight.core.predictor import Predictor


class TestPredictor:
    """测试预测分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.predictor = Predictor()
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.predictor.forecast_periods == 3
        assert self.predictor.confidence_level == 0.95
        assert self.predictor.min_history_length == 12
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备缺少必要字段的数据
        data = {
            "values": [1, 2, 3],
            "time_periods": ["T1", "T2", "T3"]
            # 缺少current_value和current_period
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.predictor.analyze(data)
        
        # 验证异常消息包含缺少的字段
        assert "current_value" in str(excinfo.value)
    
    def test_insufficient_data(self):
        """测试数据不足的情况"""
        # 准备数据不足的测试数据
        data = {
            "values": [1, 2, 3, 4, 5],  # 少于最小要求的历史数据长度
            "time_periods": ["T1", "T2", "T3", "T4", "T5"],
            "current_value": 5,
            "current_period": "T5"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证结果
        assert "预测结果" in result
        assert result["预测结果"]["状态"] == "数据不足"
        assert "历史数据长度" in result["预测结果"]["原因"]
    
    def test_basic_forecast(self):
        """测试基本预测功能"""
        # 准备测试数据
        values = list(range(1, 13))  # 12个月的数据
        time_periods = [f"2023年{i}月" for i in range(1, 13)]
        data = {
            "values": values,
            "time_periods": time_periods,
            "current_value": 12,
            "current_period": "2023年12月",
            "name": "销售额",
            "unit": "万元"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证结果
        assert "基本信息" in result
        assert "预测结果" in result
        assert "异常预测" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["指标名称"] == "销售额"
        assert basic_info["当前值"] == 12
        assert basic_info["单位"] == "万元"
        
        # 验证预测结果
        forecast_result = result["预测结果"]
        assert len(forecast_result["预测值"]) == 3  # 预测3个周期
        assert len(forecast_result["预测区间"]) == 3
        assert len(forecast_result["预测周期"]) == 3
        assert forecast_result["置信度"] == 0.95
    
    def test_seasonal_forecast(self):
        """测试季节性预测"""
        # 准备带季节性的测试数据
        values = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]  # 明显的上升趋势
        time_periods = [f"2023年{i}月" for i in range(1, 13)]
        data = {
            "values": values,
            "time_periods": time_periods,
            "current_value": 65,
            "current_period": "2023年12月"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证季节性分析
        seasonal_info = result["预测结果"]["季节性"]
        assert "是否存在" in seasonal_info
        assert "周期" in seasonal_info
        assert "强度" in seasonal_info
    
    def test_anomaly_forecast(self):
        """测试异常预测"""
        # 准备带异常的测试数据
        values = [100, 102, 98, 101, 99, 150, 103, 101, 99, 102, 98, 100]  # 包含一个异常值
        time_periods = [f"2023年{i}月" for i in range(1, 13)]
        data = {
            "values": values,
            "time_periods": time_periods,
            "current_value": 150,  # 异常值
            "current_period": "2023年6月"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证异常预测
        anomaly_forecast = result["异常预测"]
        assert "风险等级" in anomaly_forecast
        assert "异常趋势" in anomaly_forecast
        assert "建议" in anomaly_forecast
        
        # 验证高风险异常
        assert anomaly_forecast["风险等级"] in ["高", "中", "低"]
        assert anomaly_forecast["异常趋势"] in ["上升", "下降", "稳定"]
    
    def test_forecast_with_different_seasonality(self):
        """测试不同季节性周期的预测"""
        # 准备季度性数据
        values = [100, 80, 60, 100, 80, 60, 100, 80, 60, 100, 80, 60]  # 明显的季度性
        time_periods = [f"2023年{i}月" for i in range(1, 13)]
        data = {
            "values": values,
            "time_periods": time_periods,
            "current_value": 60,
            "current_period": "2023年12月"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证季节性分析
        seasonal_info = result["预测结果"]["季节性"]
        assert seasonal_info["是否存在"] == True
        assert seasonal_info["周期"] == 3  # 季度性
        assert 0 <= seasonal_info["强度"] <= 1
    
    def test_forecast_with_trend(self):
        """测试带趋势的预测"""
        # 准备带上升趋势的数据
        values = [100 + i * 5 for i in range(12)]  # 线性上升趋势
        time_periods = [f"2023年{i}月" for i in range(1, 13)]
        data = {
            "values": values,
            "time_periods": time_periods,
            "current_value": values[-1],
            "current_period": "2023年12月"
        }
        
        # 运行分析
        result = self.predictor.analyze(data)
        
        # 验证预测值保持上升趋势
        forecast_values = result["预测结果"]["预测值"]
        assert all(forecast_values[i] <= forecast_values[i+1] for i in range(len(forecast_values)-1)) 