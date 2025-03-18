#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
行动建议生成器测试
==============

测试action_suggester模块中的ActionSuggester类。
"""

import pytest
from unittest.mock import patch, MagicMock
from data_insight.core.action_suggester import ActionSuggester


class TestActionSuggester:
    """测试行动建议生成器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化行动建议生成器"""
        # 禁用LLM以便测试
        self.suggester = ActionSuggester(use_llm=False)
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.suggester is not None
        assert self.suggester.use_llm is False
        assert hasattr(self.suggester, 'improvement_actions')
        assert hasattr(self.suggester, 'cost_optimization_actions')
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备测试数据 - 缺少basic_info字段
        input_data = {
            "change_analysis": {"变化方向": "增加", "变化率": 0.2, "变化类别": "增长"}
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.suggester.analyze(input_data)
        
        # 验证异常消息包含缺少的字段
        assert "basic_info" in str(excinfo.value)
    
    def test_sales_metric_positive_change(self):
        """测试销售类指标正向变化的行动建议"""
        # 准备测试数据
        input_data = {
            "basic_info": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "万元",
                "正向增长是否为好": True
            },
            "change_analysis": {
                "变化方向": "增加",
                "变化率": 0.2,
                "变化类别": "增长"
            }
        }
        
        # 获取行动建议
        result = self.suggester.analyze(input_data)
        
        # 验证结果
        assert "行动建议" in result
        assert "建议列表" in result["行动建议"]
        assert isinstance(result["行动建议"]["建议列表"], list)
        assert len(result["行动建议"]["建议列表"]) > 0
        
        # 验证建议内容和优先级
        assert "生成方法" in result["行动建议"]
        assert result["行动建议"]["生成方法"] == "模板匹配"
        assert "优先级排序" in result["行动建议"]
        assert isinstance(result["行动建议"]["优先级排序"], list)
        assert len(result["行动建议"]["优先级排序"]) == len(result["行动建议"]["建议列表"])
    
    def test_cost_metric_negative_change(self):
        """测试成本类指标负向变化的行动建议"""
        # 准备测试数据
        input_data = {
            "basic_info": {
                "指标名称": "运营成本",
                "当前值": 120,
                "上一期值": 100,
                "单位": "万元",
                "正向增长是否为好": False
            },
            "change_analysis": {
                "变化方向": "增加",
                "变化率": 0.2,
                "变化类别": "增长"
            }
        }
        
        # 获取行动建议
        result = self.suggester.analyze(input_data)
        
        # 验证结果
        assert "行动建议" in result
        assert "建议列表" in result["行动建议"]
        assert len(result["行动建议"]["建议列表"]) > 0
        
        # 验证包含"优先行动"标记，因为成本增加是不好的
        suggestions = result["行动建议"]["建议列表"]
        assert any("优先行动" in suggestion for suggestion in suggestions)
    
    def test_quality_metric(self):
        """测试质量类指标的行动建议"""
        # 准备测试数据
        input_data = {
            "basic_info": {
                "指标名称": "用户满意度",
                "当前值": 4.2,
                "上一期值": 4.5,
                "单位": "分",
                "正向增长是否为好": True
            },
            "change_analysis": {
                "变化方向": "减少",
                "变化率": -0.067,
                "变化类别": "轻微下降"
            }
        }
        
        # 获取行动建议
        result = self.suggester.analyze(input_data)
        
        # 验证结果
        assert "行动建议" in result
        assert len(result["行动建议"]["建议列表"]) > 0
        
        # 验证建议与质量/满意度相关
        suggestions = result["行动建议"]["建议列表"]
        assert any("优先行动" in suggestion for suggestion in suggestions)
        
        # 验证优先级排序
        priorities = result["行动建议"]["优先级排序"]
        assert len(priorities) > 0
        for action, priority in priorities:
            assert priority in ["高", "中", "低"]
    
    def test_reason_based_actions(self):
        """测试基于原因分析的行动建议"""
        # 准备测试数据
        input_data = {
            "basic_info": {
                "指标名称": "销售额",
                "当前值": 80,
                "上一期值": 100,
                "单位": "万元",
                "正向增长是否为好": True
            },
            "change_analysis": {
                "变化方向": "减少",
                "变化率": -0.2,
                "变化类别": "下降"
            },
            "reason_analysis": {
                "可能原因": [
                    "市场竞争加剧，份额被竞争对手抢占",
                    "产品老化，缺乏创新",
                    "价格策略不当，失去价格竞争力"
                ]
            }
        }
        
        # 获取行动建议
        result = self.suggester.analyze(input_data)
        
        # 验证结果
        assert "行动建议" in result
        assert len(result["行动建议"]["建议列表"]) > 0
        
        # 验证建议与原因相关
        suggestions = result["行动建议"]["建议列表"]
        reason_texts = input_data["reason_analysis"]["可能原因"]
        
        # 至少有一条建议应该与原因直接相关
        assert any(reason in suggestion for reason in reason_texts for suggestion in suggestions)
    
    def test_prioritize_actions(self):
        """测试行动建议优先级排序"""
        # 准备测试数据
        actions = [
            "【优先行动】优化营销策略，针对目标客户群体进行精准投放",
            "完善产品功能，提高产品竞争力",
            "【持续优化】调整定价策略，寻找最优价格点"
        ]
        
        basic_info = {
            "指标名称": "销售额",
            "当前值": 80,
            "上一期值": 100,
            "正向增长是否为好": True
        }
        
        change_analysis = {
            "变化方向": "减少",
            "变化率": -0.2,
            "变化类别": "下降"
        }
        
        # 执行优先级排序
        result = self.suggester._prioritize_actions(actions, basic_info, change_analysis)
        
        # 验证结果
        assert len(result) == 3
        
        # 验证优先级分配
        for action, priority in result:
            if "优化营销策略" in action:
                assert priority == "高"  # 标记为【优先行动】的应该是高优先级
            elif "调整定价策略" in action:
                assert priority == "中"  # 标记为【持续优化】的应该是中优先级
    
    @patch('data_insight.core.action_suggester.OpenAI')
    @patch('data_insight.core.action_suggester.LLMChain')
    def test_llm_actions_generation(self, mock_llm_chain, mock_openai):
        """测试LLM生成行动建议"""
        # 设置环境变量模拟
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            # 设置LLM的模拟返回
            mock_chain_instance = MagicMock()
            mock_chain_instance.run.return_value = """
            建议：优化产品设计，提升核心竞争力，以应对市场竞争加剧的情况。
            
            建议：重新评估定价策略，确保价格与价值匹配，提高产品性价比。
            
            建议：加强客户关系管理，提升客户忠诚度，减少客户流失。
            """
            mock_llm_chain.return_value = mock_chain_instance
            
            # 创建带LLM的行动建议生成器
            suggester = ActionSuggester(use_llm=True)
            suggester.init_llm()
            
            # 准备测试数据
            input_data = {
                "basic_info": {
                    "指标名称": "销售额",
                    "当前值": 80,
                    "上一期值": 100,
                    "单位": "万元",
                    "正向增长是否为好": True
                },
                "change_analysis": {
                    "变化方向": "减少",
                    "变化率": -0.2,
                    "变化类别": "下降"
                },
                "reason_analysis": {
                    "可能原因": ["市场竞争加剧"]
                }
            }
            
            # 获取行动建议
            result = suggester.analyze(input_data)
            
            # 验证LLM被调用
            assert mock_chain_instance.run.called
            
            # 验证结果包含LLM生成的建议
            assert "行动建议" in result
            assert len(result["行动建议"]["建议列表"]) >= 3
            assert "生成方法" in result["行动建议"]
            assert "LLM增强" in result["行动建议"]["生成方法"]
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        # 测试文本
        text = "市场竞争加剧，产品定价过高，营销策略不当"
        
        # 提取关键词
        keywords = self.suggester._extract_keywords(text)
        
        # 验证提取结果
        assert "营销" in keywords
        assert "定价" in keywords
        assert "市场" in keywords
        assert "竞争" in keywords
        assert len(keywords) >= 3 