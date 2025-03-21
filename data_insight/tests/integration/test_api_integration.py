"""
API集成测试
========

测试数据指标平台的API端点是否正常工作。
"""

import unittest
import json
import os
import sys
from unittest.mock import patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_insight.api import create_app

class APIIntegrationTest(unittest.TestCase):
    """API集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试客户端
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()
        
        # 准备测试数据
        self.metric_data = {
            "metric_data": {
                "name": "月度销售额",
                "value": 1250000,
                "previous_value": 1000000,
                "unit": "元",
                "time_period": "2023年7月",
                "previous_time_period": "2023年6月",
                "historical_values": [920000, 980000, 950000, 1010000, 1000000]
            }
        }
        
        self.chart_data = {
            "chart_data": {
                "title": "2023年月度销售趋势",
                "type": "line",
                "data": {
                    "x": ["1月", "2月", "3月", "4月", "5月", "6月", "7月"],
                    "y": [920000, 980000, 950000, 1010000, 1000000, 1100000, 1250000]
                },
                "x_label": "月份",
                "y_label": "销售额（元）"
            },
            "chart_type": "line"
        }
        
        self.metrics_comparison_data = {
            "metrics": [
                {
                    "name": "2022年销售额",
                    "value": 980000,
                    "previous_value": 920000,
                    "unit": "元",
                    "time_period": "2022年7月",
                    "previous_time_period": "2022年6月",
                    "metric_id": "sales_2022_07"
                },
                {
                    "name": "2023年销售额",
                    "value": 1250000,
                    "previous_value": 1100000,
                    "unit": "元",
                    "time_period": "2023年7月",
                    "previous_time_period": "2023年6月",
                    "metric_id": "sales_2023_07"
                }
            ],
            "comparison_type": "general"
        }
        
        self.metrics_correlation_data = {
            "metrics": [
                {
                    "name": "销售额",
                    "value": 1250000,
                    "historical_values": [920000, 980000, 950000, 1010000, 1000000, 1100000, 1250000],
                    "metric_id": "sales"
                },
                {
                    "name": "广告支出",
                    "value": 250000,
                    "historical_values": [180000, 190000, 185000, 200000, 195000, 220000, 250000],
                    "metric_id": "ad_spend"
                }
            ]
        }
        
        self.charts_comparison_data = {
            "charts": [
                {
                    "chart_data": {
                        "title": "2022年销售趋势",
                        "type": "line",
                        "data": {
                            "x": ["1月", "2月", "3月", "4月", "5月", "6月"],
                            "y": [850000, 900000, 880000, 920000, 950000, 980000]
                        }
                    },
                    "chart_type": "line",
                    "chart_id": "sales_2022"
                },
                {
                    "chart_data": {
                        "title": "2023年销售趋势",
                        "type": "line",
                        "data": {
                            "x": ["1月", "2月", "3月", "4月", "5月", "6月"],
                            "y": [920000, 980000, 950000, 1010000, 1000000, 1100000]
                        }
                    },
                    "chart_type": "line",
                    "chart_id": "sales_2023"
                }
            ]
        }
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('version', data)
    
    @patch('data_insight.services.metric_service.MetricService.analyze_metric')
    def test_metric_analyze(self, mock_analyze):
        """测试指标分析API"""
        # 模拟服务返回结果
        mock_analyze.return_value = {
            "analysis": {"指标名称": "月度销售额", "当前值": 1250000, "环比变化": 25.0},
            "insight": "月度销售额为1,250,000元，环比增长25.0%，呈现明显上升趋势。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/metric/analyze',
            data=json.dumps(self.metric_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_analyze.assert_called_once()
    
    @patch('data_insight.services.metric_service.MetricService.predict_metric')
    def test_metric_predict(self, mock_predict):
        """测试指标预测API"""
        # 模拟服务返回结果
        mock_predict.return_value = {
            "prediction": {
                "指标名称": "月度销售额",
                "预测值": [1300000, 1350000, 1400000],
                "置信区间": [[1250000, 1350000], [1280000, 1420000], [1300000, 1500000]]
            },
            "insight": "预计未来3个月销售额将持续增长，7月预计达到130万元，8月预计达到135万元，9月预计达到140万元。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/metric/predict',
            data=json.dumps(self.metric_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('prediction', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_predict.assert_called_once()
    
    @patch('data_insight.services.metric_service.MetricService.compare_metrics')
    def test_metric_compare(self, mock_compare):
        """测试指标对比API"""
        # 模拟服务返回结果
        mock_compare.return_value = {
            "analysis": {
                "对比结果": "2023年销售额高于2022年销售额",
                "增长率": 27.55
            },
            "insight": "2023年7月销售额比2022年7月增长了27.55%，增长显著。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/metric/compare',
            data=json.dumps(self.metrics_comparison_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_compare.assert_called_once()
    
    @patch('data_insight.services.metric_service.MetricService.compare_metrics')
    def test_metric_correlation(self, mock_correlation):
        """测试指标相关性API"""
        # 模拟服务返回结果
        mock_correlation.return_value = {
            "analysis": {
                "相关系数": 0.95,
                "相关强度": "强相关",
                "相关方向": "正相关"
            },
            "insight": "销售额与广告支出存在强烈的正相关关系(相关系数0.95)，广告支出增加通常伴随着销售额的增加。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/metric/correlation',
            data=json.dumps(self.metrics_correlation_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_correlation.assert_called_once()
    
    @patch('data_insight.services.chart_service.ChartService.analyze_chart')
    def test_chart_analyze(self, mock_analyze):
        """测试图表分析API"""
        # 模拟服务返回结果
        mock_analyze.return_value = {
            "analysis": {
                "图表类型": "折线图",
                "趋势": "上升",
                "波动性": "中等"
            },
            "insight": "销售额整体呈上升趋势，6月和7月增长较为显著，7月达到最高点125万元。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/chart/analyze',
            data=json.dumps(self.chart_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_analyze.assert_called_once()
    
    @patch('data_insight.services.chart_service.ChartService.compare_charts')
    def test_chart_compare(self, mock_compare):
        """测试图表对比API"""
        # 模拟服务返回结果
        mock_compare.return_value = {
            "analysis": {
                "对比结果": "2023年销售额整体高于2022年",
                "差异最大月份": "6月",
                "增长趋势": "相似"
            },
            "insight": "2023年销售额整体高于2022年同期，两年的增长趋势相似，但2023年6月的增长幅度明显大于2022年6月。"
        }
        
        # 发送请求
        response = self.client.post(
            '/api/chart/compare',
            data=json.dumps(self.charts_comparison_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', data)
        self.assertIn('insight', data)
        
        # 验证服务是否被正确调用
        mock_compare.assert_called_once()
    
    def test_metric_validation_error(self):
        """测试指标数据验证错误处理"""
        # 准备无效数据 - 缺少必要字段
        invalid_data = {
            "metric_data": {
                "name": "月度销售额"
                # 缺少value字段
            }
        }
        
        # 发送请求
        response = self.client.post(
            '/api/metric/analyze',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证错误响应
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_missing_required_field(self):
        """测试缺少必要请求字段的错误处理"""
        # 准备无效请求 - 缺少必要字段
        invalid_request = {}
        
        # 发送请求
        response = self.client.post(
            '/api/metric/analyze',
            data=json.dumps(invalid_request),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证错误响应
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('缺少必需字段', data['error'])
    
    def test_invalid_json(self):
        """测试无效JSON的错误处理"""
        # 发送无效JSON
        response = self.client.post(
            '/api/metric/analyze',
            data='这不是有效的JSON',
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # 验证错误响应
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_not_found(self):
        """测试404错误处理"""
        # 访问不存在的端点
        response = self.client.get('/api/not_exists')
        data = json.loads(response.data)
        
        # 验证错误响应
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], '资源不存在')

if __name__ == '__main__':
    unittest.main() 