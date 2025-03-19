#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
趋势分析模块的单元测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入被测试模块
from data_insight.analysis.trend import (
    detect_trends,
    quantify_trend,
    detect_change_points,
    extract_seasonality,
    forecast_trend,
    TrendDirection,
    ChangePointDetectionMethod
)


class TestTrendAnalysis:
    """趋势分析功能的测试类"""

    @pytest.fixture
    def increasing_data(self):
        """创建线性增长的测试数据集"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        # 值从100开始，每天增加1，加上少量随机噪声
        values = 100 + np.arange(100) + np.random.normal(0, 2, 100)
        return pd.DataFrame({'date': dates, 'value': values})

    @pytest.fixture
    def decreasing_data(self):
        """创建线性下降的测试数据集"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        # 值从200开始，每天减少1，加上少量随机噪声
        values = 200 - np.arange(100) + np.random.normal(0, 2, 100)
        return pd.DataFrame({'date': dates, 'value': values})

    @pytest.fixture
    def stable_data(self):
        """创建稳定的测试数据集（无明显趋势）"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        # 值在150附近波动，只有随机噪声
        values = 150 + np.random.normal(0, 5, 100)
        return pd.DataFrame({'date': dates, 'value': values})

    @pytest.fixture
    def seasonal_data(self):
        """创建带有季节性的测试数据集"""
        dates = pd.date_range('2023-01-01', periods=365, freq='D')
        # 基本趋势：每天增加0.1
        trend = np.arange(365) * 0.1
        # 季节性：周期为365天的正弦波，振幅为20
        seasonality = 20 * np.sin(np.arange(365) * 2 * np.pi / 365)
        # 随机噪声
        noise = np.random.normal(0, 3, 365)
        # 组合趋势、季节性和噪声
        values = 100 + trend + seasonality + noise
        return pd.DataFrame({'date': dates, 'value': values})

    @pytest.fixture
    def change_point_data(self):
        """创建带有变化点的测试数据集"""
        dates = pd.date_range('2023-01-01', periods=200, freq='D')
        # 前100天平稳，后100天上升
        values = np.concatenate([
            100 + np.random.normal(0, 3, 100),  # 平稳期
            100 + np.arange(100) + np.random.normal(0, 3, 100)  # 上升期
        ])
        return pd.DataFrame({'date': dates, 'value': values})

    def test_detect_trends_increasing(self, increasing_data):
        """测试检测上升趋势"""
        # 执行检测
        result = detect_trends(increasing_data, date_col='date', value_col='value')
        
        # 验证结果
        assert result['trend_direction'] == TrendDirection.INCREASING
        assert result['confidence'] > 0.90
        assert result['slope'] > 0

    def test_detect_trends_decreasing(self, decreasing_data):
        """测试检测下降趋势"""
        # 执行检测
        result = detect_trends(decreasing_data, date_col='date', value_col='value')
        
        # 验证结果
        assert result['trend_direction'] == TrendDirection.DECREASING
        assert result['confidence'] > 0.90
        assert result['slope'] < 0

    def test_detect_trends_stable(self, stable_data):
        """测试检测稳定趋势（无趋势）"""
        # 执行检测
        result = detect_trends(stable_data, date_col='date', value_col='value')
        
        # 验证结果
        assert result['trend_direction'] == TrendDirection.STABLE
        # 稳定数据的斜率应接近于0
        assert -0.1 <= result['slope'] <= 0.1

    def test_quantify_trend_precision(self, increasing_data):
        """测试趋势量化的精度"""
        # 执行量化
        result = quantify_trend(increasing_data, date_col='date', value_col='value')
        
        # 预期斜率约为1（每天增加1），允许5%的误差
        assert 0.95 <= result['slope'] <= 1.05
        # R²应该很高（良好拟合）
        assert result['r_squared'] > 0.95

    def test_detect_change_points(self, change_point_data):
        """测试变化点检测"""
        # 执行变化点检测
        result = detect_change_points(
            change_point_data, 
            date_col='date', 
            value_col='value',
            method=ChangePointDetectionMethod.PELT
        )
        
        # 验证结果
        assert 'change_points' in result
        assert len(result['change_points']) >= 1
        
        # 检查变化点是否在预期区域（接近100天处）
        change_point_dates = pd.to_datetime(result['change_points'])
        expected_date = pd.to_datetime('2023-01-01') + timedelta(days=100)
        
        # 允许10天的误差范围
        date_diffs = [(date - expected_date).days for date in change_point_dates]
        assert any(abs(diff) <= 10 for diff in date_diffs)

    def test_extract_seasonality(self, seasonal_data):
        """测试季节性提取"""
        # 执行季节性提取
        result = extract_seasonality(seasonal_data, date_col='date', value_col='value')
        
        # 验证结果
        assert 'has_seasonality' in result
        assert result['has_seasonality'] is True
        assert 'seasonal_periods' in result
        
        # 检查是否检测到了365天的周期
        detected_periods = result['seasonal_periods']
        assert any(350 <= period <= 380 for period in detected_periods)
        
        # 季节性成分的振幅应接近于20
        seasonal_component = result['seasonal_component']
        amplitude = (max(seasonal_component) - min(seasonal_component)) / 2
        assert 15 <= amplitude <= 25

    def test_forecast_trend(self, increasing_data):
        """测试趋势预测"""
        # 执行趋势预测（预测未来30天）
        forecast_days = 30
        result = forecast_trend(
            increasing_data, 
            date_col='date', 
            value_col='value',
            forecast_periods=forecast_days
        )
        
        # 验证结果
        assert 'forecast' in result
        assert len(result['forecast']) == forecast_days
        
        # 验证预测结果的日期是连续的
        forecast_dates = pd.to_datetime(result['forecast_dates'])
        last_data_date = pd.to_datetime(increasing_data['date'].iloc[-1])
        first_forecast_date = forecast_dates[0]
        assert (first_forecast_date - last_data_date).days == 1
        
        # 验证预测值是否合理（基于已知的增长模式）
        last_value = increasing_data['value'].iloc[-1]
        first_forecast = result['forecast'][0]
        # 由于趋势是每天增加约1，第一个预测值应该接近最后一个实际值+1
        assert last_value + 0.5 <= first_forecast <= last_value + 1.5

    # 边界情况测试
    def test_detect_trends_min_data_points(self):
        """测试最小数据点数量边界条件"""
        # 创建仅有3个数据点的数据集
        dates = pd.date_range('2023-01-01', periods=3, freq='D')
        values = [100, 101, 102]
        min_data = pd.DataFrame({'date': dates, 'value': values})
        
        # 执行检测
        result = detect_trends(min_data, date_col='date', value_col='value')
        
        # 验证结果
        assert 'trend_direction' in result
        # 使用最小数据点应该能识别出趋势，但置信度较低
        assert result['confidence'] < 0.9

    def test_detect_trends_different_date_formats(self, increasing_data):
        """测试不同日期格式的处理"""
        # 修改日期格式为字符串
        data_with_str_dates = increasing_data.copy()
        data_with_str_dates['date'] = data_with_str_dates['date'].dt.strftime('%Y-%m-%d')
        
        # 执行检测
        result = detect_trends(data_with_str_dates, date_col='date', value_col='value')
        
        # 验证结果
        assert result['trend_direction'] == TrendDirection.INCREASING
        assert result['confidence'] > 0.90

    # 异常情况测试
    def test_detect_trends_empty_data(self):
        """测试空数据集"""
        empty_df = pd.DataFrame({'date': [], 'value': []})
        
        # 验证是否抛出预期的异常
        with pytest.raises(ValueError, match="Empty dataset"):
            detect_trends(empty_df, date_col='date', value_col='value')

    def test_detect_trends_missing_columns(self, increasing_data):
        """测试缺失列的处理"""
        # 删除value列
        data_without_value = increasing_data.drop(columns=['value'])
        
        # 验证是否抛出预期的异常
        with pytest.raises(ValueError, match="Column 'value' not found"):
            detect_trends(data_without_value, date_col='date', value_col='value')

    def test_detect_trends_all_missing_values(self):
        """测试所有值都缺失的情况"""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        values = [None] * 10
        all_null_data = pd.DataFrame({'date': dates, 'value': values})
        
        # 验证是否抛出预期的异常
        with pytest.raises(ValueError, match="No valid data points"):
            detect_trends(all_null_data, date_col='date', value_col='value')

    def test_detect_trends_non_numeric_values(self):
        """测试非数值型数据的处理"""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        values = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        text_data = pd.DataFrame({'date': dates, 'value': values})
        
        # 验证是否抛出预期的异常
        with pytest.raises(ValueError, match="Non-numeric data"):
            detect_trends(text_data, date_col='date', value_col='value')

    def test_quantify_trend_perfect_correlation(self):
        """测试完美相关性的数据"""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        values = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]  # 完美线性关系
        perfect_data = pd.DataFrame({'date': dates, 'value': values})
        
        # 执行量化
        result = quantify_trend(perfect_data, date_col='date', value_col='value')
        
        # 验证结果
        assert result['slope'] == 10  # 每天增加10
        assert result['r_squared'] > 0.999  # 几乎完美拟合


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 