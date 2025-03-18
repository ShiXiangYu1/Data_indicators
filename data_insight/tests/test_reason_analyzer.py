#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
原因分析器测试
===========

测试reason_analyzer模块中的ReasonAnalyzer类。
"""

import pytest
from data_insight.core.reason_analyzer import ReasonAnalyzer


class TestReasonAnalyzer:
    """测试原因分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = ReasonAnalyzer(use_llm=False)  # 测试时不使用LLM
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        analyzer = ReasonAnalyzer()
        assert analyzer.use_llm == True
        
        analyzer = ReasonAnalyzer(use_llm=False)
        assert analyzer.use_llm == False
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备缺少必要字段的数据
        data = {
            "基本信息": {
                "指标名称": "销售额"
                # 缺少当前值和上一期值
            }
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含缺少的字段
        assert "当前值" in str(excinfo.value)
    
    def test_basic_reason_analysis(self):
        """测试基本原因分析"""
        # 准备测试数据
        data = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月"
            },
            "变化分析": {
                "变化量": 20,
                "变化率": 0.2,
                "变化类别": "增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0.0,
                "是否高于正常范围": None
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果
        assert "原因分析" in result
        assert "可能原因" in result["原因分析"]
        assert "置信度" in result["原因分析"]
        assert len(result["原因分析"]["可能原因"]) > 0
    
    def test_seasonal_reason_analysis(self):
        """测试季节性原因分析"""
        # 准备带历史数据的测试数据
        data = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 150,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月"
            },
            "变化分析": {
                "变化量": 50,
                "变化率": 0.5,
                "变化类别": "大幅增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0.0,
                "是否高于正常范围": None
            },
            "历史数据": {
                "values": [80, 90, 100, 120, 130, 140, 150],
                "time_periods": ["2023年1月", "2023年2月", "2023年3月", 
                               "2023年4月", "2023年5月", "2023年6月", "2023年7月"]
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含季节性分析
        reasons = result["原因分析"]["可能原因"]
        assert any("季节性" in reason for reason in reasons)
    
    def test_anomaly_reason_analysis(self):
        """测试异常原因分析"""
        # 准备带异常的分析数据
        data = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 200,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月"
            },
            "变化分析": {
                "变化量": 100,
                "变化率": 1.0,
                "变化类别": "大幅增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": True,
                "异常程度": 2.5,
                "是否高于正常范围": True
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含异常分析
        reasons = result["原因分析"]["可能原因"]
        assert any("异常" in reason for reason in reasons)
    
    def test_metric_relations_analysis(self):
        """测试指标关系分析"""
        # 准备带相关指标的数据
        data = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月"
            },
            "变化分析": {
                "变化量": 20,
                "变化率": 0.2,
                "变化类别": "增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0.0,
                "是否高于正常范围": None
            },
            "相关指标": [
                {
                    "name": "营销费用",
                    "value": 30,
                    "previous_value": 25,
                    "unit": "元"
                },
                {
                    "name": "客户数量",
                    "value": 1000,
                    "previous_value": 800,
                    "unit": "个"
                }
            ]
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含指标关系分析
        reasons = result["原因分析"]["可能原因"]
        assert any("营销" in reason for reason in reasons)
        assert any("客户" in reason for reason in reasons)
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        # 准备测试数据
        data = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月"
            },
            "变化分析": {
                "变化量": 20,
                "变化率": 0.2,
                "变化类别": "增长",
                "变化方向": "增加"
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0.0,
                "是否高于正常范围": None
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证置信度
        confidence = result["原因分析"]["置信度"]
        assert confidence in ["高", "中", "低"] 