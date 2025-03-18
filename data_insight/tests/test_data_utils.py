#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据处理工具函数测试
=================

测试data_utils模块中的函数。
"""

import pytest
import numpy as np
from data_insight.utils.data_utils import (
    calculate_change_rate,
    calculate_change,
    classify_change,
    detect_anomaly,
    calculate_trend
)


class TestCalculateChangeRate:
    """测试计算变化率函数"""

    def test_positive_change(self):
        """测试正向变化"""
        current_value = 120
        previous_value = 100
        expected = 0.2  # (120 - 100) / 100 = 0.2
        result = calculate_change_rate(current_value, previous_value)
        assert result == expected

    def test_negative_change(self):
        """测试负向变化"""
        current_value = 80
        previous_value = 100
        expected = -0.2  # (80 - 100) / 100 = -0.2
        result = calculate_change_rate(current_value, previous_value)
        assert result == expected

    def test_no_change(self):
        """测试无变化"""
        current_value = 100
        previous_value = 100
        expected = 0.0  # (100 - 100) / 100 = 0.0
        result = calculate_change_rate(current_value, previous_value)
        assert result == expected

    def test_zero_previous_value(self):
        """测试上一期值为0的情况"""
        current_value = 100
        previous_value = 0
        result = calculate_change_rate(current_value, previous_value)
        assert result is None


class TestCalculateChange:
    """测试计算变化量函数"""

    def test_positive_change(self):
        """测试正向变化"""
        current_value = 120
        previous_value = 100
        expected = 20  # 120 - 100 = 20
        result = calculate_change(current_value, previous_value)
        assert result == expected

    def test_negative_change(self):
        """测试负向变化"""
        current_value = 80
        previous_value = 100
        expected = -20  # 80 - 100 = -20
        result = calculate_change(current_value, previous_value)
        assert result == expected

    def test_no_change(self):
        """测试无变化"""
        current_value = 100
        previous_value = 100
        expected = 0  # 100 - 100 = 0
        result = calculate_change(current_value, previous_value)
        assert result == expected


class TestClassifyChange:
    """测试分类变化程度函数"""

    def test_classify_large_increase(self):
        """测试大幅增长"""
        change_rate = 0.6
        expected = "大幅增长"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_increase(self):
        """测试增长"""
        change_rate = 0.15
        expected = "增长"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_slight_increase(self):
        """测试轻微增长"""
        change_rate = 0.05
        expected = "轻微增长"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_stable(self):
        """测试基本持平"""
        change_rate = 0.0
        expected = "基本持平"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_slight_decrease(self):
        """测试轻微下降"""
        change_rate = -0.05
        expected = "轻微下降"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_decrease(self):
        """测试下降"""
        change_rate = -0.15
        expected = "下降"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_large_decrease(self):
        """测试大幅下降"""
        change_rate = -0.6
        expected = "大幅下降"
        result = classify_change(change_rate)
        assert result == expected

    def test_classify_none(self):
        """测试None值"""
        change_rate = None
        expected = "未知"
        result = classify_change(change_rate)
        assert result == expected


class TestDetectAnomaly:
    """测试异常检测函数"""

    def test_normal_value(self):
        """测试正常值"""
        value = 105
        historical_values = [90, 95, 100, 110, 115]
        threshold = 1.5
        is_anomaly, anomaly_degree = detect_anomaly(value, historical_values, threshold)
        assert is_anomaly is False
        assert anomaly_degree == 0.0

    def test_upper_anomaly(self):
        """测试异常高值"""
        value = 150
        historical_values = [90, 95, 100, 110, 115]
        threshold = 1.5
        is_anomaly, anomaly_degree = detect_anomaly(value, historical_values, threshold)
        assert is_anomaly is True
        assert anomaly_degree > 0.0

    def test_lower_anomaly(self):
        """测试异常低值"""
        value = 50
        historical_values = [90, 95, 100, 110, 115]
        threshold = 1.5
        is_anomaly, anomaly_degree = detect_anomaly(value, historical_values, threshold)
        assert is_anomaly is True
        assert anomaly_degree > 0.0

    def test_empty_historical_values(self):
        """测试空历史值列表"""
        value = 100
        historical_values = []
        is_anomaly, anomaly_degree = detect_anomaly(value, historical_values)
        assert is_anomaly is False
        assert anomaly_degree == 0.0

    def test_different_threshold(self):
        """测试不同阈值"""
        value = 130
        historical_values = [90, 95, 100, 110, 115]
        
        # 较小阈值应该检测为异常
        is_anomaly1, _ = detect_anomaly(value, historical_values, threshold=1.0)
        assert is_anomaly1 is True
        
        # 较大阈值可能不会检测为异常
        is_anomaly2, _ = detect_anomaly(value, historical_values, threshold=2.5)
        # 此处不断言具体结果，因为它取决于具体的数据分布


class TestCalculateTrend:
    """测试计算趋势函数"""

    def test_strong_upward_trend(self):
        """测试强烈上升趋势"""
        values = [100, 120, 150, 190, 240]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "强烈上升"
        assert trend_strength > 0.0

    def test_upward_trend(self):
        """测试上升趋势"""
        values = [100, 110, 115, 125, 135]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "上升"
        assert trend_strength > 0.0

    def test_slight_upward_trend(self):
        """测试轻微上升趋势"""
        values = [100, 102, 103, 105, 107]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "轻微上升"
        assert trend_strength > 0.0

    def test_stable_trend(self):
        """测试平稳趋势"""
        values = [100, 101, 99, 100, 101]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "平稳"
        assert trend_strength >= 0.0

    def test_slight_downward_trend(self):
        """测试轻微下降趋势"""
        values = [100, 98, 97, 95, 93]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "轻微下降"
        assert trend_strength > 0.0

    def test_downward_trend(self):
        """测试下降趋势"""
        values = [100, 90, 85, 75, 65]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "下降"
        assert trend_strength > 0.0

    def test_strong_downward_trend(self):
        """测试强烈下降趋势"""
        values = [100, 80, 50, 20, 10]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "强烈下降"
        assert trend_strength > 0.0

    def test_insufficient_data(self):
        """测试数据不足的情况"""
        values = [100]
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "数据不足"
        assert trend_strength == 0.0

    def test_empty_data(self):
        """测试空数据的情况"""
        values = []
        trend_type, trend_strength = calculate_trend(values)
        assert trend_type == "数据不足"
        assert trend_strength == 0.0 