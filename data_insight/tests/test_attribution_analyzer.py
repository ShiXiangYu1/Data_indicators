"""
归因分析器测试
===========

测试attribution_analyzer模块中的AttributionAnalyzer类。
"""

import pytest
import numpy as np
import pandas as pd
from data_insight.core.attribution_analyzer import AttributionAnalyzer


class TestAttributionAnalyzer:
    """测试归因分析器类"""
    
    def setup_method(self):
        """每个测试方法前运行，初始化分析器"""
        self.analyzer = AttributionAnalyzer()
    
    def test_basic_initialization(self):
        """测试基本初始化"""
        assert self.analyzer.method == "linear"
        assert self.analyzer.min_correlation == 0.3
        assert self.analyzer.max_factors == 5
        
        # 测试自定义参数初始化
        custom_analyzer = AttributionAnalyzer(
            method="random_forest", 
            min_correlation=0.5, 
            max_factors=3
        )
        assert custom_analyzer.method == "random_forest"
        assert custom_analyzer.min_correlation == 0.5
        assert custom_analyzer.max_factors == 3
    
    def test_missing_required_field(self):
        """测试缺少必要字段"""
        # 准备缺少必要字段的数据
        data = {
            "target": "销售额",
            "factors": {"广告支出": [100, 150, 200]}
            # 缺少target_values
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含缺少的字段
        assert "target_values" in str(excinfo.value)
    
    def test_inconsistent_data_length(self):
        """测试数据长度不一致的情况"""
        # 准备数据长度不一致的测试数据
        data = {
            "target": "销售额",
            "target_values": [1000, 1100, 1200, 1300],
            "factors": {
                "广告支出": [100, 150, 200]  # 长度与target_values不一致
            }
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含不一致的提示
        assert "广告支出" in str(excinfo.value)
        assert "数据长度" in str(excinfo.value)
    
    def test_unsupported_method(self):
        """测试不支持的归因方法"""
        # 准备使用不支持方法的测试数据
        data = {
            "target": "销售额",
            "target_values": [1000, 1100, 1200, 1300],
            "factors": {
                "广告支出": [100, 150, 200, 250]
            },
            "method": "unsupported_method"  # 不支持的方法
        }
        
        # 验证异常
        with pytest.raises(ValueError) as excinfo:
            self.analyzer.analyze(data)
        
        # 验证异常消息包含方法不支持的提示
        assert "不支持的归因方法" in str(excinfo.value)
    
    def test_linear_attribution(self):
        """测试线性归因分析"""
        # 准备线性相关数据
        # 销售额与广告支出呈正相关，与竞品价格呈负相关
        sales = [1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450]
        ad_spend = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
        competitor_price = [50, 48, 46, 44, 42, 40, 38, 36, 34, 32]
        
        data = {
            "target": "销售额",
            "target_values": sales,
            "factors": {
                "广告支出": ad_spend,
                "竞品价格": competitor_price
            }
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果结构
        assert "基本信息" in result
        assert "归因结果" in result
        assert "相关性分析" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["目标指标"] == "销售额"
        assert basic_info["分析方法"] == "linear"
        assert basic_info["数据周期数"] == 10
        
        # 验证归因结果
        attribution_result = result["归因结果"]
        assert "影响因素" in attribution_result
        assert "覆盖度" in attribution_result
        assert "置信度" in attribution_result
        
        # 验证影响因素
        factors = attribution_result["影响因素"]
        assert len(factors) <= 2  # 不超过2个因素
        
        # 验证影响方向
        factor_directions = {factor["因素名称"]: factor["影响方向"] for factor in factors}
        
        # 验证广告支出对销售额的影响为正向
        if "广告支出" in factor_directions:
            assert factor_directions["广告支出"] == "正向"
        
        # 验证竞品价格对销售额的影响为负向
        if "竞品价格" in factor_directions:
            assert factor_directions["竞品价格"] == "负向"
    
    def test_random_forest_attribution(self):
        """测试随机森林归因分析"""
        # 准备复杂非线性相关数据
        np.random.seed(42)
        n = 50
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.normal(0, 1, n)
        x3 = np.random.normal(0, 1, n)
        
        # 创建非线性关系 (y = x1^2 + sin(x2) + x3 + 噪声)
        y = x1**2 + np.sin(x2) + x3 + np.random.normal(0, 0.1, n)
        
        data = {
            "target": "非线性指标",
            "target_values": y.tolist(),
            "factors": {
                "因素1": x1.tolist(),
                "因素2": x2.tolist(),
                "因素3": x3.tolist()
            },
            "method": "random_forest"
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果结构
        assert "基本信息" in result
        assert "归因结果" in result
        
        # 验证基本信息
        basic_info = result["基本信息"]
        assert basic_info["目标指标"] == "非线性指标"
        assert basic_info["分析方法"] == "random_forest"
        
        # 验证归因结果
        attribution_result = result["归因结果"]
        assert "影响因素" in attribution_result
        assert "覆盖度" in attribution_result
        assert attribution_result["覆盖度"] > 0.5  # 随机森林应该能解释超过50%的方差
    
    def test_no_correlation(self):
        """测试无相关性的情况"""
        # 准备无相关性数据
        np.random.seed(42)
        n = 20
        target_values = np.random.normal(0, 1, n).tolist()
        factor1 = np.random.normal(0, 1, n).tolist()
        factor2 = np.random.normal(0, 1, n).tolist()
        
        data = {
            "target": "随机指标",
            "target_values": target_values,
            "factors": {
                "随机因素1": factor1,
                "随机因素2": factor2
            },
            "min_correlation": 0.5  # 设置较高的相关系数阈值
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证结果
        attribution_result = result["归因结果"]
        assert len(attribution_result["影响因素"]) == 0  # 应该没有足够相关的因素
        assert attribution_result["覆盖度"] == 0.0  # 解释方差应该接近0
    
    def test_time_series_analysis(self):
        """测试时间序列分析功能"""
        # 准备带时间周期的测试数据
        sales = [1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450]
        ad_spend = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
        time_periods = [f"2023年{i+1}月" for i in range(10)]
        
        data = {
            "target": "销售额",
            "target_values": sales,
            "factors": {"广告支出": ad_spend},
            "time_periods": time_periods,
            "current_period": "2023年10月"
        }
        
        # 运行分析
        result = self.analyzer.analyze(data)
        
        # 验证时间序列分析结果
        assert "时间序列分析" in result
        time_series = result["时间序列分析"]
        assert "时间周期" in time_series
        assert "目标指标" in time_series
        assert "主要影响因素" in time_series
        assert len(time_series["时间周期"]) == 10
        assert len(time_series["目标指标"]) == 10
    
    def test_classify_attributions(self):
        """测试归因结果分类功能"""
        # 创建一个测试用的归因结果字典
        attribution_result = {
            "attributions": {
                "主要因素": {"贡献度": 0.6, "方向": "正向"},
                "重要因素": {"贡献度": 0.35, "方向": "负向"},
                "次要因素": {"贡献度": 0.15, "方向": "正向"},
                "微弱因素": {"贡献度": 0.05, "方向": "负向"}
            },
            "total_explained": 0.85
        }
        
        # 使用反射访问私有方法进行测试
        classified = self.analyzer._classify_attributions(attribution_result)
        
        # 验证分类结果
        assert len(classified) == 4
        
        # 按贡献度排序
        classified_sorted = sorted(classified, key=lambda x: x["贡献度"], reverse=True)
        
        # 验证各因素的分类是否正确
        assert classified_sorted[0]["因素名称"] == "主要因素"
        assert classified_sorted[0]["影响类型"] == "主要"
        
        assert classified_sorted[1]["因素名称"] == "重要因素"
        assert classified_sorted[1]["影响类型"] == "重要"
        
        assert classified_sorted[2]["因素名称"] == "次要因素"
        assert classified_sorted[2]["影响类型"] == "次要"
        
        assert classified_sorted[3]["因素名称"] == "微弱因素"
        assert classified_sorted[3]["影响类型"] == "微弱"
    
    def test_calculate_confidence(self):
        """测试置信度计算功能"""
        # 创建一个测试用的DataFrame
        df = pd.DataFrame({
            "factor1": range(50),
            "factor2": range(50),
            "target": range(50)
        })
        
        # 创建高解释度的归因结果
        high_attribution = {
            "attributions": {"factor1": {}, "factor2": {}, "factor3": {}},
            "total_explained": 0.8
        }
        
        # 创建中等解释度的归因结果
        medium_attribution = {
            "attributions": {"factor1": {}, "factor2": {}},
            "total_explained": 0.6
        }
        
        # 创建低解释度的归因结果
        low_attribution = {
            "attributions": {"factor1": {}},
            "total_explained": 0.3
        }
        
        # 创建数据点很少的情况
        few_points_df = pd.DataFrame({
            "factor1": range(5),
            "target": range(5)
        })
        
        processed_data = {"df": df}
        few_points_data = {"df": few_points_df}
        
        # 使用反射访问私有方法进行测试
        high_conf = self.analyzer._calculate_confidence(high_attribution, processed_data)
        medium_conf = self.analyzer._calculate_confidence(medium_attribution, processed_data)
        low_conf = self.analyzer._calculate_confidence(low_attribution, processed_data)
        few_points_conf = self.analyzer._calculate_confidence(high_attribution, few_points_data)
        
        # 验证置信度评估结果
        assert high_conf == "高"
        assert medium_conf == "中"
        assert low_conf == "低"
        assert few_points_conf == "低"  # 无论解释度多高，数据点太少都应该是低置信度 