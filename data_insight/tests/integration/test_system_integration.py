#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统集成测试模块
============

测试系统各组件间的协同工作和数据流转。
"""

import unittest
import os
import time
import json
import logging
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from fastapi import status

from data_insight.app import app, create_app
from data_insight.core import (
    TrendAnalyzer, 
    CorrelationAnalyzer, 
    AttributionAnalyzer, 
    RootCauseAnalyzer, 
    Predictor,
    SuggestionGenerator
)
from data_insight.utils import get_cache_manager
from data_insight.utils.cache_manager import CacheBackend
from data_insight.services import get_async_task_service, TaskPriority, TaskStatus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 初始化测试客户端
        cls.client = TestClient(app)
        cls.api_token = os.environ.get("TEST_API_TOKEN", "test-token-for-integration-tests")
        cls.headers = {
            "Content-Type": "application/json",
            "X-API-Token": cls.api_token
        }
        
        # 初始化缓存管理器（使用内存缓存以避免依赖外部Redis）
        cls.cache_manager = get_cache_manager({
            "backend": CacheBackend.MEMORY,
            "ttl": 300,
            "max_size": 1000
        })
        
        # 初始化分析器
        cls.trend_analyzer = TrendAnalyzer()
        cls.correlation_analyzer = CorrelationAnalyzer()
        cls.attribution_analyzer = AttributionAnalyzer()
        cls.root_cause_analyzer = RootCauseAnalyzer()
        cls.predictor = Predictor()
        cls.suggestion_generator = SuggestionGenerator()
        
        # 初始化异步任务服务
        cls.task_service = get_async_task_service()
        
        # 创建临时目录用于存储测试文件
        cls.temp_dir = tempfile.mkdtemp()
        
        # 测试数据
        cls.time_series_data = {
            "metric_name": "销售额",
            "values": [100, 120, 140, 130, 150, 160, 180, 200, 220, 210, 240, 250],
            "timestamps": [f"2023-01-{i:02d}" for i in range(1, 13)]
        }
        
        cls.attribution_data = {
            "metric_name": "转化率",
            "current_value": 0.05,
            "previous_value": 0.04,
            "factors": [
                {"name": "页面加载速度", "current_value": 2.5, "previous_value": 3.2},
                {"name": "表单简化程度", "current_value": 0.8, "previous_value": 0.6},
                {"name": "推荐个性化程度", "current_value": 0.7, "previous_value": 0.5},
                {"name": "优惠力度", "current_value": 0.15, "previous_value": 0.1}
            ],
            "time_period": "月度",
            "attribution_method": "shapley_value"
        }
        
        cls.correlation_data = {
            "primary_metric": {
                "name": "网站流量",
                "values": [1000, 1200, 1400, 1300, 1350, 1500, 1600, 1800, 1750, 1900, 2000, 2100],
                "timestamps": [f"2023-01-{i:02d}" for i in range(1, 13)]
            },
            "secondary_metrics": [
                {
                    "name": "营销支出",
                    "values": [5000, 5500, 6000, 5800, 6500, 7000, 7500, 8000, 7800, 8500, 9000, 9500],
                    "timestamps": [f"2023-01-{i:02d}" for i in range(1, 13)]
                },
                {
                    "name": "转化率",
                    "values": [0.03, 0.035, 0.04, 0.042, 0.041, 0.044, 0.047, 0.05, 0.048, 0.052, 0.055, 0.056],
                    "timestamps": [f"2023-01-{i:02d}" for i in range(1, 13)]
                }
            ],
            "correlation_method": "pearson",
            "significance_level": 0.05
        }
    
    @classmethod
    def tearDownClass(cls):
        """测试完成后清理资源"""
        # 清理临时目录
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        
        # 关闭异步任务服务
        cls.task_service.shutdown()
        
        # 清理缓存
        cls.cache_manager.clear()
    
    def test_001_core_analyzers_integration(self):
        """测试核心分析器之间的集成"""
        logger.info("开始测试核心分析器集成")
        
        # 1. 趋势分析
        trend_result = self.trend_analyzer.analyze(
            metric_name=self.time_series_data["metric_name"],
            values=self.time_series_data["values"],
            timestamps=self.time_series_data["timestamps"],
            trend_method="auto",
            seasonality=True
        )
        
        # 验证趋势分析结果
        self.assertEqual(trend_result["metric_name"], self.time_series_data["metric_name"])
        self.assertIn("trend", trend_result)
        self.assertIn("trend_type", trend_result["trend"])
        self.assertEqual(trend_result["trend"]["trend_type"], "increasing")
        
        # 2. 基于同样的数据进行预测分析
        prediction_result = self.predictor.analyze(
            metric_name=self.time_series_data["metric_name"],
            values=self.time_series_data["values"],
            timestamps=self.time_series_data["timestamps"],
            forecast_periods=3,
            confidence_level=0.95
        )
        
        # 验证预测分析结果
        self.assertEqual(prediction_result["metric_name"], self.time_series_data["metric_name"])
        self.assertIn("forecast", prediction_result)
        self.assertEqual(len(prediction_result["forecast"]["values"]), 3)
        self.assertGreater(prediction_result["forecast"]["values"][0], self.time_series_data["values"][-1])
        
        # 3. 相关性分析
        correlation_result = self.correlation_analyzer.analyze(
            primary_metric=self.correlation_data["primary_metric"],
            secondary_metrics=self.correlation_data["secondary_metrics"],
            correlation_method=self.correlation_data["correlation_method"],
            significance_level=self.correlation_data["significance_level"]
        )
        
        # 验证相关性分析结果
        self.assertEqual(correlation_result["primary_metric_name"], self.correlation_data["primary_metric"]["name"])
        self.assertIn("correlations", correlation_result)
        self.assertEqual(len(correlation_result["correlations"]), len(self.correlation_data["secondary_metrics"]))
        
        # 4. 归因分析
        attribution_result = self.attribution_analyzer.analyze(
            metric_name=self.attribution_data["metric_name"],
            current_value=self.attribution_data["current_value"],
            previous_value=self.attribution_data["previous_value"],
            factors=self.attribution_data["factors"],
            time_period=self.attribution_data["time_period"],
            attribution_method=self.attribution_data["attribution_method"]
        )
        
        # 验证归因分析结果
        self.assertEqual(attribution_result["metric_name"], self.attribution_data["metric_name"])
        self.assertIn("attributions", attribution_result)
        self.assertEqual(len(attribution_result["attributions"]), len(self.attribution_data["factors"]))
        
        # 5. 基于上述结果生成智能建议
        integrated_data = {
            "metric_analysis": {
                "metric_name": self.time_series_data["metric_name"],
                "current_value": self.time_series_data["values"][-1],
                "previous_value": self.time_series_data["values"][-2],
                "change_rate": (self.time_series_data["values"][-1] - self.time_series_data["values"][-2]) / self.time_series_data["values"][-2],
                "change_type": "increase"
            },
            "trend_analysis": trend_result,
            "attribution_analysis": attribution_result,
            "prediction_analysis": prediction_result,
            "correlation_analysis": correlation_result
        }
        
        suggestion_result = self.suggestion_generator.analyze(integrated_data)
        
        # 验证智能建议结果
        self.assertIn("suggestions", suggestion_result)
        self.assertTrue(len(suggestion_result["suggestions"]) > 0)
        self.assertIn("overall_effect", suggestion_result)
        
        logger.info("核心分析器集成测试完成")
    
    def test_002_cache_integration(self):
        """测试缓存系统与分析器的集成"""
        logger.info("开始测试缓存系统集成")
        
        # 清理可能存在的缓存
        self.cache_manager.clear()
        
        # 创建缓存键
        cache_key = f"trend_analysis:{self.time_series_data['metric_name']}:{hash(str(self.time_series_data['values']))}"
        
        # 确认缓存中不存在该键
        initial_value = self.cache_manager.get(cache_key)
        self.assertIsNone(initial_value)
        
        # 执行趋势分析并缓存结果
        start_time = time.time()
        trend_result = self.trend_analyzer.analyze(
            metric_name=self.time_series_data["metric_name"],
            values=self.time_series_data["values"],
            timestamps=self.time_series_data["timestamps"],
            trend_method="auto",
            seasonality=True
        )
        first_execution_time = time.time() - start_time
        
        # 缓存结果
        self.cache_manager.set(cache_key, trend_result, ttl=300)
        
        # 验证缓存中存在该键
        cached_value = self.cache_manager.get(cache_key)
        self.assertIsNotNone(cached_value)
        self.assertEqual(cached_value["metric_name"], trend_result["metric_name"])
        self.assertEqual(cached_value["trend"]["trend_type"], trend_result["trend"]["trend_type"])
        
        # 从缓存中获取结果，并验证速度更快
        start_time = time.time()
        cached_result = self.cache_manager.get(cache_key)
        cached_execution_time = time.time() - start_time
        
        # 验证从缓存获取比重新计算快
        self.assertLess(cached_execution_time, first_execution_time)
        
        # 获取缓存统计
        stats = self.cache_manager.get_stats()
        self.assertGreaterEqual(stats["hits"], 1)
        
        logger.info("缓存系统集成测试完成")
    
    def test_003_async_task_integration(self):
        """测试异步任务服务与分析器的集成"""
        logger.info("开始测试异步任务服务集成")
        
        # 定义异步任务函数
        def async_trend_analysis(task_args):
            trend_analyzer = TrendAnalyzer()
            result = trend_analyzer.analyze(**task_args)
            return result
        
        # 提交异步任务
        task_args = {
            "metric_name": self.time_series_data["metric_name"],
            "values": self.time_series_data["values"],
            "timestamps": self.time_series_data["timestamps"],
            "trend_method": "auto",
            "seasonality": True
        }
        
        task_id = self.task_service.submit_task(
            func=async_trend_analysis,
            args=(task_args,),
            priority=TaskPriority.NORMAL
        )
        
        # 等待任务完成
        max_wait_time = 10  # 最大等待10秒
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            task_status = self.task_service.get_task_status(task_id)
            if task_status["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            time.sleep(0.5)
        
        # 验证任务状态和结果
        task_status = self.task_service.get_task_status(task_id)
        self.assertEqual(task_status["status"], TaskStatus.COMPLETED)
        
        # 获取任务结果
        task_result = self.task_service.get_task_result(task_id)
        self.assertIsNotNone(task_result)
        self.assertEqual(task_result["metric_name"], self.time_series_data["metric_name"])
        self.assertEqual(task_result["trend"]["trend_type"], "increasing")
        
        logger.info("异步任务服务集成测试完成")
    
    def test_004_api_to_core_integration(self):
        """测试API层到核心分析器的集成"""
        logger.info("开始测试API到核心分析器集成")
        
        # 发送趋势分析请求
        trend_response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=self.time_series_data
        )
        
        # 验证响应
        self.assertEqual(trend_response.status_code, status.HTTP_200_OK)
        trend_data = trend_response.json()
        self.assertTrue(trend_data["success"])
        self.assertEqual(trend_data["data"]["metric_name"], self.time_series_data["metric_name"])
        
        # 发送相关性分析请求
        correlation_response = self.client.post(
            "/api/v1/correlation",
            headers=self.headers,
            json=self.correlation_data
        )
        
        # 验证响应
        self.assertEqual(correlation_response.status_code, status.HTTP_200_OK)
        correlation_data = correlation_response.json()
        self.assertTrue(correlation_data["success"])
        self.assertEqual(correlation_data["data"]["primary_metric_name"], self.correlation_data["primary_metric"]["name"])
        
        # 发送归因分析请求
        attribution_response = self.client.post(
            "/api/v1/attribution",
            headers=self.headers,
            json=self.attribution_data
        )
        
        # 验证响应
        self.assertEqual(attribution_response.status_code, status.HTTP_200_OK)
        attribution_data = attribution_response.json()
        self.assertTrue(attribution_data["success"])
        self.assertEqual(attribution_data["data"]["metric_name"], self.attribution_data["metric_name"])
        
        logger.info("API到核心分析器集成测试完成")
    
    def test_005_end_to_end_analysis_to_export(self):
        """测试从分析到导出的端到端集成流程"""
        logger.info("开始测试端到端分析到导出流程")
        
        # 1. 趋势分析
        trend_response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=self.time_series_data
        )
        trend_data = trend_response.json()["data"]
        
        # 2. 预测分析
        prediction_request = self.time_series_data.copy()
        prediction_request["forecast_periods"] = 3
        prediction_request["confidence_level"] = 0.95
        
        prediction_response = self.client.post(
            "/api/v1/prediction",
            headers=self.headers,
            json=prediction_request
        )
        prediction_data = prediction_response.json()["data"]
        
        # 3. 相关性分析
        correlation_response = self.client.post(
            "/api/v1/correlation",
            headers=self.headers,
            json=self.correlation_data
        )
        correlation_data = correlation_response.json()["data"]
        
        # 4. 归因分析
        attribution_response = self.client.post(
            "/api/v1/attribution",
            headers=self.headers,
            json=self.attribution_data
        )
        attribution_data = attribution_response.json()["data"]
        
        # 5. 智能建议
        suggestion_request = {
            "metric_analysis": {
                "metric_name": self.time_series_data["metric_name"],
                "current_value": self.time_series_data["values"][-1],
                "previous_value": self.time_series_data["values"][-2],
                "change_rate": (self.time_series_data["values"][-1] - self.time_series_data["values"][-2]) / self.time_series_data["values"][-2],
                "change_type": "increase"
            },
            "attribution_analysis": attribution_data,
            "prediction_analysis": prediction_data,
            "min_confidence": 0.6,
            "max_suggestions": 5
        }
        
        suggestion_response = self.client.post(
            "/api/v1/suggestion",
            headers=self.headers,
            json=suggestion_request
        )
        suggestion_data = suggestion_response.json()["data"]
        
        # 6. 导出结果
        export_request = {
            "format": "json",
            "data": {
                "trend_analysis": trend_data,
                "correlation_analysis": correlation_data,
                "attribution_analysis": attribution_data,
                "prediction_analysis": prediction_data,
                "suggestions": suggestion_data
            },
            "filename": f"integration_test_export_{int(time.time())}",
            "include_metadata": True
        }
        
        export_response = self.client.post(
            "/api/v1/export/result",
            headers=self.headers,
            json=export_request
        )
        
        # 验证导出响应
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        export_data = export_response.json()
        self.assertTrue(export_data["success"])
        self.assertIn("file_url", export_data["data"])
        self.assertIn("file_name", export_data["data"])
        
        # 7. 下载导出文件
        file_name = export_data["data"]["file_name"]
        download_response = self.client.get(
            f"/api/v1/export/download?filename={file_name}",
            headers=self.headers
        )
        
        # 验证下载响应
        self.assertEqual(download_response.status_code, status.HTTP_200_OK)
        self.assertEqual(download_response.headers["Content-Type"], "application/json")
        
        # 验证文件内容
        try:
            export_content = json.loads(download_response.content)
            self.assertIn("trend_analysis", export_content)
            self.assertIn("correlation_analysis", export_content)
            self.assertIn("attribution_analysis", export_content)
            self.assertIn("prediction_analysis", export_content)
            self.assertIn("suggestions", export_content)
        except json.JSONDecodeError:
            self.fail("导出的JSON文件格式无效")
        
        logger.info("端到端分析到导出流程测试完成")
    
    def test_006_performance_optimization_integration(self):
        """测试性能优化模块与分析器的集成"""
        logger.info("开始测试性能优化模块集成")
        
        from data_insight.utils.performance import parallel_process, timer, data_chunker, MemoryOptimizer
        
        # 1. 使用计时器测量执行时间
        with timer() as t:
            self.trend_analyzer.analyze(
                metric_name=self.time_series_data["metric_name"],
                values=self.time_series_data["values"],
                timestamps=self.time_series_data["timestamps"]
            )
        
        # 验证计时器工作正常
        self.assertGreater(t.elapsed, 0)
        
        # 2. 使用并行处理优化
        # 创建较大的数据集进行并行处理测试
        large_data = {
            "metric_name": "并行处理测试",
            "values": [i * 0.5 for i in range(100)],
            "timestamps": [f"2023-01-{(i%30)+1:02d}" for i in range(100)]
        }
        
        # 创建需要并行处理的数据块
        chunks = list(data_chunker(large_data["values"], 20))
        
        # 定义处理函数
        def process_chunk(chunk):
            return sum(chunk)
        
        # 使用并行处理
        results = parallel_process(process_chunk, chunks)
        
        # 验证并行处理结果
        self.assertEqual(len(results), len(chunks))
        self.assertAlmostEqual(sum(results), sum(large_data["values"]))
        
        # 3. 使用内存优化器
        optimizer = MemoryOptimizer()
        
        # 创建DataFrame
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=1000),
            'values': np.random.rand(1000),
            'category': np.random.choice(['A', 'B', 'C', 'D'], 1000)
        })
        
        # 优化DataFrame内存使用
        optimized_df = optimizer.optimize_dataframe(df)
        
        # 验证优化后的DataFrame包含相同的数据
        self.assertEqual(len(optimized_df), len(df))
        self.assertTrue(all(optimized_df['values'] == df['values']))
        
        logger.info("性能优化模块集成测试完成")
    
    def test_007_metrics_integration(self):
        """测试指标监控系统的集成"""
        logger.info("开始测试指标监控系统集成")
        
        from data_insight.utils.metrics import get_metrics_registry, increment_request_count, record_request_duration
        
        # 获取指标注册表
        registry = get_metrics_registry()
        
        # 重置指标
        registry.reset()
        
        # 记录API请求
        increment_request_count("/api/test", "GET", 200)
        increment_request_count("/api/test", "POST", 201)
        
        # 记录请求持续时间
        record_request_duration("/api/test", "GET", 0.15)
        
        # 获取指标并验证
        metrics = registry.get_all_metrics()
        
        # 验证请求计数指标
        self.assertIn("api_requests_total", metrics)
        self.assertEqual(metrics["api_requests_total"]["value"], 2)
        
        # 验证请求持续时间指标
        self.assertIn("request_duration_seconds", metrics)
        
        # 验证Prometheus格式的指标
        prometheus_metrics = registry.get_prometheus_metrics()
        self.assertIn("api_requests_total", prometheus_metrics)
        self.assertIn("request_duration_seconds", prometheus_metrics)
        
        logger.info("指标监控系统集成测试完成")


class TestModuleInteractions(unittest.TestCase):
    """模块交互测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        # 初始化测试客户端
        self.client = TestClient(app)
        
        # 测试数据
        self.test_data = {
            "metric_name": "测试指标",
            "values": [10, 12, 15, 14, 16, 18, 20, 22, 24, 23, 25, 28],
            "timestamps": [f"2023-01-{i:02d}" for i in range(1, 13)]
        }
    
    def test_cache_affect_on_performance(self):
        """测试缓存对性能的影响"""
        from data_insight.utils.performance import timer
        from data_insight.utils.cache_manager import CacheManager, CacheBackend
        
        # 创建缓存管理器
        cache = CacheManager(backend=CacheBackend.MEMORY)
        
        # 清除可能的现有缓存
        cache.clear()
        
        # 设置缓存键
        cache_key = f"test_data:{hash(str(self.test_data))}"
        
        # 定义一个模拟耗时操作
        def simulate_expensive_operation(data):
            time.sleep(0.2)  # 模拟计算开销
            return {"result": sum(data["values"])}
        
        # 1. 不使用缓存的执行时间
        with timer() as t1:
            result1 = simulate_expensive_operation(self.test_data)
        
        # 2. 第一次带缓存执行
        with timer() as t2:
            cached_result = cache.get(cache_key)
            if cached_result is None:
                cached_result = simulate_expensive_operation(self.test_data)
                cache.set(cache_key, cached_result)
        
        # 3. 第二次带缓存执行（已有缓存数据）
        with timer() as t3:
            cached_result = cache.get(cache_key)
            if cached_result is None:
                cached_result = simulate_expensive_operation(self.test_data)
                cache.set(cache_key, cached_result)
        
        # 验证结果
        self.assertGreater(t1.elapsed, t3.elapsed)  # 有缓存比无缓存快
        self.assertGreater(t2.elapsed, t3.elapsed)  # 缓存命中比缓存未命中快
        
        # 验证缓存统计
        stats = cache.get_stats()
        self.assertGreaterEqual(stats["hits"], 1)
    
    def test_async_task_with_caching(self):
        """测试异步任务与缓存的交互"""
        from data_insight.services import get_async_task_service, TaskPriority
        from data_insight.utils.cache_manager import get_cache_manager
        
        task_service = get_async_task_service()
        cache_manager = get_cache_manager()
        
        # 清除可能的现有缓存
        cache_manager.clear()
        
        # 设置缓存键
        cache_key = f"async_task:test:{hash(str(self.test_data))}"
        
        # 定义异步任务函数
        def async_task_with_cache(data, cache_key):
            # 检查缓存
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # 模拟计算
            time.sleep(0.2)
            result = {"processed": data["metric_name"], "sum": sum(data["values"])}
            
            # 缓存结果
            cache_manager.set(cache_key, result)
            return result
        
        # 执行异步任务
        task_id = task_service.submit_task(
            func=async_task_with_cache,
            args=(self.test_data, cache_key),
            priority=TaskPriority.NORMAL
        )
        
        # 等待任务完成
        max_wait = 5
        for _ in range(max_wait):
            status = task_service.get_task_status(task_id)
            if status["status"] == "completed":
                break
            time.sleep(0.5)
        
        # 获取任务结果
        result1 = task_service.get_task_result(task_id)
        
        # 验证任务结果
        self.assertEqual(result1["processed"], self.test_data["metric_name"])
        self.assertEqual(result1["sum"], sum(self.test_data["values"]))
        
        # 再次执行任务（应从缓存获取）
        task_id2 = task_service.submit_task(
            func=async_task_with_cache,
            args=(self.test_data, cache_key),
            priority=TaskPriority.NORMAL
        )
        
        # 等待任务完成
        for _ in range(max_wait):
            status = task_service.get_task_status(task_id2)
            if status["status"] == "completed":
                break
            time.sleep(0.5)
        
        # 获取任务结果
        result2 = task_service.get_task_result(task_id2)
        
        # 验证结果是否相同
        self.assertEqual(result1, result2)
        
        # 验证缓存统计
        stats = cache_manager.get_stats()
        self.assertGreaterEqual(stats["hits"], 1)


class TestErrorHandlingIntegration(unittest.TestCase):
    """错误处理集成测试类"""
    
    def setUp(self):
        """测试前准备工作"""
        self.client = TestClient(app)
        self.api_token = os.environ.get("TEST_API_TOKEN", "test-token-for-integration-tests")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Token": self.api_token
        }
    
    def test_validation_error_propagation(self):
        """测试验证错误的传播"""
        # 发送缺少必填字段的请求
        request_data = {
            "metric_name": "测试指标",
            # 缺少values字段
            "timestamps": ["2023-01-01", "2023-01-02", "2023-01-03"]
        }
        
        response = self.client.post(
            "/api/v1/trend/analyze",
            headers=self.headers,
            json=request_data
        )
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error_type"], "ValidationError")
    
    def test_rate_limit_integration(self):
        """测试速率限制的集成"""
        # 配置一个很低的速率限制
        with patch('data_insight.api.middlewares.rate_limiter.RateLimiter.is_allowed', 
                   return_value=(False, 1, 30)):
            response = self.client.get(
                "/api/v1/health",
                headers=self.headers
            )
            
            # 验证速率限制响应
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            data = response.json()
            self.assertFalse(data["success"])
            self.assertEqual(data["error_type"], "RateLimitExceeded")
    
    def test_service_unavailable_handling(self):
        """测试服务不可用的处理"""
        # 模拟Redis服务不可用
        with patch('data_insight.utils.cache_manager.redis.Redis.ping', 
                   side_effect=Exception("Redis connection error")):
            # 尝试使用依赖Redis的功能
            response = self.client.get(
                "/health",
                headers=self.headers
            )
            
            # 验证响应（应该还是成功，但Redis状态为不健康）
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data["status"], "ok")  # 健康检查总体OK
            cache_status = next((s for s in data["services"] if s["name"] == "cache"), None)
            if cache_status:
                self.assertEqual(cache_status["status"], "unhealthy")


if __name__ == '__main__':
    unittest.main() 