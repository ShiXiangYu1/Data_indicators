#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web界面测试模块
=============

测试Web界面的各个视图函数。
"""

import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from data_insight.app import app
from data_insight.web.views import register_web_views

class TestWebViews(unittest.TestCase):
    """Web界面视图测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.client = TestClient(app)
    
    def test_index_page(self):
        """测试首页"""
        response = self.client.get("/web/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("数据指标分析系统", response.text)
        self.assertIn("欢迎使用", response.text)
    
    def test_dashboard_page(self):
        """测试仪表盘页面"""
        response = self.client.get("/web/dashboard")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("仪表盘", response.text)
        self.assertIn("系统概览", response.text)
    
    def test_trend_analysis_page(self):
        """测试趋势分析页面"""
        response = self.client.get("/web/trend-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("趋势分析", response.text)
        self.assertIn("数据上传", response.text)
    
    def test_correlation_analysis_page(self):
        """测试相关性分析页面"""
        response = self.client.get("/web/correlation-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("相关性分析", response.text)
        self.assertIn("指标选择", response.text)
    
    def test_attribution_analysis_page(self):
        """测试归因分析页面"""
        response = self.client.get("/web/attribution-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("归因分析", response.text)
        self.assertIn("因素选择", response.text)
    
    def test_reason_analysis_page(self):
        """测试原因分析页面"""
        response = self.client.get("/web/reason-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("原因分析", response.text)
        self.assertIn("分析配置", response.text)
    
    def test_root_cause_analysis_page(self):
        """测试根因分析页面"""
        response = self.client.get("/web/root-cause-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("根因分析", response.text)
        self.assertIn("指标变化", response.text)
    
    def test_prediction_analysis_page(self):
        """测试预测分析页面"""
        response = self.client.get("/web/prediction-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("预测分析", response.text)
        self.assertIn("历史数据", response.text)
    
    def test_metric_analysis_page(self):
        """测试指标分析页面"""
        response = self.client.get("/web/metric-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("指标分析", response.text)
        self.assertIn("指标选择", response.text)
    
    def test_chart_analysis_page(self):
        """测试图表分析页面"""
        response = self.client.get("/web/chart-analysis")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("图表分析", response.text)
        self.assertIn("图表上传", response.text)
    
    def test_export_page(self):
        """测试导出页面"""
        response = self.client.get("/web/export")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("结果导出", response.text)
        self.assertIn("导出格式", response.text)
    
    def test_api_documentation_page(self):
        """测试API文档页面"""
        response = self.client.get("/web/api-documentation")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("API文档", response.text)
        self.assertIn("接口说明", response.text)
    
    def test_user_guide_page(self):
        """测试用户指南页面"""
        response = self.client.get("/web/user-guide")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("用户指南", response.text)
        self.assertIn("使用方法", response.text)
    
    @patch('data_insight.web.views.render_template')
    def test_template_rendering(self, mock_render):
        """测试模板渲染"""
        mock_render.return_value = "<html>模拟的HTML内容</html>"
        
        self.client.get("/web/")
        mock_render.assert_called_once()
        
        # 重置模拟对象
        mock_render.reset_mock()
        
        self.client.get("/web/dashboard")
        mock_render.assert_called_once()
    
    def test_page_not_found(self):
        """测试404页面"""
        response = self.client.get("/web/non-existent-page")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('data_insight.web.views.render_template')
    def test_error_handling(self, mock_render):
        """测试错误处理"""
        # 模拟render_template抛出异常
        mock_render.side_effect = Exception("模板渲染错误")
        
        response = self.client.get("/web/")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestWebTemplates(unittest.TestCase):
    """Web模板测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.client = TestClient(app)
    
    def test_base_template_components(self):
        """测试基础模板组件"""
        response = self.client.get("/web/")
        
        # 检查导航菜单
        self.assertIn("首页", response.text)
        self.assertIn("分析", response.text)
        self.assertIn("报告", response.text)
        
        # 检查页脚
        self.assertIn("版权所有", response.text)
        self.assertIn("数据指标分析系统", response.text)
    
    def test_dashboard_components(self):
        """测试仪表盘组件"""
        response = self.client.get("/web/dashboard")
        
        # 检查仪表盘组件
        self.assertIn("系统状态", response.text)
        self.assertIn("最近分析", response.text)
        self.assertIn("常用功能", response.text)
    
    def test_analysis_form_components(self):
        """测试分析表单组件"""
        # 测试趋势分析表单
        response = self.client.get("/web/trend-analysis")
        self.assertIn("数据上传", response.text)
        self.assertIn("分析参数", response.text)
        self.assertIn("提交", response.text)
        
        # 测试相关性分析表单
        response = self.client.get("/web/correlation-analysis")
        self.assertIn("指标选择", response.text)
        self.assertIn("相关性方法", response.text)
        self.assertIn("提交", response.text)


class TestWebFunctionality(unittest.TestCase):
    """Web功能测试类"""
    
    @patch('data_insight.web.views.render_template')
    @patch('data_insight.core.trend_analyzer.TrendAnalyzer.analyze')
    def test_trend_analysis_submission(self, mock_analyze, mock_render):
        """测试趋势分析表单提交"""
        client = TestClient(app)
        
        # 模拟分析结果
        mock_analyze.return_value = {
            "trend_type": "increasing",
            "trend_values": [1, 2, 3, 4, 5],
            "seasonality": False,
            "inflection_points": []
        }
        
        # 提交表单
        response = client.post(
            "/web/trend-analysis/submit",
            json={
                "values": [1, 2, 3, 4, 5],
                "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
                "trend_method": "linear"
            }
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_analyze.assert_called_once()
    
    @patch('data_insight.web.views.render_template')
    def test_export_functionality(self, mock_render):
        """测试导出功能"""
        client = TestClient(app)
        
        # 提交导出请求
        response = client.post(
            "/web/export/submit",
            json={
                "format": "csv",
                "data": {"values": [1, 2, 3], "labels": ["A", "B", "C"]},
                "filename": "test_export"
            }
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("下载链接", response.text)


if __name__ == '__main__':
    unittest.main() 