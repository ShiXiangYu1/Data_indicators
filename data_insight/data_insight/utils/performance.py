#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能优化模块
==========

提供性能优化工具，包括内存优化、并行处理和执行时间跟踪等功能。
"""

import os
import gc
import time
import logging
import functools
import multiprocessing
import concurrent.futures
from typing import Dict, Any, List, Callable, Optional, Union, Tuple, TypeVar, Iterable, Iterator
from contextlib import contextmanager

import numpy as np
import pandas as pd

# 创建日志记录器
logger = logging.getLogger(__name__)

# 泛型类型定义
T = TypeVar('T')
R = TypeVar('R')


@contextmanager
def timer(name: str = "操作"):
    """
    计时上下文管理器
    
    用于测量代码块的执行时间。
    
    参数:
        name (str): 操作名称
    
    示例:
        with timer("数据加载"):
            df = pd.read_csv("data.csv")
    """
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"{name}完成，耗时: {elapsed_time:.4f}秒")


def time_it(name: Optional[str] = None):
    """
    计时装饰器
    
    用于测量函数的执行时间。
    
    参数:
        name (str, optional): 操作名称，如果为None则使用函数名
    
    返回:
        Callable: 装饰器函数
    
    示例:
        @time_it("数据处理")
        def process_data(data):
            # 处理数据
            return processed_data
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            function_name = name if name else func.__name__
            with timer(function_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def parallel_process(
    func: Callable[[T], R],
    items: List[T],
    max_workers: Optional[int] = None,
    use_processes: bool = False,
    chunk_size: Optional[int] = None
) -> List[R]:
    """
    并行处理列表项
    
    对列表中的每个项目并行应用函数。
    
    参数:
        func (Callable): 要应用的函数
        items (List): 要处理的项目列表
        max_workers (int, optional): 最大工作线程/进程数，如果为None则使用CPU核心数
        use_processes (bool): 是否使用进程而不是线程
        chunk_size (int, optional): 分块大小，如果为None则自动计算
        
    返回:
        List: 处理结果列表
    """
    if not items:
        return []
    
    # 如果未指定最大工作线程/进程数，则使用CPU核心数
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)
    
    # 如果项目数量较少，直接使用单线程
    if len(items) <= 1 or max_workers <= 1:
        return [func(item) for item in items]
    
    # 确定合适的分块大小
    if chunk_size is None:
        chunk_size = max(1, len(items) // (max_workers * 4))
    
    # 选择适当的执行器类型
    executor_class = concurrent.futures.ProcessPoolExecutor if use_processes else concurrent.futures.ThreadPoolExecutor
    
    # 并行处理
    results = []
    with executor_class(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_item = {executor.submit(func, item): i for i, item in enumerate(items)}
        
        # 收集结果，保持原始顺序
        results = [None] * len(items)
        for future in concurrent.futures.as_completed(future_to_item):
            index = future_to_item[future]
            try:
                results[index] = future.result()
            except Exception as e:
                logger.error(f"处理项目 {index} 时发生错误: {str(e)}")
                results[index] = None
    
    return results


def data_chunker(data: Union[List[T], pd.DataFrame, np.ndarray], chunk_size: int) -> Iterator[Union[List[T], pd.DataFrame, np.ndarray]]:
    """
    数据分块器
    
    将大型数据集分割成较小的块进行处理。
    
    参数:
        data: 要分块的数据
        chunk_size (int): 分块大小
        
    返回:
        Iterator: 数据块的迭代器
    """
    if isinstance(data, pd.DataFrame):
        # 对DataFrame进行分块
        for i in range(0, len(data), chunk_size):
            yield data.iloc[i:i+chunk_size]
    
    elif isinstance(data, np.ndarray):
        # 对NumPy数组进行分块
        for i in range(0, len(data), chunk_size):
            yield data[i:i+chunk_size]
    
    else:
        # 对列表或其他可迭代对象进行分块
        for i in range(0, len(data), chunk_size):
            yield data[i:i+chunk_size]


class MemoryOptimizer:
    """
    内存优化器
    
    提供各种内存优化技术，减少大型数据集的内存使用。
    """
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame, category_threshold: float = 0.5, verbose: bool = False) -> pd.DataFrame:
        """
        优化DataFrame的内存使用
        
        将适当的列转换为更内存高效的数据类型。
        
        参数:
            df (pd.DataFrame): 要优化的DataFrame
            category_threshold (float): 将列转换为类别类型的唯一值比例阈值
            verbose (bool): 是否打印详细信息
            
        返回:
            pd.DataFrame: 优化后的DataFrame
        """
        start_mem = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        if verbose:
            logger.info(f"原始DataFrame内存使用: {start_mem:.2f} MB")
        
        # 复制DataFrame以避免修改原始数据
        result = df.copy()
        
        # 对每一列进行优化
        for col in result.columns:
            col_type = result[col].dtype
            
            # 数值列优化
            if pd.api.types.is_numeric_dtype(col_type):
                # 整数优化
                if pd.api.types.is_integer_dtype(col_type):
                    min_val = result[col].min()
                    max_val = result[col].max()
                    
                    # 选择最合适的整数类型
                    if min_val >= 0:
                        if max_val < 2**8:
                            result[col] = result[col].astype(np.uint8)
                        elif max_val < 2**16:
                            result[col] = result[col].astype(np.uint16)
                        elif max_val < 2**32:
                            result[col] = result[col].astype(np.uint32)
                        else:
                            result[col] = result[col].astype(np.uint64)
                    else:
                        if min_val >= -2**7 and max_val < 2**7:
                            result[col] = result[col].astype(np.int8)
                        elif min_val >= -2**15 and max_val < 2**15:
                            result[col] = result[col].astype(np.int16)
                        elif min_val >= -2**31 and max_val < 2**31:
                            result[col] = result[col].astype(np.int32)
                        else:
                            result[col] = result[col].astype(np.int64)
                
                # 浮点数优化
                elif pd.api.types.is_float_dtype(col_type):
                    # 检查是否可以使用float32而不是float64
                    result[col] = result[col].astype(np.float32)
            
            # 字符串列优化
            elif pd.api.types.is_object_dtype(col_type) or pd.api.types.is_string_dtype(col_type):
                # 计算唯一值的比例
                unique_ratio = result[col].nunique() / len(result)
                
                # 如果唯一值比例较低，将列转换为类别类型
                if unique_ratio <= category_threshold:
                    result[col] = result[col].astype('category')
        
        # 计算优化后的内存使用
        end_mem = result.memory_usage(deep=True).sum() / (1024 * 1024)
        reduction = 100 * (start_mem - end_mem) / start_mem
        
        if verbose:
            logger.info(f"优化后DataFrame内存使用: {end_mem:.2f} MB")
            logger.info(f"内存减少: {reduction:.2f}%")
        
        return result
    
    @staticmethod
    def clear_memory() -> None:
        """
        清理内存
        
        强制进行垃圾收集并尝试释放未使用的内存。
        """
        # 强制垃圾收集
        gc.collect()
        
        # 在Linux系统上尝试释放内存
        if hasattr(os, "posix_fadvise"):
            # 通知操作系统不再需要的内存
            try:
                os.system("echo 1 > /proc/sys/vm/drop_caches")
            except:
                pass


def memoize(maxsize: int = 128, ttl: Optional[int] = None):
    """
    记忆化装饰器
    
    缓存函数的返回值，避免重复计算。
    
    参数:
        maxsize (int): 最大缓存条目数
        ttl (int, optional): 缓存生存时间（秒），如果为None则永不过期
        
    返回:
        Callable: 装饰器函数
    """
    cache = {}
    expires = {}  # 用于存储过期时间
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 为基本类型创建键
            key = str(args) + str(sorted(kwargs.items()))
            
            # 检查是否在缓存中且未过期
            if key in cache:
                if ttl is None or time.time() - expires.get(key, 0) < ttl:
                    return cache[key]
            
            # 计算结果
            result = func(*args, **kwargs)
            
            # 更新缓存
            cache[key] = result
            
            # 更新过期时间
            if ttl is not None:
                expires[key] = time.time()
            
            # 如果超过最大缓存大小，移除最早的条目
            if len(cache) > maxsize:
                oldest_key = next(iter(cache))
                del cache[oldest_key]
                if ttl is not None and oldest_key in expires:
                    del expires[oldest_key]
            
            return result
        
        return wrapper
    
    return decorator


def lazy_property(fn):
    """
    惰性属性装饰器
    
    延迟计算属性值，直到第一次访问。
    
    参数:
        fn (Callable): 属性计算函数
        
    返回:
        property: 惰性属性
    """
    attr_name = '_lazy_' + fn.__name__
    
    @property
    @functools.wraps(fn)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    
    return _lazy_property


def batch_decorator(batch_size: int = 1000):
    """
    批处理装饰器
    
    将列表输入分批处理，适用于处理大型输入列表的函数。
    
    参数:
        batch_size (int): 批处理大小
        
    返回:
        Callable: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(items, *args, **kwargs):
            if not isinstance(items, list):
                return func(items, *args, **kwargs)
            
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_result = func(batch, *args, **kwargs)
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                else:
                    results.append(batch_result)
            
            return results
        
        return wrapper
    
    return decorator


def get_memory_usage() -> Dict[str, Any]:
    """
    获取当前进程的内存使用情况
    
    返回:
        Dict[str, Any]: 内存使用信息
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss / (1024 * 1024),  # 物理内存使用（MB）
            "vms": memory_info.vms / (1024 * 1024),  # 虚拟内存使用（MB）
            "percent": process.memory_percent(),  # 内存使用百分比
            "cpu_percent": process.cpu_percent(),  # CPU使用百分比
            "num_threads": process.num_threads(),  # 线程数
        }
    except ImportError:
        logger.warning("psutil库未安装，无法获取详细内存使用信息")
        import resource
        return {
            "memory_usage": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,  # 最大常驻集大小（MB）
        }
    except Exception as e:
        logger.error(f"获取内存使用信息时发生错误: {str(e)}")
        return {
            "error": str(e)
        } 