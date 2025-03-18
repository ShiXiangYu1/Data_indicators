#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本生成器测试
===========

测试text_generator模块中的TextGenerator类。
"""

import pytest
from data_insight.core.text_generator import TextGenerator


class TestTextGenerator:
    """测试文本生成器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化生成器"""
        self.generator = TextGenerator()
    
    def test_generate_text_with_basic_analysis(self):
        """测试基础分析结果的文本生成"""
        # 准备简单分析结果
        analysis_result = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月",
                "正向增长是否为好": True
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
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证结果包含必要信息
        assert "销售额" in result
        assert "120元" in result or "120" in result
        assert "100元" in result or "100" in result
        assert "20%" in result or "20" in result
        assert "增加" in result or "增长" in result
        assert "2023年7月" in result or "7月" in result
        assert "2023年6月" in result or "6月" in result
    
    def test_generate_text_with_anomaly(self):
        """测试带异常分析的文本生成"""
        # 准备带异常的分析结果
        analysis_result = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 200,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月",
                "正向增长是否为好": True
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
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证结果包含异常信息
        assert "销售额" in result
        assert "200元" in result or "200" in result
        assert "100元" in result or "100" in result
        assert "100%" in result or "100" in result
        assert "大幅" in result or "显著" in result
        assert any(term in result for term in ["异常", "高于", "超出"])
    
    def test_generate_text_with_trend(self):
        """测试带趋势分析的文本生成"""
        # 准备带趋势的分析结果
        analysis_result = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 120,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月",
                "正向增长是否为好": True
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
            "趋势分析": {
                "趋势类型": "上升",
                "趋势强度": 0.08
            }
        }
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证结果包含趋势信息
        assert "销售额" in result
        assert "上升" in result or "增长" in result
        assert any(term in result for term in ["趋势", "历史", "整体"])
    
    def test_generate_text_with_negative_change(self):
        """测试负向变化的文本生成"""
        # 准备负向变化的分析结果
        analysis_result = {
            "基本信息": {
                "指标名称": "销售额",
                "当前值": 80,
                "上一期值": 100,
                "单位": "元",
                "当前周期": "2023年7月",
                "上一周期": "2023年6月",
                "正向增长是否为好": True
            },
            "变化分析": {
                "变化量": -20,
                "变化率": -0.2,
                "变化类别": "下降",
                "变化方向": "减少"
            },
            "异常分析": {
                "是否异常": False,
                "异常程度": 0.0,
                "是否高于正常范围": None
            }
        }
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证结果包含负向变化信息
        assert "销售额" in result
        assert "80元" in result or "80" in result
        assert "100元" in result or "100" in result
        assert "20%" in result or "20" in result
        assert "下降" in result or "减少" in result
        assert any(term in result for term in ["警惕", "关注", "不佳", "负面"])
    
    def test_generate_text_unknown_type(self):
        """测试未知类型分析结果的处理"""
        # 准备不符合格式的分析结果
        analysis_result = {
            "some_key": "some_value"
        }
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证返回了未知类型提示
        assert "无法识别" in result
    
    def test_format_error_handling(self):
        """测试格式错误处理"""
        # 准备缺少关键字段的分析结果
        analysis_result = {
            "基本信息": {
                "指标名称": "销售额",
                # 缺少当前值和上一期值
                "单位": "元"
            },
            "变化分析": {
                "变化量": 20,
                "变化率": 0.2,
                "变化类别": "增长"
                # 缺少变化方向
            }
        }
        
        # 生成文本
        result = self.generator.generate_text(analysis_result)
        
        # 验证返回了错误提示
        assert "缺少必要的模板参数" in result 