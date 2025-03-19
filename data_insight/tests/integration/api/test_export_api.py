#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导出API的集成测试
测试导出API的各种功能和处理边界情况
"""

import pytest
import os
import json
import tempfile
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from data_insight.app import app
from data_insight.api.routes.export import ExportFormat, clean_temp_files


class TestExportAPI:
    """导出API功能的测试类"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def sample_analysis_result(self):
        """创建示例分析结果数据"""
        return {
            "analysis_id": "test_analysis_123",
            "status": "completed",
            "type": "trend",
            "created_at": "2023-06-01T10:00:00",
            "result": {
                "trend_direction": "increasing",
                "confidence": 0.95,
                "slope": 2.5,
                "change_points": ["2023-02-15", "2023-04-10"],
                "seasonality": {
                    "has_seasonality": True,
                    "period": 7
                },
                "data": [
                    {"date": "2023-01-01", "value": 100},
                    {"date": "2023-01-02", "value": 102},
                    {"date": "2023-01-03", "value": 105},
                    # ... 更多数据点
                    {"date": "2023-01-30", "value": 175}
                ]
            }
        }

    @pytest.fixture
    def mock_temp_dir(self):
        """创建临时目录用于测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('data_insight.api.routes.export.TEMP_EXPORT_DIR', temp_dir):
                yield temp_dir

    def test_export_result_csv(self, client, sample_analysis_result, mock_temp_dir):
        """测试CSV格式导出"""
        # 模拟获取分析结果的函数
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=sample_analysis_result):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": ExportFormat.CSV.value,
                    "include_metadata": True
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            result = response.json()
            assert "download_url" in result
            assert "expires_at" in result
            assert ExportFormat.CSV.value in result["download_url"]
            
            # 验证文件是否已创建
            file_path = os.path.join(mock_temp_dir, 
                                     os.path.basename(result["download_url"].split("?")[0]))
            assert os.path.exists(file_path)
            
            # 验证文件内容
            df = pd.read_csv(file_path)
            assert "date" in df.columns
            assert "value" in df.columns
            assert len(df) == len(sample_analysis_result["result"]["data"])

    def test_export_result_excel(self, client, sample_analysis_result, mock_temp_dir):
        """测试Excel格式导出"""
        # 模拟获取分析结果的函数
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=sample_analysis_result):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": ExportFormat.EXCEL.value,
                    "include_metadata": True
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            result = response.json()
            assert "download_url" in result
            assert ExportFormat.EXCEL.value in result["download_url"]
            
            # 验证文件是否已创建
            file_path = os.path.join(mock_temp_dir, 
                                     os.path.basename(result["download_url"].split("?")[0]))
            assert os.path.exists(file_path)
            
            # 验证文件内容
            df = pd.read_excel(file_path)
            assert "date" in df.columns
            assert "value" in df.columns
            assert len(df) == len(sample_analysis_result["result"]["data"])

    def test_export_result_pdf(self, client, sample_analysis_result, mock_temp_dir):
        """测试PDF格式导出"""
        # 模拟获取分析结果的函数
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=sample_analysis_result), \
             patch('data_insight.api.routes.export.export_to_pdf') as mock_export_pdf:
            # 模拟PDF导出函数，返回临时文件路径
            temp_pdf_path = os.path.join(mock_temp_dir, "test_analysis_123.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(b"%PDF-1.5\n")  # 简单的PDF文件头
            mock_export_pdf.return_value = temp_pdf_path
            
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": ExportFormat.PDF.value,
                    "include_charts": True
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            result = response.json()
            assert "download_url" in result
            assert ExportFormat.PDF.value in result["download_url"]
            
            # 验证文件是否存在
            file_path = os.path.join(mock_temp_dir, 
                                    os.path.basename(result["download_url"].split("?")[0]))
            assert os.path.exists(file_path)
            
            # 验证mock函数是否被正确调用
            mock_export_pdf.assert_called_once()
            call_args = mock_export_pdf.call_args[0]
            assert call_args[0] == sample_analysis_result
            assert call_args[1] == True  # include_charts

    def test_export_result_json(self, client, sample_analysis_result, mock_temp_dir):
        """测试JSON格式导出"""
        # 模拟获取分析结果的函数
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=sample_analysis_result):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": ExportFormat.JSON.value
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            result = response.json()
            assert "download_url" in result
            assert ExportFormat.JSON.value in result["download_url"]
            
            # 验证文件是否已创建
            file_path = os.path.join(mock_temp_dir, 
                                     os.path.basename(result["download_url"].split("?")[0]))
            assert os.path.exists(file_path)
            
            # 验证文件内容
            with open(file_path, 'r') as f:
                exported_data = json.load(f)
            assert exported_data["analysis_id"] == sample_analysis_result["analysis_id"]
            assert exported_data["result"]["trend_direction"] == sample_analysis_result["result"]["trend_direction"]

    def test_download_file(self, client, mock_temp_dir):
        """测试下载文件端点"""
        # 创建测试文件
        test_content = "test,data\n1,2\n3,4"
        test_filename = "test_export_123.csv"
        test_file_path = os.path.join(mock_temp_dir, test_filename)
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        # 测试下载
        response = client.get(f"/api/v1/export/download/{test_filename}")
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert response.headers["content-disposition"] == f'attachment; filename="{test_filename}"'
        assert response.content.decode() == test_content

    def test_download_non_existent_file(self, client, mock_temp_dir):
        """测试下载不存在的文件"""
        non_existent_file = "non_existent_file.csv"
        
        # 测试下载不存在的文件
        response = client.get(f"/api/v1/export/download/{non_existent_file}")
        
        # 验证响应
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_invalid_analysis_id(self, client):
        """测试导出无效的分析ID"""
        # 模拟获取分析结果的函数抛出异常
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   side_effect=ValueError("Analysis not found")):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "invalid_id",
                    "format": ExportFormat.CSV.value
                }
            )
            
            # 验证响应
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_export_incomplete_analysis(self, client):
        """测试导出未完成的分析"""
        # 模拟获取分析结果返回未完成的分析
        incomplete_analysis = {
            "analysis_id": "test_analysis_123",
            "status": "processing",
            "type": "trend",
            "created_at": "2023-06-01T10:00:00"
        }
        
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=incomplete_analysis):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": ExportFormat.CSV.value
                }
            )
            
            # 验证响应
            assert response.status_code == 400
            assert "not completed" in response.json()["detail"].lower()

    def test_export_invalid_format(self, client, sample_analysis_result):
        """测试导出无效的格式"""
        with patch('data_insight.api.routes.export.get_analysis_result', 
                   return_value=sample_analysis_result):
            response = client.post(
                "/api/v1/export/result",
                json={
                    "analysis_id": "test_analysis_123",
                    "format": "invalid_format"
                }
            )
            
            # 验证响应
            assert response.status_code == 422  # 验证请求失败

    def test_clean_temp_files(self, mock_temp_dir):
        """测试清理临时文件功能"""
        # 创建一些测试文件，设置不同的修改时间
        import time
        from datetime import datetime, timedelta
        
        # 创建旧文件 (7天前)
        old_file = os.path.join(mock_temp_dir, "old_export.csv")
        with open(old_file, 'w') as f:
            f.write("old,file")
        
        # 设置文件修改时间为7天前
        old_time = time.time() - 7 * 24 * 3600
        os.utime(old_file, (old_time, old_time))
        
        # 创建新文件 (刚刚创建)
        new_file = os.path.join(mock_temp_dir, "new_export.csv")
        with open(new_file, 'w') as f:
            f.write("new,file")
        
        # 执行清理 (5天前的文件)
        days = 5
        clean_temp_files(days)
        
        # 验证结果
        assert not os.path.exists(old_file), "旧文件应该被删除"
        assert os.path.exists(new_file), "新文件应该保留"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 