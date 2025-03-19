#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
端到端API流程测试模块
=================

测试数据指标分析系统API的完整工作流程。
"""

import unittest
import json
import os
import time
from fastapi.testclient import TestClient
from fastapi import status

from data_insight.app import app


class TestE2EApiFlow(unittest.TestCase):
    """端到端API流程测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.client = TestClient(app)
        cls.api_token = os.environ.get("TEST_API_TOKEN", "test-token-for-e2e-tests")
        cls.headers = {
            "Content-Type": "application/json",
            "X-API-Token": cls.api_token
        }
        # 测试数据
        cls.test_data = {
            "metric_name": "用户增长率",
            "values": [1.2, 1.5, 1.7, 2.0, 2.3, 2.7, 3.1, 3.5, 3.8, 4.2],
            "timestamps": [
                "2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", 
                "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"
            ]
        }
        # 存储测试中生成的资源ID
        cls.test_resources = {}
    
    @classmethod
    def tearDownClass(cls):
        """测试完成后清理资源"""
        # 清理测试中创建的临时文件
        if cls.test_resources.get("export_file") and os.path.exists(cls.test_resources["export_file"]):
            try:
                os.remove(cls.test_resources["export_file"])
            except:
                pass
    
    def test_001_health_check(self):
        """测试健康检查接口"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["api_service"], "healthy")
    
    def test_002_trend_analysis(self):
        """测试趋势分析接口"""
        # 准备请求数据
        request_data = self.test_data.copy()
        request_data["trend_method"] = "linear"
        request_data["detect_seasonality"] = True
        
        # 发送请求
        response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertEqual(result["metric_name"], request_data["metric_name"])
        self.assertEqual(result["trend"]["trend_type"], "increasing")
        self.assertEqual(len(result["trend"]["trend_values"]), len(request_data["values"]))
        self.assertIn("summary", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["trend_analysis"] = result
    
    def test_003_correlation_analysis(self):
        """测试相关性分析接口"""
        # 准备请求数据
        request_data = {
            "primary_metric": {
                "name": "用户增长率",
                "values": [1.2, 1.5, 1.7, 2.0, 2.3, 2.7, 3.1, 3.5, 3.8, 4.2],
                "timestamps": [
                    "2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", 
                    "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"
                ]
            },
            "secondary_metrics": [
                {
                    "name": "营销支出",
                    "values": [5.0, 5.5, 6.0, 6.2, 6.5, 6.8, 7.0, 7.5, 8.0, 8.5],
                    "timestamps": [
                        "2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", 
                        "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"
                    ]
                }
            ],
            "correlation_method": "pearson",
            "significance_level": 0.05
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/correlation",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertEqual(result["primary_metric_name"], request_data["primary_metric"]["name"])
        self.assertTrue(len(result["correlations"]) > 0)
        self.assertIn("summary", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["correlation_analysis"] = result
    
    def test_004_attribution_analysis(self):
        """测试归因分析接口"""
        # 准备请求数据
        request_data = {
            "metric_name": "销售额",
            "current_value": 1200,
            "previous_value": 1000,
            "factors": [
                {"name": "网站流量", "current_value": 15000, "previous_value": 12000},
                {"name": "转化率", "current_value": 0.08, "previous_value": 0.07},
                {"name": "客单价", "current_value": 120, "previous_value": 110},
                {"name": "促销活动", "current_value": 3, "previous_value": 2}
            ],
            "time_period": "月度",
            "attribution_method": "first_order"
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/attribution",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertEqual(result["metric_name"], request_data["metric_name"])
        self.assertEqual(len(result["attributions"]), len(request_data["factors"]))
        self.assertIn("summary", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["attribution_analysis"] = result
    
    def test_005_root_cause_analysis(self):
        """测试根因分析接口"""
        # 准备请求数据
        request_data = {
            "metric_name": "销售额",
            "current_value": 1200,
            "previous_value": 1000,
            "related_metrics": [
                {"name": "网站流量", "current_value": 15000, "previous_value": 12000},
                {"name": "转化率", "current_value": 0.08, "previous_value": 0.07},
                {"name": "客单价", "current_value": 120, "previous_value": 110},
                {"name": "促销活动", "current_value": 3, "previous_value": 2}
            ],
            "context": {
                "industry": "电子商务",
                "time_period": "月度",
                "region": "全国"
            },
            "analysis_depth": 2
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/root-cause",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertEqual(result["metric_name"], request_data["metric_name"])
        self.assertTrue(len(result["causes"]) > 0)
        self.assertIn("causal_graph", result)
        self.assertIn("summary", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["root_cause_analysis"] = result
    
    def test_006_prediction_analysis(self):
        """测试预测分析接口"""
        # 准备请求数据
        request_data = self.test_data.copy()
        request_data["forecast_periods"] = 3
        request_data["confidence_level"] = 0.95
        request_data["forecast_method"] = "auto"
        
        # 发送请求
        response = self.client.post(
            "/api/v1/prediction",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertEqual(result["metric_name"], request_data["metric_name"])
        self.assertEqual(len(result["forecast"]["values"]), request_data["forecast_periods"])
        self.assertIn("lower_bound", result["forecast"])
        self.assertIn("upper_bound", result["forecast"])
        self.assertIn("summary", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["prediction_analysis"] = result
    
    def test_007_suggestion_generation(self):
        """测试智能建议生成接口"""
        # 确保之前的分析结果已生成
        self.assertTrue("trend_analysis" in self.__class__.test_resources)
        self.assertTrue("attribution_analysis" in self.__class__.test_resources)
        
        # 准备请求数据
        request_data = {
            "metric_analysis": {
                "metric_name": "销售额",
                "current_value": 1200,
                "previous_value": 1000,
                "change_rate": 0.2,
                "change_type": "increase"
            },
            "attribution_analysis": self.__class__.test_resources["attribution_analysis"],
            "root_cause_analysis": self.__class__.test_resources["root_cause_analysis"],
            "prediction_analysis": self.__class__.test_resources["prediction_analysis"],
            "min_confidence": 0.6,
            "max_suggestions": 5
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/suggestion",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证分析结果
        result = data["data"]
        self.assertTrue(len(result["suggestions"]) > 0)
        self.assertLessEqual(len(result["suggestions"]), request_data["max_suggestions"])
        self.assertIn("overall_effect", result)
        
        # 保存结果用于后续测试
        self.__class__.test_resources["suggestions"] = result
    
    def test_008_export_result(self):
        """测试结果导出接口"""
        # 确保之前的分析结果已生成
        self.assertTrue("trend_analysis" in self.__class__.test_resources)
        self.assertTrue("suggestions" in self.__class__.test_resources)
        
        # 准备请求数据
        request_data = {
            "format": "json",
            "data": {
                "trend_analysis": self.__class__.test_resources["trend_analysis"],
                "correlation_analysis": self.__class__.test_resources["correlation_analysis"],
                "attribution_analysis": self.__class__.test_resources["attribution_analysis"],
                "root_cause_analysis": self.__class__.test_resources["root_cause_analysis"],
                "prediction_analysis": self.__class__.test_resources["prediction_analysis"],
                "suggestions": self.__class__.test_resources["suggestions"]
            },
            "filename": f"test_export_{int(time.time())}",
            "include_metadata": True
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/export/result",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 验证导出结果
        result = data["data"]
        self.assertIn("file_url", result)
        self.assertIn("file_name", result)
        self.assertEqual(result["file_type"], request_data["format"])
        
        # 保存导出文件路径
        export_url = result["file_url"]
        self.__class__.test_resources["export_url"] = export_url
        
        # 从URL中提取文件名
        filename = export_url.split("/")[-1]
        self.__class__.test_resources["export_file"] = filename
    
    def test_009_download_export(self):
        """测试下载导出文件接口"""
        # 确保之前的导出已完成
        self.assertTrue("export_url" in self.__class__.test_resources)
        
        # 提取filename参数
        filename = self.__class__.test_resources["export_file"]
        
        # 发送请求
        response = self.client.get(
            f"/api/v1/export/download?filename={filename}",
            headers=self.headers
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        
        # 验证文件内容
        content = response.content
        self.assertTrue(len(content) > 0)
        
        # 尝试解析JSON内容
        try:
            data = json.loads(content)
            self.assertIn("trend_analysis", data)
            self.assertIn("suggestions", data)
        except json.JSONDecodeError:
            self.fail("导出文件内容不是有效的JSON格式")
    
    def test_010_async_analysis_flow(self):
        """测试异步分析流程"""
        # 准备请求数据 - 使用较大的数据集触发异步处理
        request_data = {
            "metric_name": "大规模数据分析",
            "values": [i * 1.1 for i in range(100)],  # 较大的数据集
            "timestamps": [f"2023-01-{str(i+1).zfill(2)}" for i in range(100)],
            "trend_method": "auto",
            "detect_seasonality": True
        }
        
        # 发送异步分析请求
        response = self.client.post(
            "/api/v1/trend/analyze-async",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        data = response.json()
        self.assertTrue(data["success"])
        
        # 获取任务ID
        task_id = data["data"]["task_id"]
        self.assertTrue(task_id)
        
        # 轮询任务状态
        max_retries = 10
        retry_interval = 1  # 秒
        for i in range(max_retries):
            # 查询任务状态
            status_response = self.client.get(
                f"/api/v1/tasks/{task_id}",
                headers=self.headers
            )
            
            self.assertEqual(status_response.status_code, status.HTTP_200_OK)
            status_data = status_response.json()
            
            # 检查任务是否完成
            if status_data["data"]["status"] in ["completed", "failed"]:
                break
                
            # 等待一段时间再次查询
            time.sleep(retry_interval)
        
        # 验证任务最终状态
        self.assertEqual(status_data["data"]["status"], "completed")
        
        # 获取任务结果
        result_response = self.client.get(
            f"/api/v1/tasks/{task_id}/result",
            headers=self.headers
        )
        
        self.assertEqual(result_response.status_code, status.HTTP_200_OK)
        result_data = result_response.json()
        self.assertTrue(result_data["success"])
        
        # 验证分析结果
        result = result_data["data"]
        self.assertEqual(result["metric_name"], request_data["metric_name"])
        self.assertIn("trend", result)
        self.assertIn("summary", result)


class TestE2EApiErrors(unittest.TestCase):
    """API错误处理端到端测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.client = TestClient(app)
        self.api_token = os.environ.get("TEST_API_TOKEN", "test-token-for-e2e-tests")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Token": self.api_token
        }
    
    def test_missing_required_field(self):
        """测试缺少必填字段的错误处理"""
        # 准备缺少必填字段的请求数据
        request_data = {
            "metric_name": "测试指标",
            # 缺少values字段
            "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03"]
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=request_data
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error_type", data)
        self.assertEqual(data["error_type"], "ValidationError")
    
    def test_invalid_data_format(self):
        """测试无效数据格式的错误处理"""
        # 准备格式无效的请求数据
        request_data = {
            "metric_name": "测试指标",
            "values": "非数组格式",  # 应该是数组
            "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03"]
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=request_data
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error_type", data)
    
    def test_authentication_error(self):
        """测试认证错误的处理"""
        # 准备有效的请求数据
        request_data = {
            "metric_name": "测试指标",
            "values": [1, 2, 3],
            "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03"]
        }
        
        # 使用无效的API令牌
        invalid_headers = {
            "Content-Type": "application/json",
            "X-API-Token": "invalid-token"
        }
        
        # 发送请求
        response = self.client.post(
            "/api/v1/trend/analyze",
            headers=invalid_headers,
            json=request_data
        )
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error_type", data)
        self.assertEqual(data["error_type"], "AuthenticationError")
    
    def test_invalid_endpoint(self):
        """测试访问无效端点的错误处理"""
        # 发送请求到不存在的端点
        response = self.client.get("/api/v1/non-existent-endpoint")
        
        # 验证错误响应
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertFalse(data["success"])


if __name__ == '__main__':
    unittest.main() 