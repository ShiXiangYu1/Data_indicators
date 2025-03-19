#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析流程端到端测试
===============

测试从数据输入到结果输出的完整分析流程，包括各种分析功能和导出功能。
"""

import unittest
import json
import os
import pandas as pd
import tempfile
from fastapi.testclient import TestClient

from data_insight.app import create_app
from data_insight.utils.data_generator import generate_sample_data
from data_insight.services.file_service import save_temp_file


class TestE2EAnalysis(unittest.TestCase):
    """测试端到端分析流程"""
    
    @classmethod
    def setUpClass(cls):
        """测试类前置设置"""
        # 创建测试应用
        cls.app = create_app({"TESTING": True})
        cls.client = TestClient(cls.app)
        
        # 准备测试数据
        cls.sample_data = generate_sample_data(
            start_date="2023-01-01",
            end_date="2023-12-31", 
            metrics=["sales", "users", "conversion_rate"],
            dimensions=["channel", "region", "device"]
        )
        
        # 保存为临时文件
        cls.temp_file_path = save_temp_file(
            cls.sample_data.to_csv(index=False), 
            file_type="csv"
        )
    
    @classmethod
    def tearDownClass(cls):
        """测试类后置清理"""
        # 删除临时文件
        if os.path.exists(cls.temp_file_path):
            os.remove(cls.temp_file_path)
    
    def test_e2e_trend_analysis(self):
        """测试趋势分析端到端流程"""
        # 第1步：上传数据文件
        with open(self.temp_file_path, "rb") as f:
            response = self.client.post(
                "/api/v1/data/upload",
                files={"file": ("sample_data.csv", f, "text/csv")}
            )
        
        self.assertEqual(response.status_code, 200)
        upload_result = response.json()
        self.assertIn("data_id", upload_result)
        data_id = upload_result["data_id"]
        
        # 第2步：进行数据预处理
        preprocess_response = self.client.post(
            "/api/v1/data/preprocess",
            json={
                "data_id": data_id,
                "operations": [
                    {"type": "fillna", "columns": ["sales", "users"], "method": "mean"},
                    {"type": "normalize", "columns": ["sales", "users"]}
                ],
                "time_column": "date"
            }
        )
        
        self.assertEqual(preprocess_response.status_code, 200)
        preprocess_result = preprocess_response.json()
        self.assertIn("success", preprocess_result)
        self.assertTrue(preprocess_result["success"])
        
        # 第3步：执行趋势分析
        trend_analysis_response = self.client.post(
            "/api/v1/analysis/trend",
            json={
                "data_id": data_id,
                "metric": "sales",
                "time_column": "date",
                "dimensions": ["channel"],
                "analysis_type": "decomposition",
                "period": 7
            }
        )
        
        self.assertEqual(trend_analysis_response.status_code, 200)
        trend_result = trend_analysis_response.json()
        self.assertIn("analysis_id", trend_result)
        analysis_id = trend_result["analysis_id"]
        
        # 第4步：获取分析结果
        result_response = self.client.get(f"/api/v1/analysis/result/{analysis_id}")
        self.assertEqual(result_response.status_code, 200)
        analysis_result = result_response.json()
        
        self.assertIn("components", analysis_result)
        self.assertIn("trend", analysis_result["components"])
        self.assertIn("seasonal", analysis_result["components"])
        self.assertIn("residual", analysis_result["components"])
        
        # 第5步：导出分析结果
        export_response = self.client.post(
            "/api/v1/export/result",
            json={
                "analysis_id": analysis_id,
                "format": "json"
            }
        )
        
        self.assertEqual(export_response.status_code, 200)
        export_result = export_response.json()
        self.assertIn("export_url", export_result)
        
        # 第6步：验证导出的文件
        export_url = export_result["export_url"]
        download_response = self.client.get(export_url)
        self.assertEqual(download_response.status_code, 200)
        downloaded_data = download_response.json()
        
        self.assertIn("components", downloaded_data)
        self.assertIn("trend", downloaded_data["components"])
    
    def test_e2e_attribution_analysis(self):
        """测试归因分析端到端流程"""
        # 第1步：上传数据
        with open(self.temp_file_path, "rb") as f:
            response = self.client.post(
                "/api/v1/data/upload",
                files={"file": ("sample_data.csv", f, "text/csv")}
            )
        
        data_id = response.json()["data_id"]
        
        # 第2步：执行归因分析
        attribution_response = self.client.post(
            "/api/v1/analysis/attribution",
            json={
                "data_id": data_id,
                "target_metric": "conversion_rate",
                "dimensions": ["channel", "region", "device"],
                "time_column": "date",
                "comparison_period": {
                    "start": "2023-10-01",
                    "end": "2023-12-31"
                },
                "base_period": {
                    "start": "2023-07-01",
                    "end": "2023-09-30"
                },
                "method": "shapley"
            }
        )
        
        self.assertEqual(attribution_response.status_code, 200)
        attribution_result = attribution_response.json()
        self.assertIn("analysis_id", attribution_result)
        analysis_id = attribution_result["analysis_id"]
        
        # 第3步：获取分析结果
        result_response = self.client.get(f"/api/v1/analysis/result/{analysis_id}")
        self.assertEqual(result_response.status_code, 200)
        analysis_result = result_response.json()
        
        self.assertIn("contributions", analysis_result)
        self.assertTrue(len(analysis_result["contributions"]) > 0)
        
        # 第4步：获取智能建议
        suggestion_response = self.client.post(
            "/api/v1/suggestion",
            json={
                "analysis_id": analysis_id,
                "analysis_type": "attribution",
                "target_metric": "conversion_rate"
            }
        )
        
        self.assertEqual(suggestion_response.status_code, 200)
        suggestion_result = suggestion_response.json()
        self.assertIn("suggestions", suggestion_result)
        self.assertTrue(len(suggestion_result["suggestions"]) > 0)
    
    def test_e2e_correlation_analysis(self):
        """测试相关性分析端到端流程"""
        # 第1步：上传数据
        with open(self.temp_file_path, "rb") as f:
            response = self.client.post(
                "/api/v1/data/upload",
                files={"file": ("sample_data.csv", f, "text/csv")}
            )
        
        data_id = response.json()["data_id"]
        
        # 第2步：执行相关性分析
        correlation_response = self.client.post(
            "/api/v1/analysis/correlation",
            json={
                "data_id": data_id,
                "metrics": ["sales", "users", "conversion_rate"],
                "method": "pearson",
                "min_correlation": 0.3
            }
        )
        
        self.assertEqual(correlation_response.status_code, 200)
        correlation_result = correlation_response.json()
        self.assertIn("analysis_id", correlation_result)
        analysis_id = correlation_result["analysis_id"]
        
        # 第3步：获取分析结果
        result_response = self.client.get(f"/api/v1/analysis/result/{analysis_id}")
        self.assertEqual(result_response.status_code, 200)
        analysis_result = result_response.json()
        
        self.assertIn("correlation_matrix", analysis_result)
        self.assertIn("significant_pairs", analysis_result)
    
    def test_e2e_prediction_analysis(self):
        """测试预测分析端到端流程"""
        # 第1步：上传数据
        with open(self.temp_file_path, "rb") as f:
            response = self.client.post(
                "/api/v1/data/upload",
                files={"file": ("sample_data.csv", f, "text/csv")}
            )
        
        data_id = response.json()["data_id"]
        
        # 第2步：执行预测分析
        prediction_response = self.client.post(
            "/api/v1/analysis/prediction",
            json={
                "data_id": data_id,
                "metric": "sales",
                "time_column": "date",
                "dimensions": ["channel"],
                "forecast_periods": 30,
                "model": "prophet",
                "confidence_interval": 0.95
            }
        )
        
        self.assertEqual(prediction_response.status_code, 200)
        prediction_result = prediction_response.json()
        self.assertIn("analysis_id", prediction_result)
        analysis_id = prediction_result["analysis_id"]
        
        # 第3步：获取分析结果
        result_response = self.client.get(f"/api/v1/analysis/result/{analysis_id}")
        self.assertEqual(result_response.status_code, 200)
        analysis_result = result_response.json()
        
        self.assertIn("forecast", analysis_result)
        self.assertIn("lower_bound", analysis_result)
        self.assertIn("upper_bound", analysis_result)


class TestE2EExportFunctionality(unittest.TestCase):
    """测试导出功能的端到端流程"""
    
    def setUp(self):
        """测试前置设置"""
        self.app = create_app({"TESTING": True})
        self.client = TestClient(self.app)
        
        # 创建测试分析结果
        response = self.client.post(
            "/api/v1/analysis/sample",
            json={"analysis_type": "trend", "metric": "sales"}
        )
        self.analysis_id = response.json()["analysis_id"]
    
    def test_export_to_csv(self):
        """测试导出为CSV格式"""
        response = self.client.post(
            "/api/v1/export/result",
            json={
                "analysis_id": self.analysis_id,
                "format": "csv"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("export_url", result)
        
        # 下载导出的文件
        download_response = self.client.get(result["export_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.headers["Content-Type"], "text/csv")
        
        # 验证CSV内容
        content = download_response.content.decode("utf-8")
        self.assertIn("date", content)
        self.assertIn("sales", content)
    
    def test_export_to_excel(self):
        """测试导出为Excel格式"""
        response = self.client.post(
            "/api/v1/export/result",
            json={
                "analysis_id": self.analysis_id,
                "format": "excel"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("export_url", result)
        
        # 下载导出的文件
        download_response = self.client.get(result["export_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(
            download_response.headers["Content-Type"], 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # 验证文件大小（确保不是空文件）
        self.assertTrue(len(download_response.content) > 100)
    
    def test_export_to_pdf(self):
        """测试导出为PDF格式"""
        response = self.client.post(
            "/api/v1/export/result",
            json={
                "analysis_id": self.analysis_id,
                "format": "pdf",
                "include_charts": True
            }
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("export_url", result)
        
        # 下载导出的文件
        download_response = self.client.get(result["export_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.headers["Content-Type"], "application/pdf")
        
        # 验证文件大小（确保不是空文件）
        self.assertTrue(len(download_response.content) > 1000)


if __name__ == "__main__":
    unittest.main() 