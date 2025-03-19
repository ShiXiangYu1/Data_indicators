#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存管理器测试
============

测试缓存管理功能。
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from data_insight.utils.cache_manager import (
    CacheKey, BaseCache, MemoryCache, RedisCache, CacheManager, cached
)
from data_insight.utils import get_cache_manager


class TestCacheKey(unittest.TestCase):
    """测试缓存键生成器"""
    
    def test_generate(self):
        """测试生成缓存键"""
        # 测试简单参数
        key = CacheKey.generate("test", {"a": 1, "b": "2"})
        self.assertTrue(key.startswith("test:"))
        self.assertEqual(len(key), len("test:") + 32)  # MD5哈希长度为32
        
        # 测试相同参数生成相同键
        key2 = CacheKey.generate("test", {"a": 1, "b": "2"})
        self.assertEqual(key, key2)
        
        # 测试不同参数生成不同键
        key3 = CacheKey.generate("test", {"a": 1, "b": "3"})
        self.assertNotEqual(key, key3)
        
        # 测试不同前缀生成不同键
        key4 = CacheKey.generate("test2", {"a": 1, "b": "2"})
        self.assertNotEqual(key, key4)
    
    def test_parse(self):
        """测试解析缓存键"""
        # 测试正常解析
        prefix, hash_str = CacheKey.parse("test:abc123")
        self.assertEqual(prefix, "test")
        self.assertEqual(hash_str, "abc123")
        
        # 测试无冒号的键
        prefix, hash_str = CacheKey.parse("testkey")
        self.assertEqual(prefix, "testkey")
        self.assertEqual(hash_str, "")
        
        # 测试空键
        prefix, hash_str = CacheKey.parse("")
        self.assertEqual(prefix, "")
        self.assertEqual(hash_str, "")


class TestMemoryCache(unittest.TestCase):
    """测试内存缓存"""
    
    def setUp(self):
        """测试前准备"""
        self.cache = MemoryCache(cache_type="ttl", maxsize=100, ttl=1)  # 使用1秒的TTL便于测试
    
    def test_set_get(self):
        """测试设置和获取缓存"""
        # 设置缓存
        self.assertTrue(self.cache.set("key1", "value1"))
        
        # 获取缓存
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # 获取不存在的缓存
        self.assertIsNone(self.cache.get("nonexistent"))
    
    def test_exists(self):
        """测试检查缓存是否存在"""
        # 设置缓存
        self.cache.set("key1", "value1")
        
        # 检查存在的缓存
        self.assertTrue(self.cache.exists("key1"))
        
        # 检查不存在的缓存
        self.assertFalse(self.cache.exists("nonexistent"))
    
    def test_delete(self):
        """测试删除缓存"""
        # 设置缓存
        self.cache.set("key1", "value1")
        
        # 删除缓存
        self.assertTrue(self.cache.delete("key1"))
        self.assertFalse(self.cache.exists("key1"))
        
        # 删除不存在的缓存
        self.assertFalse(self.cache.delete("nonexistent"))
    
    def test_clear(self):
        """测试清空缓存"""
        # 设置多个缓存
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # 清空缓存
        self.assertTrue(self.cache.clear())
        
        # 检查缓存是否已清空
        self.assertFalse(self.cache.exists("key1"))
        self.assertFalse(self.cache.exists("key2"))
    
    def test_ttl(self):
        """测试缓存过期"""
        # 设置带过期时间的缓存
        self.cache.set("key1", "value1")  # 使用默认TTL (1秒)
        
        # 立即获取，应该存在
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # 等待缓存过期
        time.sleep(1.5)
        
        # 再次获取，应该已过期
        self.assertIsNone(self.cache.get("key1"))
    
    def test_stats(self):
        """测试缓存统计信息"""
        # 设置缓存
        self.cache.set("key1", "value1")
        
        # 获取缓存（命中）
        self.cache.get("key1")
        
        # 获取不存在的缓存（未命中）
        self.cache.get("nonexistent")
        
        # 获取统计信息
        stats = self.cache.get_stats()
        
        # 验证统计信息
        self.assertEqual(stats["type"], "memory")
        self.assertEqual(stats["cache_type"], "ttl")
        self.assertEqual(stats["maxsize"], 100)
        self.assertEqual(stats["currsize"], 1)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["sets"], 1)
        self.assertEqual(stats["deletes"], 0)
        self.assertEqual(stats["hit_ratio"], 0.5)


class TestRedisCacheFallback(unittest.TestCase):
    """测试Redis缓存回退到内存缓存的情况"""
    
    @patch('data_insight.utils.cache_manager.REDIS_AVAILABLE', False)
    def test_fallback(self):
        """测试Redis不可用时回退到内存缓存"""
        cache = RedisCache()
        
        # 验证类型为内存缓存
        self.assertEqual(cache.type, "memory")
        
        # 测试基本功能
        self.assertTrue(cache.set("key1", "value1"))
        self.assertEqual(cache.get("key1"), "value1")
        self.assertTrue(cache.exists("key1"))
        self.assertTrue(cache.delete("key1"))
        self.assertFalse(cache.exists("key1"))


class TestCacheManager(unittest.TestCase):
    """测试缓存管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.config = {
            'memory': {
                'cache_type': 'ttl',
                'maxsize': 100,
                'ttl': 60
            },
            'redis': {
                'enabled': False  # 禁用Redis缓存
            }
        }
        self.cache_manager = CacheManager(self.config)
    
    def test_get_cache(self):
        """测试获取缓存实例"""
        # 获取默认缓存
        cache = self.cache_manager.get_cache()
        self.assertIsInstance(cache, MemoryCache)
        
        # 获取内存缓存
        cache = self.cache_manager.get_cache('memory')
        self.assertIsInstance(cache, MemoryCache)
        
        # 获取不存在的缓存类型，应返回默认缓存
        cache = self.cache_manager.get_cache('nonexistent')
        self.assertIsInstance(cache, MemoryCache)
    
    def test_cache_operations(self):
        """测试缓存操作"""
        # 设置缓存
        self.assertTrue(self.cache_manager.set("key1", "value1"))
        
        # 获取缓存
        self.assertEqual(self.cache_manager.get("key1"), "value1")
        
        # 检查缓存是否存在
        self.assertTrue(self.cache_manager.exists("key1"))
        
        # 删除缓存
        self.assertTrue(self.cache_manager.delete("key1"))
        self.assertFalse(self.cache_manager.exists("key1"))
        
        # 设置多个缓存
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        
        # 清空缓存
        self.assertTrue(self.cache_manager.clear())
        self.assertFalse(self.cache_manager.exists("key1"))
        self.assertFalse(self.cache_manager.exists("key2"))
    
    def test_get_stats(self):
        """测试获取统计信息"""
        # 设置缓存
        self.cache_manager.set("key1", "value1")
        
        # 获取所有缓存统计信息
        stats = self.cache_manager.get_stats()
        self.assertIn('memory', stats)
        
        # 获取内存缓存统计信息
        memory_stats = self.cache_manager.get_stats('memory')
        self.assertEqual(memory_stats["type"], "memory")
        self.assertEqual(memory_stats["cache_type"], "ttl")


class TestCachedDecorator(unittest.TestCase):
    """测试缓存装饰器"""
    
    def setUp(self):
        """测试前准备"""
        # 创建一个计数函数，用于测试缓存是否生效
        self.counter = 0
        
        @cached(expire=1)  # 1秒过期
        def test_function(a, b=2):
            self.counter += 1
            return a + b
        
        self.test_function = test_function
    
    @patch('data_insight.utils.get_cache_manager')
    def test_cached_decorator(self, mock_get_cache_manager):
        """测试缓存装饰器"""
        # 创建模拟缓存管理器
        mock_cache_manager = MagicMock()
        mock_get_cache_manager.return_value = mock_cache_manager
        
        # 模拟缓存未命中
        mock_cache_manager.get.return_value = None
        
        # 首次调用，缓存未命中，执行函数
        result = self.test_function(1, 2)
        self.assertEqual(result, 3)
        self.assertEqual(self.counter, 1)
        
        # 验证get和set调用
        mock_cache_manager.get.assert_called_once()
        mock_cache_manager.set.assert_called_once()
        
        # 重置模拟对象
        mock_cache_manager.reset_mock()
        
        # 模拟缓存命中
        mock_cache_manager.get.return_value = 3
        
        # 再次调用，缓存命中，不执行函数
        result = self.test_function(1, 2)
        self.assertEqual(result, 3)
        self.assertEqual(self.counter, 1)  # 计数器不变
        
        # 验证get调用，不调用set
        mock_cache_manager.get.assert_called_once()
        mock_cache_manager.set.assert_not_called()


if __name__ == '__main__':
    unittest.main() 