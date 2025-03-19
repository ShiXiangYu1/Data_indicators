#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
端到端测试模块
============

测试系统的完整工作流程，包括数据输入、分析处理和结果导出等端到端流程。
"""

import pytest
import pandas as pd
import numpy as np
import time
import json
import os
from fastapi.testclient import TestClient
import logging

from data_insight.app import app
from data_insight.core.models.trend import TrendAnalysisModel
from data_insight.core.models.attribution import AttributionAnalysisModel
from data_insight.core.models.rootcause import RootCauseAnalysisModel
from data_insight.core.models.prediction import PredictionAnalysisModel

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化测试客户端
client = TestClient(app)

# 测试数据路径
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
os.makedirs(TEST_DATA_DIR, exist_ok=True)


class TestEndToEndWorkflows:
    """测试端到端工作流"""

    def setup_method(self):
        """每个测试方法前的设置"""
        logger.info("准备端到端测试数据...")
        
        # 生成测试时间序列数据
        self.timestamps = pd.date_range(start='2023-01-01', periods=30, freq='D')
        
        # 基础趋势数据（线性上升趋势+周期性）
        base_trend = np.linspace(100, 200, 30)
        seasonality = 20 * np.sin(np.arange(30) * 2 * np.pi / 7)  # 7天周期
        noise = np.random.normal(0, 5, 30)
        
        self.metric_data = base_trend + seasonality + noise
        
        # 构造影响因素数据
        self.factor1 = base_trend * 0.5 + np.random.normal(0, 10, 30)
        self.factor2 = seasonality * 2 + np.random.normal(0, 5, 30)
        self.factor3 = base_trend * 0.3 + seasonality * 0.5 + np.random.normal(0, 8, 30)
        
        # 创建测试数据集
        self.test_df = pd.DataFrame({
            'timestamp': self.timestamps,
            'metric': self.metric_data,
            'factor1': self.factor1,
            'factor2': self.factor2,
            'factor3': self.factor3
        })
        
        # 保存测试数据
        self.test_data_path = os.path.join(TEST_DATA_DIR, 'test_data.csv')
        self.test_df.to_csv(self.test_data_path, index=False)
        
        logger.info(f"测试数据已保存至: {self.test_data_path}")
    
    def test_complete_trend_analysis_workflow(self):
        """测试完整的趋势分析工作流程"""
        logger.info("开始趋势分析端到端测试...")
        
        # 准备API请求数据
        data = {
            "metric_name": "测试指标",
            "timestamps": self.timestamps.strftime("%Y-%m-%d").tolist(),
            "values": self.metric_data.tolist(),
            "trend_method": "auto",
            "detect_seasonality": True,
            "frequency": "D"
        }
        
        # 1. 调用趋势分析API
        response = client.post("/api/v1/analysis/trend", json=data)
        assert response.status_code == 200
        result = response.json()
        
        # 验证结果格式
        assert "data" in result
        assert "trend_type" in result["data"]
        assert "trend_parameters" in result["data"]
        assert "seasonality_detected" in result["data"]
        assert "change_points" in result["data"]
        
        # 获取分析结果ID
        analysis_id = result["data"]["analysis_id"]
        
        # 2. 获取分析详细信息
        detail_response = client.get(f"/api/v1/analysis/trend/{analysis_id}")
        assert detail_response.status_code == 200
        detail_result = detail_response.json()
        
        # 验证详细结果
        assert detail_result["data"]["trend_parameters"]["trend_coefficient"] > 0  # 应该是上升趋势
        assert detail_result["data"]["seasonality_detected"] == True  # 应该检测到季节性
        
        # 3. 生成可视化
        viz_response = client.get(f"/api/v1/analysis/trend/{analysis_id}/visualization")
        assert viz_response.status_code == 200
        assert "image/png" in viz_response.headers.get("content-type", "")
        
        # 4. 导出结果
        export_data = {
            "analysis_id": analysis_id,
            "analysis_type": "trend",
            "format": "json",
            "include_visualization": True
        }
        export_response = client.post("/api/v1/export/result", json=export_data)
        assert export_response.status_code == 200
        export_result = export_response.json()
        
        # 验证导出结果
        assert "export_id" in export_result["data"]
        assert "download_url" in export_result["data"]
        
        # 5. 下载导出的结果
        download_url = export_result["data"]["download_url"]
        download_response = client.get(download_url)
        assert download_response.status_code == 200
        
        logger.info("趋势分析端到端测试完成")
    
    def test_attribution_to_prediction_workflow(self):
        """测试归因分析到预测分析的完整工作流程"""
        logger.info("开始归因分析到预测分析的端到端测试...")
        
        # 准备归因分析API请求数据
        attribution_data = {
            "metric_name": "销售额",
            "metric_values": self.metric_data.tolist(),
            "timestamps": self.timestamps.strftime("%Y-%m-%d").tolist(),
            "factors": {
                "营销支出": self.factor1.tolist(),
                "季节因素": self.factor2.tolist(),
                "价格调整": self.factor3.tolist()
            },
            "attribution_method": "shapley",
            "baseline_method": "average"
        }
        
        # 1. 调用归因分析API
        attribution_response = client.post("/api/v1/analysis/attribution", json=attribution_data)
        assert attribution_response.status_code == 200
        attribution_result = attribution_response.json()
        
        # 验证归因结果
        assert "data" in attribution_result
        assert "attributions" in attribution_result["data"]
        assert "total_contribution" in attribution_result["data"]
        
        # 提取归因结果用于后续预测
        attribution_id = attribution_result["data"]["analysis_id"]
        attributions = attribution_result["data"]["attributions"]
        
        # 根据归因结果，确定主要影响因素
        primary_factors = [factor for factor, value in attributions.items() 
                          if value > 0.2]  # 只选择贡献度大于20%的因素
        
        logger.info(f"主要影响因素: {primary_factors}")
        
        # 2. 根据归因结果构建预测分析请求
        prediction_data = {
            "metric_name": "销售额",
            "timestamps": self.timestamps.strftime("%Y-%m-%d").tolist(),
            "values": self.metric_data.tolist(),
            "forecast_periods": 10,
            "confidence_level": 0.95,
            "related_factors": {
                factor: attribution_data["factors"][factor] for factor in primary_factors
            },
            "seasonality_mode": "additive",
            "prior_scale": 0.05
        }
        
        # 3. 调用预测分析API
        prediction_response = client.post("/api/v1/analysis/prediction", json=prediction_data)
        assert prediction_response.status_code == 200
        prediction_result = prediction_response.json()
        
        # 验证预测结果
        assert "data" in prediction_result
        assert "forecast" in prediction_result["data"]
        assert "forecast_lower" in prediction_result["data"]
        assert "forecast_upper" in prediction_result["data"]
        assert "forecast_timestamps" in prediction_result["data"]
        
        prediction_id = prediction_result["data"]["analysis_id"]
        
        # 4. 获取预测可视化
        viz_response = client.get(f"/api/v1/analysis/prediction/{prediction_id}/visualization")
        assert viz_response.status_code == 200
        
        # 5. 生成智能建议
        suggestion_data = {
            "analysis_results": {
                "attribution": {
                    "analysis_id": attribution_id,
                    "attributions": attributions
                },
                "prediction": {
                    "analysis_id": prediction_id,
                    "forecast": prediction_result["data"]["forecast"]
                }
            },
            "context": {
                "business_domain": "电子商务",
                "goal": "提升销售额",
                "constraints": ["预算有限", "短期内实现"]
            }
        }
        
        suggestion_response = client.post("/api/v1/suggestion", json=suggestion_data)
        assert suggestion_response.status_code == 200
        suggestion_result = suggestion_response.json()
        
        # 验证建议结果
        assert "data" in suggestion_result
        assert "suggestions" in suggestion_result["data"]
        assert len(suggestion_result["data"]["suggestions"]) > 0
        
        # 6. 一次性导出所有分析结果
        export_data = {
            "analysis_ids": [attribution_id, prediction_id],
            "format": "pdf",
            "include_suggestions": True,
            "include_visualization": True
        }
        
        export_response = client.post("/api/v1/export/comprehensive", json=export_data)
        assert export_response.status_code == 200
        
        logger.info("归因分析到预测分析的端到端测试完成")
    
    def test_root_cause_analysis_workflow(self):
        """测试根因分析完整工作流程"""
        logger.info("开始根因分析端到端测试...")
        
        # 准备根因分析API请求数据
        root_cause_data = {
            "target_metric": "销售额",
            "target_values": self.metric_data.tolist(),
            "timestamps": self.timestamps.strftime("%Y-%m-%d").tolist(),
            "potential_causes": {
                "营销支出": self.factor1.tolist(),
                "季节因素": self.factor2.tolist(),
                "价格调整": self.factor3.tolist()
            },
            "anomaly_detection": True,
            "causal_discovery_method": "pc_algorithm"
        }
        
        # 1. 调用根因分析API
        response = client.post("/api/v1/analysis/rootcause", json=root_cause_data)
        assert response.status_code == 200
        result = response.json()
        
        # 验证结果
        assert "data" in result
        assert "causal_graph" in result["data"]
        assert "primary_causes" in result["data"]
        
        root_cause_id = result["data"]["analysis_id"]
        
        # 2. 获取根因分析可视化
        viz_response = client.get(f"/api/v1/analysis/rootcause/{root_cause_id}/visualization")
        assert viz_response.status_code == 200
        
        # 3. 导出根因分析报告
        export_data = {
            "analysis_id": root_cause_id,
            "analysis_type": "rootcause",
            "format": "pdf",
            "include_recommendations": True
        }
        
        export_response = client.post("/api/v1/export/result", json=export_data)
        assert export_response.status_code == 200
        
        logger.info("根因分析端到端测试完成")
    
    def test_data_upload_to_analysis_workflow(self):
        """测试从数据上传到分析的完整工作流程"""
        logger.info("开始数据上传到分析的端到端测试...")
        
        # 1. 上传数据文件
        with open(self.test_data_path, 'rb') as f:
            upload_response = client.post(
                "/api/v1/data/upload",
                files={"file": ("test_data.csv", f, "text/csv")}
            )
        
        assert upload_response.status_code == 200
        upload_result = upload_response.json()
        
        # 验证上传结果
        assert "data" in upload_result
        assert "dataset_id" in upload_result["data"]
        
        dataset_id = upload_result["data"]["dataset_id"]
        
        # 2. 获取数据集摘要
        summary_response = client.get(f"/api/v1/data/summary/{dataset_id}")
        assert summary_response.status_code == 200
        summary_result = summary_response.json()
        
        # 验证摘要信息
        assert "data" in summary_result
        assert "columns" in summary_result["data"]
        assert "row_count" in summary_result["data"]
        assert "numeric_columns" in summary_result["data"]
        
        # 3. 配置分析
        analysis_config = {
            "dataset_id": dataset_id,
            "analysis_type": "comprehensive",
            "target_column": "metric",
            "timestamp_column": "timestamp",
            "feature_columns": ["factor1", "factor2", "factor3"],
            "components": ["trend", "attribution", "rootcause", "prediction"]
        }
        
        config_response = client.post("/api/v1/analysis/configure", json=analysis_config)
        assert config_response.status_code == 200
        config_result = config_response.json()
        
        # 验证配置结果
        assert "data" in config_result
        assert "analysis_configuration_id" in config_result["data"]
        
        config_id = config_result["data"]["analysis_configuration_id"]
        
        # 4. 执行分析
        execute_response = client.post(f"/api/v1/analysis/execute/{config_id}")
        assert execute_response.status_code == 200
        execute_result = execute_response.json()
        
        # 验证执行结果
        assert "data" in execute_result
        assert "job_id" in execute_result["data"]
        
        job_id = execute_result["data"]["job_id"]
        
        # 5. 轮询任务状态直到完成
        max_attempts = 10
        attempts = 0
        job_completed = False
        
        while attempts < max_attempts and not job_completed:
            status_response = client.get(f"/api/v1/analysis/job/{job_id}")
            assert status_response.status_code == 200
            status_result = status_response.json()
            
            if status_result["data"]["status"] in ["SUCCESS", "FAILURE"]:
                job_completed = True
                assert status_result["data"]["status"] == "SUCCESS"
            else:
                attempts += 1
                time.sleep(3)  # 等待3秒再次检查
        
        assert job_completed, "分析任务未在预期时间内完成"
        
        # 6. 获取分析结果
        results_response = client.get(f"/api/v1/analysis/results/{job_id}")
        assert results_response.status_code == 200
        results = results_response.json()
        
        # 验证分析结果
        assert "data" in results
        assert "components" in results["data"]
        assert "trend" in results["data"]["components"]
        assert "attribution" in results["data"]["components"]
        assert "rootcause" in results["data"]["components"]
        assert "prediction" in results["data"]["components"]
        
        # 7. 导出综合报告
        report_data = {
            "job_id": job_id,
            "format": "pdf",
            "template": "comprehensive",
            "include_visualizations": True,
            "include_recommendations": True
        }
        
        report_response = client.post("/api/v1/export/report", json=report_data)
        assert report_response.status_code == 200
        report_result = report_response.json()
        
        # 验证报告导出结果
        assert "data" in report_result
        assert "report_id" in report_result["data"]
        assert "download_url" in report_result["data"]
        
        logger.info("数据上传到分析的端到端测试完成")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 