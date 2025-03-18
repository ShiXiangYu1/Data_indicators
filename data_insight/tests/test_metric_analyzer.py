#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标分析器测试
===========

测试metric_analyzer模块中的MetricAnalyzer类。
"""

import pytest
from data_insight.core.metric_analyzer import MetricAnalyzer


class TestMetricAnalyzer:
    """测试指标分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = MetricAnalyzer()
    
    def test_basic_analysis(self):
        """测试基本分析功能"""
        # 准备测试数据
        metric_data = {
            "name": "销售额",
            "value": 120,
            "previous_value": 100,
            "unit": "元"
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证结果
        assert "基本信息" in result
        assert "变化分析" in result
        assert "异常分析" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["指标名称"] == "销售额"
        assert basic_info["当前值"] == 120
        assert basic_info["上一期值"] == 100
        assert basic_info["单位"] == "元"
        assert basic_info["正向增长是否为好"] == True  # 销售额默认增长为好
        
        # 验证变化分析
        change_analysis = result["变化分析"]
        assert change_analysis["变化量"] == 20
        assert change_analysis["变化率"] == 0.2
        assert change_analysis["变化类别"] == "增长"
        assert change_analysis["变化方向"] == "增加"
    
    def test_analysis_with_historical_values(self):
        """测试带历史值的分析功能"""
        # 准备测试数据
        metric_data = {
            "name": "销售额",
            "value": 120,
            "previous_value": 100,
            "unit": "元",
            "historical_values": [80, 85, 90, 95, 100]
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证包含趋势分析
        assert "趋势分析" in result
        
        # 验证趋势分析结果
        trend_analysis = result["趋势分析"]
        assert "趋势类型" in trend_analysis
        assert "趋势强度" in trend_analysis
        assert trend_analysis["趋势强度"] > 0.0
    
    def test_analysis_with_anomaly(self):
        """测试异常检测功能"""
        # 准备测试数据 - 高异常值
        metric_data = {
            "name": "销售额",
            "value": 200,  # 明显高于历史值
            "previous_value": 100,
            "unit": "元",
            "historical_values": [80, 85, 90, 95, 100]
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证异常分析结果
        anomaly_analysis = result["异常分析"]
        assert anomaly_analysis["是否异常"] == True
        assert anomaly_analysis["异常程度"] > 0.0
        assert anomaly_analysis["是否高于正常范围"] == True
    
    def test_negative_indicator(self):
        """测试负向指标分析"""
        # 准备测试数据 - 成本类指标
        metric_data = {
            "name": "成本",
            "value": 120,
            "previous_value": 100,
            "unit": "元"
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证基本信息 - 成本类指标默认增长为坏
        basic_info = result["基本信息"]
        assert basic_info["正向增长是否为好"] == False
    
    def test_custom_is_positive_better(self):
        """测试自定义正向性"""
        # 准备测试数据 - 正向指标设置为负
        metric_data = {
            "name": "销售额",
            "value": 120,
            "previous_value": 100,
            "unit": "元",
            "is_positive_better": False  # 自定义设置
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证基本信息 - 自定义设置优先
        basic_info = result["基本信息"]
        assert basic_info["正向增长是否为好"] == False
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备测试数据 - 缺少value字段
        metric_data = {
            "name": "销售额",
            "previous_value": 100
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(metric_data)
        
        # 验证异常消息包含缺少的字段
        assert "value" in str(excinfo.value)
    
    def test_no_change(self):
        """测试无变化情况"""
        # 准备测试数据 - 当前值等于上一期值
        metric_data = {
            "name": "销售额",
            "value": 100,
            "previous_value": 100,
            "unit": "元"
        }
        
        # 运行分析
        result = self.analyzer.analyze(metric_data)
        
        # 验证变化分析
        change_analysis = result["变化分析"]
        assert change_analysis["变化量"] == 0
        assert change_analysis["变化率"] == 0.0
        assert change_analysis["变化类别"] == "基本持平"
        assert change_analysis["变化方向"] == "保持不变" 