#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能优化工具测试
==============

测试性能监控和优化功能。
"""

import unittest
import time
import numpy as np
from unittest.mock import patch, MagicMock

from data_insight.utils.performance import (
    PerformanceMonitor, time_it, data_chunker, parallel_process,
    optimize_numpy_operations, MemoryOptimizer, OptimizationContext
)


class TestPerformanceMonitor(unittest.TestCase):
    """测试性能监控器"""
    
    def setUp(self):
        """测试前准备"""
        self.monitor = PerformanceMonitor()
        self.monitor.reset_metrics()  # 确保测试开始前重置指标
    
    def test_singleton(self):
        """测试单例模式"""
        monitor2 = PerformanceMonitor()
        self.assertIs(self.monitor, monitor2)
    
    def test_time_function(self):
        """测试函数执行时间装饰器"""
        @self.monitor.time_function
        def test_func(sleep_time):
            time.sleep(sleep_time)
            return sleep_time
        
        # 调用函数
        test_func(0.1)
        test_func(0.1)
        
        # 获取指标
        metrics = self.monitor.get_metrics()
        
        # 验证指标
        self.assertIn('test_func', metrics)
        self.assertEqual(metrics['test_func']['calls'], 2)
        self.assertTrue(metrics['test_func']['total_time'] >= 0.2)
        self.assertTrue(metrics['test_func']['min_time'] >= 0.1)
        self.assertTrue(metrics['test_func']['max_time'] >= 0.1)
        self.assertTrue(metrics['test_func']['avg_time'] >= 0.1)
    
    def test_timer(self):
        """测试计时器功能"""
        # 开始计时
        self.monitor.start_timer('test_timer')
        
        # 等待一段时间
        time.sleep(0.1)
        
        # 记录一圈用时
        lap_time = self.monitor.lap_timer('test_timer')
        self.assertTrue(lap_time >= 0.1)
        
        # 等待另一段时间
        time.sleep(0.1)
        
        # 停止计时
        total_time = self.monitor.stop_timer('test_timer')
        self.assertTrue(total_time >= 0.2)
        
        # 测试不存在的计时器
        with self.assertRaises(ValueError):
            self.monitor.lap_timer('nonexistent')
        
        with self.assertRaises(ValueError):
            self.monitor.stop_timer('nonexistent')


class TestTimeIt(unittest.TestCase):
    """测试time_it装饰器"""
    
    def test_time_it_decorator(self):
        """测试time_it装饰器"""
        @time_it
        def test_func(sleep_time):
            time.sleep(sleep_time)
            return sleep_time
        
        # 调用函数
        result = test_func(0.1)
        self.assertEqual(result, 0.1)
    
    def test_time_it_decorator_with_name(self):
        """测试带名称的time_it装饰器"""
        @time_it(name="custom_timer")
        def test_func(sleep_time):
            time.sleep(sleep_time)
            return sleep_time
        
        # 调用函数
        result = test_func(0.1)
        self.assertEqual(result, 0.1)


class TestDataChunker(unittest.TestCase):
    """测试数据分块功能"""
    
    def test_list_chunking(self):
        """测试列表分块"""
        data = list(range(10))
        chunks = list(data_chunker(data, 3))
        
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], [0, 1, 2])
        self.assertEqual(chunks[1], [3, 4, 5])
        self.assertEqual(chunks[2], [6, 7, 8])
        self.assertEqual(chunks[3], [9])
    
    def test_numpy_chunking(self):
        """测试NumPy数组分块"""
        data = np.array(range(10))
        chunks = list(data_chunker(data, 3))
        
        self.assertEqual(len(chunks), 4)
        np.testing.assert_array_equal(chunks[0], np.array([0, 1, 2]))
        np.testing.assert_array_equal(chunks[1], np.array([3, 4, 5]))
        np.testing.assert_array_equal(chunks[2], np.array([6, 7, 8]))
        np.testing.assert_array_equal(chunks[3], np.array([9]))
    
    def test_empty_data(self):
        """测试空数据"""
        data = []
        chunks = list(data_chunker(data, 3))
        self.assertEqual(len(chunks), 0)


class TestParallelProcess(unittest.TestCase):
    """测试并行处理功能"""
    
    def test_empty_data(self):
        """测试空数据列表"""
        def process_func(x):
            return x * 2
        
        result = parallel_process(process_func, [])
        self.assertEqual(result, [])
    
    def test_single_item(self):
        """测试单个数据项"""
        def process_func(x):
            return x * 2
        
        result = parallel_process(process_func, [5])
        self.assertEqual(result, [10])
    
    def test_threading_backend(self):
        """测试线程后端"""
        def process_func(x):
            return x * 2
        
        data = list(range(5))
        result = parallel_process(process_func, data, backend='threading')
        self.assertEqual(result, [0, 2, 4, 6, 8])
    
    def test_with_kwargs(self):
        """测试带关键字参数"""
        def process_func(x, multiplier=2):
            return x * multiplier
        
        data = list(range(5))
        result = parallel_process(process_func, data, multiplier=3)
        self.assertEqual(result, [0, 3, 6, 9, 12])
    
    def test_invalid_backend(self):
        """测试无效后端"""
        def process_func(x):
            return x * 2
        
        with self.assertRaises(ValueError):
            parallel_process(process_func, [1, 2, 3], backend='invalid')


class TestMemoryOptimizer(unittest.TestCase):
    """测试内存优化器"""
    
    def test_reduce_precision(self):
        """测试降低精度"""
        data = np.array([1.1, 2.2, 3.3], dtype=np.float64)
        result = MemoryOptimizer.reduce_precision(data, np.float32)
        
        self.assertEqual(result.dtype, np.float32)
        np.testing.assert_allclose(result, data, rtol=1e-6)
    
    def test_batch_process(self):
        """测试批处理"""
        def square(data):
            return data ** 2
        
        data = np.array(range(10))
        result = MemoryOptimizer.batch_process(square, data, batch_size=3)
        
        np.testing.assert_array_equal(result, data ** 2)


class TestOptimizationContext(unittest.TestCase):
    """测试优化上下文管理器"""
    
    def test_context_manager(self):
        """测试上下文管理器"""
        # 保存原始NumPy错误设置
        original_settings = np.geterr()
        
        # 使用优化上下文
        with OptimizationContext(optimize_memory=True, optimize_cpu=True) as ctx:
            # 在上下文中获取错误设置
            context_settings = np.geterr()
            
            # 验证设置已更改（all 设为 ignore）
            self.assertEqual(context_settings['all'], 'ignore')
        
        # 验证退出上下文后设置已恢复
        restored_settings = np.geterr()
        self.assertEqual(restored_settings, original_settings)


if __name__ == '__main__':
    unittest.main() 