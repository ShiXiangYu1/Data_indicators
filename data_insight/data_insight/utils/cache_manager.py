#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存管理器
========

提供高性能的缓存功能，支持多种缓存后端（内存、Redis和文件系统）。
"""

import os
import time
import hashlib
import pickle
import json
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable, Union, List, Tuple
from enum import Enum

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from data_insight.utils.metrics import (
    increment_cache_hit,
    increment_cache_miss,
    set_cache_size,
    record_cache_operation_time
)

# 创建日志记录器
logger = logging.getLogger(__name__)


class CacheBackend(str, Enum):
    """缓存后端类型"""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"


class CacheManager:
    """
    缓存管理器
    
    提供高性能的缓存功能，支持多种后端，包括内存缓存、Redis缓存和文件系统缓存。
    支持键过期、最大缓存大小限制和缓存统计。
    """
    
    def __init__(
        self,
        backend: CacheBackend = CacheBackend.MEMORY,
        ttl: int = 3600,
        max_size: int = 10000,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        redis_db: int = 0,
        file_cache_dir: str = "tmp/cache",
        namespace: str = "data_insight"
    ):
        """
        初始化缓存管理器
        
        参数:
            backend (CacheBackend): 缓存后端类型
            ttl (int): 默认缓存生存时间（秒）
            max_size (int): 最大缓存条目数（仅适用于内存缓存）
            redis_host (str): Redis主机地址
            redis_port (int): Redis端口
            redis_password (str, optional): Redis密码
            redis_db (int): Redis数据库索引
            file_cache_dir (str): 文件缓存目录
            namespace (str): 缓存命名空间，用于隔离不同应用的缓存
        """
        self.backend = backend
        self.ttl = ttl
        self.max_size = max_size
        self.namespace = namespace
        
        # 缓存统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "clears": 0
        }
        
        # 初始化缓存后端
        if backend == CacheBackend.MEMORY:
            # 内存缓存
            self.cache = {}  # 键值对存储
            self.expirations = {}  # 过期时间存储
            self.lru_list = []  # 最近最少使用列表
            
        elif backend == CacheBackend.REDIS:
            # Redis缓存
            if not REDIS_AVAILABLE:
                raise ImportError("Redis缓存需要安装redis库，请使用'pip install redis'安装")
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=False
            )
            try:
                self.redis_client.ping()
            except redis.ConnectionError as e:
                logger.error(f"无法连接到Redis: {str(e)}")
                raise
            
        elif backend == CacheBackend.FILE:
            # 文件系统缓存
            self.file_cache_dir = os.path.join(file_cache_dir, namespace)
            os.makedirs(self.file_cache_dir, exist_ok=True)
            
            # 文件缓存索引
            self.index_file = os.path.join(self.file_cache_dir, "index.json")
            if os.path.exists(self.index_file):
                try:
                    with open(self.index_file, "r") as f:
                        self.cache_index = json.load(f)
                except Exception as e:
                    logger.error(f"无法加载缓存索引: {str(e)}")
                    self.cache_index = {}
            else:
                self.cache_index = {}
        
        logger.info(f"缓存管理器已初始化，使用{backend}后端")
    
    def _generate_key(self, key: str) -> str:
        """
        为缓存键生成命名空间前缀
        
        参数:
            key (str): 原始键
            
        返回:
            str: 带命名空间的键
        """
        return f"{self.namespace}:{key}"
    
    def _generate_file_path(self, key: str) -> str:
        """
        生成缓存文件路径
        
        参数:
            key (str): 缓存键
            
        返回:
            str: 文件路径
        """
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.file_cache_dir, key_hash)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        参数:
            key (str): 缓存键
            default (Any): 默认值，如果键不存在则返回
            
        返回:
            Any: 缓存的值或默认值
        """
        start_time = time.time()
        namespaced_key = self._generate_key(key)
        
        try:
            if self.backend == CacheBackend.MEMORY:
                # 检查键是否存在和是否过期
                if namespaced_key in self.cache:
                    # 检查是否过期
                    if namespaced_key in self.expirations and self.expirations[namespaced_key] < time.time():
                        # 已过期，删除并返回默认值
                        del self.cache[namespaced_key]
                        del self.expirations[namespaced_key]
                        if namespaced_key in self.lru_list:
                            self.lru_list.remove(namespaced_key)
                        self.stats["misses"] += 1
                        increment_cache_miss(self.backend.value)
                        return default
                    
                    # 未过期，更新LRU列表
                    if namespaced_key in self.lru_list:
                        self.lru_list.remove(namespaced_key)
                    self.lru_list.append(namespaced_key)
                    
                    # 返回缓存值
                    self.stats["hits"] += 1
                    increment_cache_hit(self.backend.value)
                    return self.cache[namespaced_key]
                else:
                    # 键不存在
                    self.stats["misses"] += 1
                    increment_cache_miss(self.backend.value)
                    return default
            
            elif self.backend == CacheBackend.REDIS:
                # 从Redis获取值
                value = self.redis_client.get(namespaced_key)
                if value is not None:
                    # 缓存命中
                    self.stats["hits"] += 1
                    increment_cache_hit(self.backend.value)
                    try:
                        return pickle.loads(value)
                    except Exception as e:
                        logger.error(f"无法反序列化缓存值: {str(e)}")
                        return default
                else:
                    # 缓存未命中
                    self.stats["misses"] += 1
                    increment_cache_miss(self.backend.value)
                    return default
            
            elif self.backend == CacheBackend.FILE:
                # 检查索引中是否存在键
                if namespaced_key in self.cache_index:
                    # 检查是否过期
                    if "expiration" in self.cache_index[namespaced_key] and \
                       self.cache_index[namespaced_key]["expiration"] < time.time():
                        # 已过期，删除并返回默认值
                        self._remove_file_cache(namespaced_key)
                        self.stats["misses"] += 1
                        increment_cache_miss(self.backend.value)
                        return default
                    
                    # 未过期，从文件读取
                    try:
                        file_path = self._generate_file_path(namespaced_key)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                # 更新访问时间
                                self.cache_index[namespaced_key]["last_accessed"] = time.time()
                                self._save_cache_index()
                                
                                # 缓存命中
                                self.stats["hits"] += 1
                                increment_cache_hit(self.backend.value)
                                return pickle.load(f)
                        else:
                            # 文件不存在但索引存在，清理索引
                            del self.cache_index[namespaced_key]
                            self._save_cache_index()
                            self.stats["misses"] += 1
                            increment_cache_miss(self.backend.value)
                            return default
                    except Exception as e:
                        logger.error(f"无法读取文件缓存: {str(e)}")
                        self.stats["misses"] += 1
                        increment_cache_miss(self.backend.value)
                        return default
                else:
                    # 键不存在
                    self.stats["misses"] += 1
                    increment_cache_miss(self.backend.value)
                    return default
            
            else:
                return default
                
        finally:
            operation_time = time.time() - start_time
            record_cache_operation_time("get", operation_time)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        参数:
            key (str): 缓存键
            value (Any): 要缓存的值
            ttl (int, optional): 缓存生存时间（秒），如果为None则使用默认值
            
        返回:
            bool: 是否设置成功
        """
        start_time = time.time()
        namespaced_key = self._generate_key(key)
        
        # 使用默认TTL如果未指定
        if ttl is None:
            ttl = self.ttl
        
        try:
            if self.backend == CacheBackend.MEMORY:
                # 检查缓存大小限制
                if len(self.cache) >= self.max_size and namespaced_key not in self.cache:
                    # 移除最近最少使用的项
                    if self.lru_list:
                        oldest_key = self.lru_list.pop(0)
                        if oldest_key in self.cache:
                            del self.cache[oldest_key]
                        if oldest_key in self.expirations:
                            del self.expirations[oldest_key]
                
                # 设置缓存值
                self.cache[namespaced_key] = value
                
                # 设置过期时间
                if ttl > 0:
                    self.expirations[namespaced_key] = time.time() + ttl
                elif ttl <= 0 and namespaced_key in self.expirations:
                    # 永不过期或清除过期时间
                    del self.expirations[namespaced_key]
                
                # 更新LRU列表
                if namespaced_key in self.lru_list:
                    self.lru_list.remove(namespaced_key)
                self.lru_list.append(namespaced_key)
                
                # 设置缓存大小
                self._update_cache_size()
                
                self.stats["sets"] += 1
                return True
            
            elif self.backend == CacheBackend.REDIS:
                try:
                    # 序列化值
                    serialized_value = pickle.dumps(value)
                    
                    # 设置到Redis
                    if ttl > 0:
                        self.redis_client.setex(namespaced_key, ttl, serialized_value)
                    else:
                        self.redis_client.set(namespaced_key, serialized_value)
                    
                    self.stats["sets"] += 1
                    return True
                except Exception as e:
                    logger.error(f"无法设置Redis缓存: {str(e)}")
                    return False
            
            elif self.backend == CacheBackend.FILE:
                try:
                    # 生成文件路径
                    file_path = self._generate_file_path(namespaced_key)
                    
                    # 保存到文件
                    with open(file_path, "wb") as f:
                        pickle.dump(value, f)
                    
                    # 更新索引
                    self.cache_index[namespaced_key] = {
                        "file_path": file_path,
                        "created": time.time(),
                        "last_accessed": time.time()
                    }
                    
                    # 设置过期时间
                    if ttl > 0:
                        self.cache_index[namespaced_key]["expiration"] = time.time() + ttl
                    elif ttl <= 0 and "expiration" in self.cache_index[namespaced_key]:
                        # 永不过期或清除过期时间
                        del self.cache_index[namespaced_key]["expiration"]
                    
                    # 保存索引
                    self._save_cache_index()
                    
                    self.stats["sets"] += 1
                    return True
                except Exception as e:
                    logger.error(f"无法设置文件缓存: {str(e)}")
                    return False
            
            else:
                return False
                
        finally:
            operation_time = time.time() - start_time
            record_cache_operation_time("set", operation_time)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存键
        
        参数:
            key (str): 缓存键
            
        返回:
            bool: 是否删除成功
        """
        start_time = time.time()
        namespaced_key = self._generate_key(key)
        
        try:
            if self.backend == CacheBackend.MEMORY:
                # 从内存缓存中删除
                if namespaced_key in self.cache:
                    del self.cache[namespaced_key]
                    if namespaced_key in self.expirations:
                        del self.expirations[namespaced_key]
                    if namespaced_key in self.lru_list:
                        self.lru_list.remove(namespaced_key)
                    
                    # 更新缓存大小
                    self._update_cache_size()
                    
                    self.stats["deletes"] += 1
                    return True
                return False
            
            elif self.backend == CacheBackend.REDIS:
                # 从Redis中删除
                result = self.redis_client.delete(namespaced_key)
                if result > 0:
                    self.stats["deletes"] += 1
                return result > 0
            
            elif self.backend == CacheBackend.FILE:
                # 从文件缓存中删除
                if namespaced_key in self.cache_index:
                    result = self._remove_file_cache(namespaced_key)
                    if result:
                        self.stats["deletes"] += 1
                    return result
                return False
            
            else:
                return False
                
        finally:
            operation_time = time.time() - start_time
            record_cache_operation_time("delete", operation_time)
    
    def clear(self) -> bool:
        """
        清空缓存
        
        返回:
            bool: 是否清空成功
        """
        start_time = time.time()
        
        try:
            if self.backend == CacheBackend.MEMORY:
                # 清空内存缓存
                self.cache.clear()
                self.expirations.clear()
                self.lru_list.clear()
                
                # 更新缓存大小
                self._update_cache_size()
                
                self.stats["clears"] += 1
                return True
            
            elif self.backend == CacheBackend.REDIS:
                # 清空Redis命名空间下的所有键
                keys = self.redis_client.keys(f"{self.namespace}:*")
                if keys:
                    self.redis_client.delete(*keys)
                
                self.stats["clears"] += 1
                return True
            
            elif self.backend == CacheBackend.FILE:
                # 清空文件缓存
                for key in list(self.cache_index.keys()):
                    self._remove_file_cache(key)
                
                # 清空索引
                self.cache_index.clear()
                self._save_cache_index()
                
                self.stats["clears"] += 1
                return True
            
            else:
                return False
                
        finally:
            operation_time = time.time() - start_time
            record_cache_operation_time("clear", operation_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            Dict[str, Any]: 缓存统计信息
        """
        if self.backend == CacheBackend.MEMORY:
            # 计算当前缓存大小
            current_size = len(self.cache)
            total_memory = 0
            
            # 估算内存使用
            try:
                import sys
                for key, value in self.cache.items():
                    total_memory += sys.getsizeof(key) + sys.getsizeof(value)
            except:
                total_memory = -1
            
            # 计算缓存命中率
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "backend": self.backend,
                "current_size": current_size,
                "max_size": self.max_size,
                "total_memory": total_memory,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "clears": self.stats["clears"],
                "hit_rate": hit_rate
            }
            
        elif self.backend == CacheBackend.REDIS:
            # 计算Redis缓存大小
            keys = self.redis_client.keys(f"{self.namespace}:*")
            current_size = len(keys)
            
            # 获取Redis信息
            try:
                info = self.redis_client.info()
                memory_used = info.get("used_memory", -1)
            except:
                memory_used = -1
            
            # 计算缓存命中率
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "backend": self.backend,
                "current_size": current_size,
                "memory_used": memory_used,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "clears": self.stats["clears"],
                "hit_rate": hit_rate
            }
            
        elif self.backend == CacheBackend.FILE:
            # 计算文件缓存大小
            current_size = len(self.cache_index)
            total_disk_usage = 0
            
            # 计算磁盘使用
            try:
                for key, info in self.cache_index.items():
                    file_path = info.get("file_path")
                    if file_path and os.path.exists(file_path):
                        total_disk_usage += os.path.getsize(file_path)
            except:
                total_disk_usage = -1
            
            # 计算缓存命中率
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "backend": self.backend,
                "current_size": current_size,
                "total_disk_usage": total_disk_usage,
                "cache_dir": self.file_cache_dir,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "clears": self.stats["clears"],
                "hit_rate": hit_rate
            }
            
        else:
            return self.stats
    
    def cleanup_expired(self) -> int:
        """
        清理过期的缓存项
        
        返回:
            int: 清理的项数
        """
        start_time = time.time()
        cleaned_count = 0
        
        try:
            if self.backend == CacheBackend.MEMORY:
                # 清理过期的内存缓存项
                current_time = time.time()
                expired_keys = [
                    key for key, expiry in self.expirations.items()
                    if expiry < current_time
                ]
                
                for key in expired_keys:
                    if key in self.cache:
                        del self.cache[key]
                    if key in self.lru_list:
                        self.lru_list.remove(key)
                    del self.expirations[key]
                    cleaned_count += 1
                
                # 更新缓存大小
                self._update_cache_size()
                
                return cleaned_count
            
            elif self.backend == CacheBackend.REDIS:
                # Redis自动处理过期，无需手动清理
                return 0
            
            elif self.backend == CacheBackend.FILE:
                # 清理过期的文件缓存项
                current_time = time.time()
                expired_keys = [
                    key for key, info in self.cache_index.items()
                    if "expiration" in info and info["expiration"] < current_time
                ]
                
                for key in expired_keys:
                    if self._remove_file_cache(key):
                        cleaned_count += 1
                
                return cleaned_count
            
            else:
                return 0
                
        finally:
            operation_time = time.time() - start_time
            record_cache_operation_time("cleanup", operation_time)
    
    def _remove_file_cache(self, key: str) -> bool:
        """
        删除文件缓存项
        
        参数:
            key (str): 缓存键
            
        返回:
            bool: 是否删除成功
        """
        if key in self.cache_index:
            try:
                # 获取文件路径
                file_path = self.cache_index[key].get("file_path")
                if file_path and os.path.exists(file_path):
                    # 删除文件
                    os.remove(file_path)
                
                # 从索引中删除
                del self.cache_index[key]
                
                # 保存索引
                self._save_cache_index()
                
                return True
            except Exception as e:
                logger.error(f"无法删除文件缓存: {str(e)}")
                return False
        return False
    
    def _save_cache_index(self) -> bool:
        """
        保存缓存索引
        
        返回:
            bool: 是否保存成功
        """
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.cache_index, f)
            return True
        except Exception as e:
            logger.error(f"无法保存缓存索引: {str(e)}")
            return False
    
    def _update_cache_size(self) -> None:
        """
        更新缓存大小指标
        """
        if self.backend == CacheBackend.MEMORY:
            size = len(self.cache)
            set_cache_size(self.backend.value, size)


# 单例缓存管理器实例
_cache_manager = None


def get_cache_manager(config: Optional[Dict[str, Any]] = None) -> CacheManager:
    """
    获取缓存管理器实例
    
    参数:
        config (Dict[str, Any], optional): 配置参数
        
    返回:
        CacheManager: 缓存管理器实例
    """
    global _cache_manager
    
    if _cache_manager is None:
        # 创建默认配置
        default_config = {
            "backend": CacheBackend.MEMORY,
            "ttl": 3600,
            "max_size": 10000,
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_password": None,
            "redis_db": 0,
            "file_cache_dir": "tmp/cache",
            "namespace": "data_insight"
        }
        
        # 合并自定义配置
        if config:
            if "CACHE_BACKEND" in config:
                default_config["backend"] = config["CACHE_BACKEND"]
            if "CACHE_TTL" in config:
                default_config["ttl"] = config["CACHE_TTL"]
            if "CACHE_MAX_SIZE" in config:
                default_config["max_size"] = config["CACHE_MAX_SIZE"]
            if "REDIS_HOST" in config:
                default_config["redis_host"] = config["REDIS_HOST"]
            if "REDIS_PORT" in config:
                default_config["redis_port"] = config["REDIS_PORT"]
            if "REDIS_PASSWORD" in config:
                default_config["redis_password"] = config["REDIS_PASSWORD"]
            if "REDIS_DB" in config:
                default_config["redis_db"] = config["REDIS_DB"]
            if "FILE_CACHE_DIR" in config:
                default_config["file_cache_dir"] = config["FILE_CACHE_DIR"]
            if "CACHE_NAMESPACE" in config:
                default_config["namespace"] = config["CACHE_NAMESPACE"]
        
        # 创建缓存管理器
        try:
            _cache_manager = CacheManager(
                backend=default_config["backend"],
                ttl=default_config["ttl"],
                max_size=default_config["max_size"],
                redis_host=default_config["redis_host"],
                redis_port=default_config["redis_port"],
                redis_password=default_config["redis_password"],
                redis_db=default_config["redis_db"],
                file_cache_dir=default_config["file_cache_dir"],
                namespace=default_config["namespace"]
            )
        except Exception as e:
            logger.error(f"无法创建缓存管理器: {str(e)}")
            
            # 回退到内存缓存
            logger.info("回退到内存缓存")
            _cache_manager = CacheManager(
                backend=CacheBackend.MEMORY,
                ttl=default_config["ttl"],
                max_size=default_config["max_size"],
                namespace=default_config["namespace"]
            )
    
    return _cache_manager


def cache(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    缓存装饰器
    
    用于缓存函数结果。
    
    参数:
        ttl (int, optional): 缓存生存时间（秒）
        key_prefix (str): 缓存键前缀
        
    返回:
        Callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取缓存管理器
            cache_manager = get_cache_manager()
            
            # 生成缓存键
            key = f"{key_prefix}:{func.__name__}:"
            
            # 添加位置参数
            if args:
                key += ":".join(str(arg) for arg in args)
            
            # 添加关键字参数
            if kwargs:
                key += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            # 生成唯一键
            cache_key = hashlib.md5(key.encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 计算函数结果
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator 