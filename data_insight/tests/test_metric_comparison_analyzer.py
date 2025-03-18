#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标对比分析器测试
==============

测试metric_comparison_analyzer模块中的MetricComparisonAnalyzer类。
"""

import pytest
import numpy as np
from data_insight.core.metric_comparison_analyzer import MetricComparisonAnalyzer


class TestMetricComparisonAnalyzer:
    """测试指标对比分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = MetricComparisonAnalyzer()
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'correlation_strength')
        assert isinstance(self.analyzer.correlation_strength, dict)
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备无metrics字段的测试数据
        data = {
            "time_periods": ["2023年1月", "2023年2月"]
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息
        assert "metrics" in str(excinfo.value)
    
    def test_insufficient_metrics(self):
        """测试指标数量不足"""
        # 准备只有一个指标的测试数据
        data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 100,
                    "previous_value": 90
                }
            ]
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含相关信息
        assert "至少两个指标" in str(excinfo.value)
    
    def test_basic_comparison_analysis(self):
        """测试基本对比分析功能"""
        # 准备测试数据 - 两个指标
        data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 120,
                    "previous_value": 100,
                    "unit": "万元"
                },
                {
                    "name": "利润",
                    "value": 30,
                    "previous_value": 25,
                    "unit": "万元"
                }
            ]
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果结构
        assert "基本信息" in result
        assert "对比分析" in result
        assert "相关性分析" in result
        assert "群组分析" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["指标数量"] == 2
        assert basic_info["指标名称列表"] == ["销售额", "利润"]
        
        # 验证对比分析
        comparisons = result["对比分析"]
        assert len(comparisons) == 1  # 2个指标组合成1对
        
        comparison = comparisons[0]
        assert comparison["指标1"]["名称"] == "销售额"
        assert comparison["指标2"]["名称"] == "利润"
        assert comparison["指标1"]["当前值"] == 120
        assert comparison["指标2"]["当前值"] == 30
        assert comparison["绝对差异"] == 90
        assert comparison["相对差异"] == 3.0  # (120 - 30) / 30 = 3.0
        assert comparison["差异方向"] == "高于"
        assert comparison["差异大小"] in ["巨大差异", "大幅差异"]  # 根据分类规则，300%是巨大差异
    
    def test_correlation_analysis(self):
        """测试相关性分析功能"""
        # 创建一组高度相关的历史数据
        base_values = [100, 110, 105, 115, 120]
        correlated_values = [25, 27.5, 26.25, 28.75, 30]  # 刻意设计为基础值的25%
        
        # 准备测试数据 - 两个有历史值的指标
        data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 130,
                    "previous_value": 120,
                    "unit": "万元",
                    "historical_values": base_values
                },
                {
                    "name": "利润",
                    "value": 32.5,
                    "previous_value": 30,
                    "unit": "万元",
                    "historical_values": correlated_values
                }
            ],
            "time_periods": ["2023年1月", "2023年2月", "2023年3月", "2023年4月", "2023年5月", "2023年6月"]
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证相关性分析
        correlations = result["相关性分析"]
        assert len(correlations) == 1
        
        correlation = correlations[0]
        assert correlation["指标1"] == "销售额"
        assert correlation["指标2"] == "利润"
        assert correlation["相关系数"] > 0.95  # 应该非常接近1，因为是完全线性相关
        assert correlation["相关性类型"] == "正相关"
        assert correlation["相关性强度"] == "强相关"  # 根据我们的分类规则
        assert correlation["样本数量"] == 5
    
    def test_metric_groups_analysis(self):
        """测试指标群组分析功能"""
        # 准备测试数据 - 多个具有不同变化趋势的指标
        data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 120,  # 增长20%
                    "previous_value": 100,
                    "unit": "万元"
                },
                {
                    "name": "利润",
                    "value": 30,  # 增长20%
                    "previous_value": 25,
                    "unit": "万元"
                },
                {
                    "name": "成本",
                    "value": 85,  # 下降约5.6%
                    "previous_value": 90,
                    "unit": "万元"
                },
                {
                    "name": "客户数",
                    "value": 1050,  # 增长5%
                    "previous_value": 1000,
                    "unit": "个"
                },
                {
                    "name": "投诉率",
                    "value": 0.021,  # 下降16%
                    "previous_value": 0.025,
                    "unit": ""
                },
                {
                    "name": "平均订单金额",
                    "value": 1030,  # 稳定，变化率低于5%
                    "previous_value": 1000,
                    "unit": "元"
                }
            ]
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证群组分析
        groups = result["群组分析"]
        
        # 验证增长指标组
        assert len(groups["增长指标"]) == 2  # 销售额和利润增长超过5%
        growth_names = [item["指标名称"] for item in groups["增长指标"]]
        assert "销售额" in growth_names
        assert "利润" in growth_names
        
        # 验证下降指标组
        assert len(groups["下降指标"]) == 2  # 成本和投诉率下降超过5%
        decline_names = [item["指标名称"] for item in groups["下降指标"]]
        assert "成本" in decline_names
        assert "投诉率" in decline_names
        
        # 验证稳定指标组
        assert len(groups["稳定指标"]) == 2  # 客户数和平均订单金额变化不超过5%
        stable_names = [item["指标名称"] for item in groups["稳定指标"]]
        assert "客户数" in stable_names or "平均订单金额" in stable_names
    
    def test_anomaly_group(self):
        """测试异常指标分组"""
        # 准备测试数据 - 包含异常指标
        data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 120,
                    "previous_value": 100,
                    "unit": "万元"
                },
                {
                    "name": "利润",
                    "value": 30,
                    "previous_value": 25,
                    "unit": "万元"
                },
                {
                    "name": "客户投诉",
                    "value": 50,
                    "previous_value": 30,
                    "unit": "件",
                    "is_anomaly": True,
                    "anomaly_degree": 2.5
                }
            ]
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证异常指标组
        groups = result["群组分析"]
        assert len(groups["异常指标"]) == 1
        anomaly = groups["异常指标"][0]
        assert anomaly["指标名称"] == "客户投诉"
        assert anomaly["异常程度"] == 2.5
    
    def test_classify_difference(self):
        """测试差异分类功能"""
        # 测试各种差异大小的分类
        assert self.analyzer._classify_difference(None) == "无法比较"
        assert self.analyzer._classify_difference(0.03) == "微小差异"
        assert self.analyzer._classify_difference(0.15) == "小幅差异"
        assert self.analyzer._classify_difference(0.3) == "中等差异"
        assert self.analyzer._classify_difference(0.8) == "大幅差异"
        assert self.analyzer._classify_difference(1.5) == "巨大差异"
    
    def test_describe_correlation_strength(self):
        """测试相关性强度描述功能"""
        # 测试各种相关系数的强度描述
        assert self.analyzer._describe_correlation_strength(0.1) == "几乎不相关"
        assert self.analyzer._describe_correlation_strength(0.3) == "弱相关"
        assert self.analyzer._describe_correlation_strength(0.5) == "中等相关"
        assert self.analyzer._describe_correlation_strength(0.7) == "较强相关"
        assert self.analyzer._describe_correlation_strength(0.9) == "强相关"
        assert self.analyzer._describe_correlation_strength(1.0) == "强相关"  # 边界检查 