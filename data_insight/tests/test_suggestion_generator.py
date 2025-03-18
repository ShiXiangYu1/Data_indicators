"""
智能建议生成器测试
===============

测试suggestion_generator模块中的SuggestionGenerator类。
"""

import pytest
import numpy as np
from data_insight.core.suggestion_generator import SuggestionGenerator


class TestSuggestionGenerator:
    """测试智能建议生成器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化生成器"""
        self.generator = SuggestionGenerator()
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.generator.min_confidence == 0.6
        assert self.generator.max_suggestions == 5
        assert self.generator.priority_threshold == 0.7
        assert isinstance(self.generator.suggestion_templates, dict)
        assert isinstance(self.generator.action_templates, dict)
        
        # 测试自定义参数初始化
        custom_generator = SuggestionGenerator(
            min_confidence=0.8,
            max_suggestions=10,
            priority_threshold=0.8
        )
        assert custom_generator.min_confidence == 0.8
        assert custom_generator.max_suggestions == 10
        assert custom_generator.priority_threshold == 0.8
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备缺少必要字段的数据
        data = {
            # 缺少metric_analysis
            "chart_analysis": {},
            "attribution_analysis": {}
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.generator.analyze(data)
        
        # 验证异常消息包含缺少的字段
        assert "metric_analysis" in str(excinfo.value)
    
    def test_basic_metric_suggestions(self):
        """测试基本指标建议生成"""
        # 准备测试数据
        data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "变化分析": {
                    "变化类别": "显著上升",
                    "变化率": 0.3
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0
                }
            }
        }
        
        # 运行分析
        result = self.generator.analyze(data)
        
        # 验证结果结构
        assert "建议列表" in result
        assert "总体效果" in result
        assert "建议数量" in result
        assert "高优先级建议数" in result
        
        # 验证建议内容
        suggestions = result["建议列表"]
        assert len(suggestions) > 0
        assert all(isinstance(s, dict) for s in suggestions)
        assert all("建议内容" in s for s in suggestions)
        assert all("优先级" in s for s in suggestions)
        assert all("置信度" in s for s in suggestions)
        assert all("预期效果" in s for s in suggestions)
        assert all("建议类型" in s for s in suggestions)
    
    def test_chart_suggestions(self):
        """测试图表建议生成"""
        # 准备测试数据
        data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "变化分析": {
                    "变化类别": "基本持平",
                    "变化率": 0.05
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0
                }
            },
            "chart_analysis": {
                "基本信息": {
                    "图表标题": "销售额趋势"
                },
                "趋势分析": {
                    "趋势类型": "下降",
                    "趋势强度": 0.4
                },
                "异常点分析": [
                    {
                        "时间点": "2023-03-15",
                        "异常程度": 1.8
                    }
                ]
            }
        }
        
        # 运行分析
        result = self.generator.analyze(data)
        
        # 验证结果
        suggestions = result["建议列表"]
        assert len(suggestions) > 0
        
        # 验证是否包含基于趋势的建议
        trend_suggestions = [s for s in suggestions if s["建议类型"] == "趋势优化"]
        assert len(trend_suggestions) > 0
        
        # 验证是否包含基于异常点的建议
        anomaly_suggestions = [s for s in suggestions if s["建议类型"] == "异常处理"]
        assert len(anomaly_suggestions) > 0
    
    def test_attribution_suggestions(self):
        """测试归因建议生成"""
        # 准备测试数据
        data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "变化分析": {
                    "变化类别": "基本持平",
                    "变化率": 0.05
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0
                }
            },
            "attribution_analysis": {
                "目标指标": "销售额",
                "因素贡献": [
                    {
                        "因素名称": "广告支出",
                        "贡献度": 0.4,
                        "影响方向": "正向"
                    },
                    {
                        "因素名称": "价格调整",
                        "贡献度": 0.3,
                        "影响方向": "负向"
                    }
                ]
            }
        }
        
        # 运行分析
        result = self.generator.analyze(data)
        
        # 验证结果
        suggestions = result["建议列表"]
        assert len(suggestions) > 0
        
        # 验证是否包含基于归因的建议
        attribution_suggestions = [s for s in suggestions if "广告支出" in s["建议内容"] or "价格调整" in s["建议内容"]]
        assert len(attribution_suggestions) > 0
    
    def test_root_cause_suggestions(self):
        """测试根因建议生成"""
        # 准备测试数据
        data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "变化分析": {
                    "变化类别": "基本持平",
                    "变化率": 0.05
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0
                }
            },
            "root_cause_analysis": {
                "目标指标": "销售额",
                "根因列表": [
                    {
                        "根因描述": "市场竞争加剧",
                        "根因类型": "外部因素",
                        "影响程度": 0.6
                    },
                    {
                        "根因描述": "产品竞争力不足",
                        "根因类型": "内部因素",
                        "影响程度": 0.4
                    }
                ]
            }
        }
        
        # 运行分析
        result = self.generator.analyze(data)
        
        # 验证结果
        suggestions = result["建议列表"]
        assert len(suggestions) > 0
        
        # 验证是否包含基于根因的建议
        root_cause_suggestions = [s for s in suggestions if s["建议类型"] == "根因解决"]
        assert len(root_cause_suggestions) > 0
    
    def test_prediction_suggestions(self):
        """测试预测建议生成"""
        # 准备测试数据
        data = {
            "metric_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "变化分析": {
                    "变化类别": "基本持平",
                    "变化率": 0.05
                },
                "异常分析": {
                    "是否异常": False,
                    "异常程度": 0
                }
            },
            "prediction_analysis": {
                "基本信息": {
                    "指标名称": "销售额"
                },
                "预测结果": {
                    "预测值": [100, 95, 90, 85, 80]
                },
                "异常预测": {
                    "风险等级": "高"
                }
            }
        }
        
        # 运行分析
        result = self.generator.analyze(data)
        
        # 验证结果
        suggestions = result["建议列表"]
        assert len(suggestions) > 0
        
        # 验证是否包含基于预测的建议
        prediction_suggestions = [s for s in suggestions if s["建议类型"] in ["趋势优化", "异常处理"]]
        assert len(prediction_suggestions) > 0
    
    def test_suggestion_priority(self):
        """测试建议优先级计算"""
        # 测试高优先级
        assert self.generator._calculate_priority(0.8) == "高"
        assert self.generator._calculate_priority(0.7) == "高"
        
        # 测试中优先级
        assert self.generator._calculate_priority(0.6) == "中"
        assert self.generator._calculate_priority(0.5) == "中"
        
        # 测试低优先级
        assert self.generator._calculate_priority(0.4) == "低"
        assert self.generator._calculate_priority(0.3) == "低"
    
    def test_suggestion_confidence(self):
        """测试建议置信度计算"""
        # 测试高置信度
        high_confidence = self.generator._calculate_confidence({
            "effect": 0.8,
            "anomaly_type": "显著",
            "risk_level": "高"
        })
        assert high_confidence >= 0.8
        
        # 测试中等置信度
        medium_confidence = self.generator._calculate_confidence({
            "effect": 0.5,
            "anomaly_type": "轻微",
            "risk_level": "中"
        })
        assert 0.5 <= medium_confidence < 0.8
        
        # 测试低置信度
        low_confidence = self.generator._calculate_confidence({
            "effect": 0.2,
            "anomaly_type": "",
            "risk_level": "低"
        })
        assert low_confidence < 0.5
    
    def test_suggestion_filtering(self):
        """测试建议筛选"""
        # 准备测试数据
        suggestions = [
            {
                "建议内容": "建议1",
                "优先级": "高",
                "置信度": 0.8,
                "预期效果": 0.7,
                "建议类型": "指标提升"
            },
            {
                "建议内容": "建议2",
                "优先级": "中",
                "置信度": 0.5,
                "预期效果": 0.4,
                "建议类型": "异常处理"
            },
            {
                "建议内容": "建议3",
                "优先级": "低",
                "置信度": 0.3,
                "预期效果": 0.2,
                "建议类型": "趋势优化"
            }
        ]
        
        # 运行筛选
        filtered_suggestions = self.generator._sort_and_filter_suggestions(suggestions)
        
        # 验证结果
        assert len(filtered_suggestions) <= self.generator.max_suggestions
        assert all(s["置信度"] >= self.generator.min_confidence for s in filtered_suggestions)
        assert filtered_suggestions[0]["优先级"] == "高"
    
    def test_overall_effect_calculation(self):
        """测试总体效果计算"""
        # 准备测试数据
        suggestions = [
            {
                "建议内容": "建议1",
                "优先级": "高",
                "置信度": 0.8,
                "预期效果": 0.7,
                "建议类型": "指标提升"
            },
            {
                "建议内容": "建议2",
                "优先级": "中",
                "置信度": 0.6,
                "预期效果": 0.5,
                "建议类型": "异常处理"
            }
        ]
        
        # 运行计算
        overall_effect = self.generator._calculate_overall_effect(suggestions)
        
        # 验证结果
        assert "总体效果" in overall_effect
        assert "效果评估" in overall_effect
        assert "建议数量" in overall_effect
        assert overall_effect["建议数量"] == len(suggestions)
        
        # 测试空建议列表
        empty_effect = self.generator._calculate_overall_effect([])
        assert empty_effect["总体效果"] == 0.0
        assert empty_effect["效果评估"] == "无有效建议"
        assert empty_effect["建议数量"] == 0 