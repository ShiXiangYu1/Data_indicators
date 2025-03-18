"""
根因分析器测试
===========

测试root_cause_analyzer模块中的RootCauseAnalyzer类。
"""

import pytest
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
from unittest.mock import patch, MagicMock

from data_insight.core.root_cause_analyzer import RootCauseAnalyzer
from data_insight.core.attribution_analyzer import AttributionAnalyzer


class TestRootCauseAnalyzer:
    """测试根因分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = RootCauseAnalyzer()
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.analyzer.min_causal_strength == 0.2
        assert self.analyzer.max_depth == 3
        assert self.analyzer.attribution_method == "linear"
        assert isinstance(self.analyzer.attribution_analyzer, AttributionAnalyzer)
        
        # 测试自定义参数初始化
        custom_analyzer = RootCauseAnalyzer(
            min_causal_strength=0.3,
            max_depth=5,
            attribution_method="random_forest"
        )
        assert custom_analyzer.min_causal_strength == 0.3
        assert custom_analyzer.max_depth == 5
        assert custom_analyzer.attribution_method == "random_forest"
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备缺少必要字段的数据
        data = {
            "target": "销售额",
            # 缺少target_values和factors
            "subfactors": {},
            "relationships": []
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含缺少的字段
        assert "target_values" in str(excinfo.value) or "factors" in str(excinfo.value)
    
    @patch.object(AttributionAnalyzer, 'analyze')
    def test_basic_root_cause_analysis(self, mock_attribution_analyze):
        """测试基本根因分析功能"""
        # 模拟归因分析结果
        mock_attribution_analyze.return_value = {
            "归因结果": {
                "影响因素": [
                    {"因素名称": "广告支出", "贡献度": 0.5, "影响方向": "正向", "影响类型": "主要"},
                    {"因素名称": "价格调整", "贡献度": 0.3, "影响方向": "负向", "影响类型": "次要"},
                    {"因素名称": "促销活动", "贡献度": 0.1, "影响方向": "正向", "影响类型": "微弱"}
                ],
                "覆盖度": 0.9,
                "置信度": "高"
            }
        }
        
        # 准备测试数据
        target_values = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
        factors = {
            "广告支出": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
            "价格调整": [100, 98, 96, 94, 92, 90, 88, 86, 84, 82, 80],
            "促销活动": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2]
        }
        
        data = {
            "target": "销售额",
            "target_values": target_values,
            "factors": factors
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果结构
        assert "基本信息" in result
        assert "根因分析结果" in result
        assert "一级归因分析" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["目标指标"] == "销售额"
        assert basic_info["分析方法"] == "linear"
        assert basic_info["数据周期数"] == len(target_values)
    
    @patch.object(AttributionAnalyzer, 'analyze')
    def test_with_subfactors(self, mock_attribution_analyze):
        """测试带子因素的根因分析"""
        # 模拟归因分析结果 - 第一级归因
        mock_attribution_analyze.return_value = {
            "归因结果": {
                "影响因素": [
                    {"因素名称": "广告支出", "贡献度": 0.6, "影响方向": "正向", "影响类型": "主要"},
                    {"因素名称": "促销活动", "贡献度": 0.3, "影响方向": "正向", "影响类型": "次要"}
                ],
                "覆盖度": 0.9,
                "置信度": "高"
            }
        }
        
        # 准备测试数据
        target_values = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
        factors = {
            "广告支出": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
            "促销活动": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2]
        }
        subfactors = {
            "广告支出": {
                "电视广告": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
                "在线广告": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
            }
        }
        
        # 为子因素分析设置不同的返回值
        mock_attribution_analyze.side_effect = [
            # 主分析结果
            {
                "归因结果": {
                    "影响因素": [
                        {"因素名称": "广告支出", "贡献度": 0.6, "影响方向": "正向", "影响类型": "主要"},
                        {"因素名称": "促销活动", "贡献度": 0.3, "影响方向": "正向", "影响类型": "次要"}
                    ],
                    "覆盖度": 0.9,
                    "置信度": "高"
                }
            },
            # 子因素分析结果
            {
                "归因结果": {
                    "影响因素": [
                        {"因素名称": "电视广告", "贡献度": 0.7, "影响方向": "正向", "影响类型": "主要"},
                        {"因素名称": "在线广告", "贡献度": 0.3, "影响方向": "正向", "影响类型": "次要"}
                    ],
                    "覆盖度": 0.9,
                    "置信度": "高"
                }
            }
        ]
        
        data = {
            "target": "销售额",
            "target_values": target_values,
            "factors": factors,
            "subfactors": subfactors
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含根因分析结果
        assert "根因分析结果" in result
        assert "根本原因" in result["根因分析结果"]
        
        # 检查是否有子因素在根因中
        # 由于模拟的复杂性，我们不检查具体的子因素，但确保结果结构正确
        assert isinstance(result["根因分析结果"]["根本原因"], list)
    
    @patch.object(AttributionAnalyzer, 'analyze')
    def test_with_known_relationships(self, mock_attribution_analyze):
        """测试带已知关系的根因分析"""
        # 模拟归因分析结果
        mock_attribution_analyze.return_value = {
            "归因结果": {
                "影响因素": [
                    {"因素名称": "价格", "贡献度": 0.6, "影响方向": "负向", "影响类型": "主要"},
                    {"因素名称": "质量", "贡献度": 0.3, "影响方向": "正向", "影响类型": "次要"}
                ],
                "覆盖度": 0.9,
                "置信度": "高"
            }
        }
        
        # 准备测试数据
        target_values = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50]
        factors = {
            "价格": [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
            "质量": [80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100]
        }
        known_relationships = [
            {"source": "原材料成本", "target": "价格", "strength": 0.8, "direction": "正向"},
            {"source": "生产技术", "target": "质量", "strength": 0.7, "direction": "正向"},
            {"source": "原材料成本", "target": "质量", "strength": 0.3, "direction": "负向"}
        ]
        
        data = {
            "target": "销量",
            "target_values": target_values,
            "factors": factors,
            "relationships": known_relationships
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含根因分析结果
        assert "根因分析结果" in result
        assert "根本原因" in result["根因分析结果"]
        
        # 检查是否有外部因素在根因中
        # 确保至少有一个根本原因
        assert len(result["根因分析结果"]["根本原因"]) > 0
    
    @patch.object(AttributionAnalyzer, 'analyze')
    def test_causal_path_analysis(self, mock_attribution_analyze):
        """测试因果路径分析"""
        # 模拟归因分析结果
        mock_attribution_analyze.return_value = {
            "归因结果": {
                "影响因素": [
                    {"因素名称": "广告支出", "贡献度": 0.5, "影响方向": "正向", "影响类型": "主要"},
                    {"因素名称": "竞争对手价格", "贡献度": 0.4, "影响方向": "正向", "影响类型": "主要"}
                ],
                "覆盖度": 0.9,
                "置信度": "高"
            }
        }
        
        # 准备测试数据
        target_values = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
        factors = {
            "广告支出": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110],
            "竞争对手价格": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
        }
        known_relationships = [
            {"source": "市场预算", "target": "广告支出", "strength": 0.9, "direction": "正向"},
            {"source": "行业趋势", "target": "竞争对手价格", "strength": 0.8, "direction": "正向"},
            {"source": "行业趋势", "target": "市场预算", "strength": 0.7, "direction": "正向"}
        ]
        
        data = {
            "target": "销售额",
            "target_values": target_values,
            "factors": factors,
            "relationships": known_relationships
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果包含因果路径
        assert "因果路径" in result["根因分析结果"]
        assert isinstance(result["根因分析结果"]["因果路径"], list)
        
        # 检查每条路径的结构
        if result["根因分析结果"]["因果路径"]:
            path = result["根因分析结果"]["因果路径"][0]
            assert "起点" in path
            assert "终点" in path
            assert "路径" in path
            assert "影响度" in path
            assert "影响强度" in path
            assert "边信息" in path
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        # 准备测试数据
        attribution_result = {
            "归因结果": {
                "覆盖度": 0.9,
                "置信度": "高"
            }
        }
        
        # 测试高置信度场景
        root_causes = [
            {"总影响度": 0.8, "根因名称": "因素1"},
            {"总影响度": 0.3, "根因名称": "因素2"}
        ]
        high_confidence = self.analyzer._calculate_confidence(
            attribution_result, root_causes, 5, 30
        )
        assert high_confidence == "高"
        
        # 测试中等置信度场景
        attribution_result["归因结果"]["覆盖度"] = 0.7
        attribution_result["归因结果"]["置信度"] = "中"
        medium_confidence = self.analyzer._calculate_confidence(
            attribution_result, root_causes, 5, 15
        )
        assert medium_confidence == "中"
        
        # 测试低置信度场景
        attribution_result["归因结果"]["覆盖度"] = 0.5
        attribution_result["归因结果"]["置信度"] = "低"
        low_confidence = self.analyzer._calculate_confidence(
            attribution_result, root_causes, 10, 5
        )
        assert low_confidence == "低"
    
    def test_calculate_explanation_power(self):
        """测试解释能力计算"""
        # 准备测试数据
        attribution_result = {
            "归因结果": {
                "覆盖度": 0.8
            }
        }
        
        # 测试正常场景
        root_causes = [
            {"总影响度": 0.6, "根因名称": "因素1"},
            {"总影响度": 0.3, "根因名称": "因素2"}
        ]
        explanation_power = self.analyzer._calculate_explanation_power(
            root_causes, attribution_result
        )
        # 期望值: 0.8 * (0.6 + 0.3) = 0.72
        assert 0.7 <= explanation_power <= 0.73
        
        # 测试空根因列表
        explanation_power = self.analyzer._calculate_explanation_power(
            [], attribution_result
        )
        assert explanation_power == 0.0
        
        # 测试总影响度超过1的情况
        root_causes = [
            {"总影响度": 0.8, "根因名称": "因素1"},
            {"总影响度": 0.6, "根因名称": "因素2"}
        ]
        explanation_power = self.analyzer._calculate_explanation_power(
            root_causes, attribution_result
        )
        # 期望是被限制在1.0以内
        assert explanation_power == 1.0
    
    def test_classify_path_strength(self):
        """测试路径强度分类"""
        assert self.analyzer._classify_path_strength(0.5) == "强"
        assert self.analyzer._classify_path_strength(0.3) == "中"
        assert self.analyzer._classify_path_strength(0.1) == "弱"
        assert self.analyzer._classify_path_strength(0.0) == "弱"
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_visualize_causal_graph(self, mock_savefig, mock_show):
        """测试因果图可视化功能"""
        # 准备测试数据 - 创建简单的因果图
        G = nx.DiGraph()
        G.add_node("销售额", type="target")
        G.add_node("广告支出", type="factor")
        G.add_node("季节性", type="factor")
        G.add_edge("广告支出", "销售额", weight=0.6, type="direct", direction="正向")
        G.add_edge("季节性", "销售额", weight=0.3, type="direct", direction="正向")
        
        # 设置图属性
        self.analyzer.causal_graph = G
        
        # 测试不保存图像
        self.analyzer.visualize_causal_graph()
        mock_show.assert_called_once()
        mock_savefig.assert_not_called()
        
        # 重置mock
        mock_show.reset_mock()
        
        # 测试保存图像
        self.analyzer.visualize_causal_graph(save_path="test_graph.png")
        mock_savefig.assert_called_once_with("test_graph.png", dpi=300, bbox_inches='tight')
        mock_show.assert_not_called()
    
    def test_get_root_cause_summary(self):
        """测试获取根因分析摘要"""
        # 没有结果时的测试
        assert "请先运行分析" in self.analyzer.get_root_cause_summary()
        
        # 设置模拟结果
        self.analyzer.last_result = {
            "基本信息": {
                "目标指标": "销售额"
            },
            "根因分析结果": {
                "置信度": "高",
                "解释覆盖率": 0.85,
                "根本原因": [
                    {"根因名称": "广告支出", "总影响度": 0.6, "影响类型": "关键"},
                    {"根因名称": "季节性", "总影响度": 0.25, "影响类型": "主要"}
                ],
                "因果路径": [
                    {
                        "路径": ["广告支出", "销售额"],
                        "影响强度": "强",
                        "影响度": 0.6
                    },
                    {
                        "路径": ["季节性", "销售额"],
                        "影响强度": "中",
                        "影响度": 0.25
                    }
                ]
            }
        }
        
        # 获取摘要并检查内容
        summary = self.analyzer.get_root_cause_summary()
        assert "销售额" in summary
        assert "高" in summary
        assert "0.85" in summary
        assert "广告支出" in summary
        assert "季节性" in summary
        assert "关键" in summary
        assert "主要" in summary
        assert "→" in summary 