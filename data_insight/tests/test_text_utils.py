#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本处理工具函数测试
=================

测试text_utils模块中的函数。
"""

import pytest
from data_insight.utils.text_utils import (
    format_number,
    format_percentage,
    get_change_description,
    get_anomaly_description
)


class TestFormatNumber:
    """测试格式化数字函数"""

    def test_format_small_number(self):
        """测试小数字格式化"""
        value = 123.45
        result = format_number(value, "元")
        assert result == "123.45元"

    def test_format_wan(self):
        """测试万级数字格式化"""
        value = 12345.678
        result = format_number(value, "元")
        assert result == "1.23万元"

    def test_format_yi(self):
        """测试亿级数字格式化"""
        value = 123456789.0
        result = format_number(value, "元")
        assert result == "1.23亿元"

    def test_format_zero(self):
        """测试零值格式化"""
        value = 0.0
        result = format_number(value, "元")
        assert result == "0元"

    def test_format_negative(self):
        """测试负数格式化"""
        value = -12345.678
        result = format_number(value, "元")
        assert result == "-1.23万元"
    
    def test_format_without_unit(self):
        """测试无单位格式化"""
        value = 123.45
        result = format_number(value)
        assert result == "123.45"
    
    def test_format_precision(self):
        """测试精度控制"""
        value = 123.4567
        result = format_number(value, precision=3)
        assert result == "123.457"  # 四舍五入
    
    def test_format_international(self):
        """测试国际格式"""
        value = 1234567.89
        result = format_number(value, use_wan=False)
        assert result == "1.23M"


class TestFormatPercentage:
    """测试格式化百分比函数"""

    def test_format_percentage_positive(self):
        """测试正百分比格式化"""
        value = 0.1234
        result = format_percentage(value)
        assert result == "12.34%"

    def test_format_percentage_negative(self):
        """测试负百分比格式化"""
        value = -0.0567
        result = format_percentage(value)
        assert result == "-5.67%"

    def test_format_percentage_zero(self):
        """测试零百分比格式化"""
        value = 0.0
        result = format_percentage(value)
        assert result == "0%"

    def test_format_percentage_large(self):
        """测试大百分比格式化"""
        value = 1.5  # 150%
        result = format_percentage(value)
        assert result == "150%"

    def test_format_percentage_small(self):
        """测试小百分比格式化"""
        value = 0.00123
        result = format_percentage(value)
        assert result == "0.12%"
    
    def test_format_percentage_none(self):
        """测试None值格式化"""
        value = None
        result = format_percentage(value)
        assert result == "N/A"
    
    def test_format_percentage_precision(self):
        """测试百分比精度控制"""
        value = 0.123456
        result = format_percentage(value, precision=3)
        assert result == "12.346%"  # 四舍五入
    
    def test_format_percentage_strip_zeros(self):
        """测试去除尾零"""
        value = 0.2500
        result = format_percentage(value)
        assert result == "25%"  # 去除尾零


class TestGetChangeDescription:
    """测试获取变化描述函数"""

    def test_large_increase_positive(self):
        """测试大幅增长-正向指标"""
        result = get_change_description("大幅增长", "销售额", True)
        # 由于函数内部是随机选择的，我们只能检查结果包含某些词语
        assert "销售额" in result
        assert any(term in result for term in ["大幅增长", "显著提升", "大幅提高", "大幅上升"])
        assert any(term in result for term in ["积极", "良好", "正面"])

    def test_decrease_positive(self):
        """测试下降-正向指标"""
        result = get_change_description("下降", "销售额", True)
        assert "销售额" in result
        assert any(term in result for term in ["下降", "下滑", "降低", "下跌"])
        assert any(term in result for term in ["关注", "警惕", "不佳", "负面"])

    def test_decrease_negative(self):
        """测试下降-负向指标"""
        result = get_change_description("下降", "成本", False)
        assert "成本" in result
        assert any(term in result for term in ["下降", "下滑", "降低", "下跌"])
        assert any(term in result for term in ["积极", "良好", "正面"])

    def test_stable(self):
        """测试基本持平"""
        result = get_change_description("基本持平", "销售额", True)
        assert "销售额" in result
        assert any(term in result for term in ["基本持平", "保持稳定", "变化不大", "相对稳定"])
        # 基本持平不应该有好坏评价
        assert "积极" not in result
        assert "需要关注" not in result

    def test_unknown(self):
        """测试未知变化"""
        result = get_change_description("未知", "销售额", True)
        assert "销售额" in result
        assert any(term in result for term in ["变化无法确定", "变化情况不明", "数据不足", "不确定"])
        # 未知不应该有好坏评价
        assert "积极" not in result
        assert "需要关注" not in result


class TestGetAnomalyDescription:
    """测试获取异常描述函数"""

    def test_high_anomaly(self):
        """测试高异常值"""
        result = get_anomaly_description(True, 2.5, "销售额", True)
        assert "销售额" in result
        assert "高于" in result
        assert any(term in result for term in ["非常", "明显", "极度"])

    def test_low_anomaly(self):
        """测试低异常值"""
        result = get_anomaly_description(True, 1.8, "销售额", False)
        assert "销售额" in result
        assert "低于" in result
        assert any(term in result for term in ["非常", "明显", "极度"])

    def test_slight_anomaly(self):
        """测试轻微异常值"""
        result = get_anomaly_description(True, 0.8, "销售额", True)
        assert "销售额" in result
        assert "高于" in result
        assert "略微" in result

    def test_extreme_anomaly(self):
        """测试极端异常值"""
        result = get_anomaly_description(True, 4.0, "销售额", True)
        assert "销售额" in result
        assert "高于" in result
        assert "极度" in result

    def test_normal_value(self):
        """测试正常值(无异常)"""
        result = get_anomaly_description(False, 0.0, "销售额", True)
        assert result == ""  # 无异常时返回空字符串 