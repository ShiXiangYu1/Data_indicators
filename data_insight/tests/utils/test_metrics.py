#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
监控指标模块测试
==============

测试监控指标模块的功能。
"""

import unittest
from unittest.mock import patch, MagicMock
import time

from data_insight.utils.metrics import (
    MetricType, 
    MetricsRegistry, 
    get_metrics_registry,
    increment_request_count,
    record_request_duration,
    increment_cache_hit,
    increment_cache_miss,
    increment_async_task,
    record_async_task_duration,
    increment_analysis_request,
    record_analysis_duration,
)


class TestMetricsRegistry(unittest.TestCase):
    """测试指标注册表"""
    
    def setUp(self):
        """测试前准备"""
        # 创建一个新的注册表实例，避免使用单例
        with patch.object(MetricsRegistry, '_instance', None):
            self.registry = MetricsRegistry()
    
    def test_singleton(self):
        """测试单例模式"""
        registry1 = MetricsRegistry()
        registry2 = MetricsRegistry()
        self.assertIs(registry1, registry2)
    
    def test_register(self):
        """测试注册指标"""
        # 注册一个不带标签的指标
        self.registry.register(
            "test_counter",
            "测试计数器",
            MetricType.COUNTER
        )
        
        # 注册一个带标签的指标
        self.registry.register(
            "test_gauge",
            "测试仪表盘",
            MetricType.GAUGE,
            ["label1", "label2"]
        )
        
        # 验证指标已注册
        self.assertEqual(self.registry._descriptions["test_counter"], "测试计数器")
        self.assertEqual(self.registry._metric_types["test_counter"], MetricType.COUNTER)
        self.assertEqual(self.registry._labels["test_counter"], [])
        
        self.assertEqual(self.registry._descriptions["test_gauge"], "测试仪表盘")
        self.assertEqual(self.registry._metric_types["test_gauge"], MetricType.GAUGE)
        self.assertEqual(self.registry._labels["test_gauge"], ["label1", "label2"])
    
    def test_get_set(self):
        """测试获取和设置指标值"""
        # 注册指标
        self.registry.register("test_counter", "测试计数器", MetricType.COUNTER)
        self.registry.register("test_gauge", "测试仪表盘", MetricType.GAUGE, ["label1", "label2"])
        
        # 设置和获取不带标签的指标
        self.registry.set("test_counter", 10)
        self.assertEqual(self.registry.get("test_counter"), 10)
        
        # 设置和获取带标签的指标
        self.registry.set("test_gauge", 20, {"label1": "value1", "label2": "value2"})
        self.assertEqual(
            self.registry.get("test_gauge", {"label1": "value1", "label2": "value2"}),
            20
        )
        
        # 测试不存在的指标
        with self.assertRaises(KeyError):
            self.registry.get("non_existent")
        
        # 测试缺少标签
        with self.assertRaises(ValueError):
            self.registry.get("test_gauge")
    
    def test_inc_dec(self):
        """测试增加和减少指标值"""
        # 注册指标
        self.registry.register("test_counter", "测试计数器", MetricType.COUNTER)
        self.registry.register("test_gauge", "测试仪表盘", MetricType.GAUGE)
        
        # 增加计数器
        self.registry.inc("test_counter", 5)
        self.assertEqual(self.registry.get("test_counter"), 5)
        
        self.registry.inc("test_counter")  # 默认增加1
        self.assertEqual(self.registry.get("test_counter"), 6)
        
        # 增加和减少仪表盘
        self.registry.inc("test_gauge", 10)
        self.assertEqual(self.registry.get("test_gauge"), 10)
        
        self.registry.dec("test_gauge", 3)
        self.assertEqual(self.registry.get("test_gauge"), 7)
        
        # 计数器不能减少
        with self.assertRaises(ValueError):
            self.registry.dec("test_counter")
        
        # 不能将计数器设置为较小的值
        with self.assertRaises(ValueError):
            self.registry.set("test_counter", 5)  # 当前值是6
    
    def test_reset(self):
        """测试重置指标"""
        # 注册指标
        self.registry.register("test_counter", "测试计数器", MetricType.COUNTER)
        self.registry.register("test_gauge", "测试仪表盘", MetricType.GAUGE, ["label"])
        
        # 设置指标值
        self.registry.set("test_counter", 10)
        self.registry.set("test_gauge", 20, {"label": "value"})
        
        # 重置指标
        self.registry.reset()
        
        # 验证指标已重置
        self.assertEqual(self.registry.get("test_counter"), 0)
        self.assertEqual(self.registry.get("test_gauge", {"label": "value"}), 0)
    
    def test_prometheus_format(self):
        """测试Prometheus格式输出"""
        # 注册指标
        self.registry.register("test_counter", "测试计数器", MetricType.COUNTER)
        self.registry.register("test_gauge", "测试仪表盘", MetricType.GAUGE, ["label"])
        
        # 设置指标值
        self.registry.set("test_counter", 10)
        self.registry.set("test_gauge", 20, {"label": "value"})
        
        # 获取Prometheus格式输出
        prometheus_output = self.registry.get_prometheus_metrics()
        
        # 验证输出包含指标信息
        self.assertIn("# HELP test_counter 测试计数器", prometheus_output)
        self.assertIn("# TYPE test_counter counter", prometheus_output)
        self.assertIn("test_counter 10", prometheus_output)
        
        self.assertIn("# HELP test_gauge 测试仪表盘", prometheus_output)
        self.assertIn("# TYPE test_gauge gauge", prometheus_output)
        self.assertIn('test_gauge{label="value"} 20', prometheus_output)


class TestMetricHelpers(unittest.TestCase):
    """测试指标辅助函数"""
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_increment_request_count(self, mock_get_registry):
        """测试增加请求计数"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        increment_request_count("/api/test", "GET", 200)
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("api_requests_total", labels={
            "endpoint": "/api/test",
            "method": "GET",
            "status": "200"
        })
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_record_request_duration(self, mock_get_registry):
        """测试记录请求处理时间"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        record_request_duration("/api/test", "GET", 0.123)
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("api_request_duration_seconds", value=0.123, labels={
            "endpoint": "/api/test",
            "method": "GET"
        })
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_increment_cache_hit(self, mock_get_registry):
        """测试增加缓存命中计数"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        increment_cache_hit("memory")
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("cache_hits_total", labels={"cache_type": "memory"})
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_increment_cache_miss(self, mock_get_registry):
        """测试增加缓存未命中计数"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        increment_cache_miss("redis")
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("cache_misses_total", labels={"cache_type": "redis"})
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_increment_async_task(self, mock_get_registry):
        """测试增加异步任务计数"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        increment_async_task("completed")
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("async_tasks_total", labels={"status": "completed"})
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_record_async_task_duration(self, mock_get_registry):
        """测试记录异步任务执行时间"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        record_async_task_duration("analysis", 1.5)
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("async_task_duration_seconds", value=1.5, labels={
            "task_type": "analysis"
        })
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_increment_analysis_request(self, mock_get_registry):
        """测试增加分析请求计数"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        increment_analysis_request("trend")
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("analysis_requests_total", labels={"analysis_type": "trend"})
    
    @patch('data_insight.utils.metrics.get_metrics_registry')
    def test_record_analysis_duration(self, mock_get_registry):
        """测试记录分析处理时间"""
        # 创建模拟注册表
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        
        # 调用辅助函数
        record_analysis_duration("attribution", 2.5)
        
        # 验证调用了正确的方法
        mock_registry.inc.assert_called_once_with("analysis_duration_seconds", value=2.5, labels={
            "analysis_type": "attribution"
        })


class TestMetricsIntegration(unittest.TestCase):
    """测试指标集成功能"""
    
    def test_get_metrics_registry(self):
        """测试获取指标注册表实例"""
        # 重置单例
        with patch('data_insight.utils.metrics._metrics_registry', None):
            # 获取注册表实例
            registry = get_metrics_registry()
            
            # 验证实例类型
            self.assertIsInstance(registry, MetricsRegistry)
            
            # 验证基础指标已注册
            self.assertIn("process_uptime_seconds", registry._metrics)
            self.assertIn("api_requests_total", registry._metrics)
            self.assertIn("cache_hits_total", registry._metrics)


if __name__ == '__main__':
    unittest.main() 