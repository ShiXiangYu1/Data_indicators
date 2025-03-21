#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
监控指标模块
==========

收集和导出系统监控指标，支持Prometheus格式。
"""

import time
import threading
import os
import psutil
from typing import Dict, Any, List, Optional, Set
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)


class MetricType:
    """指标类型定义"""
    COUNTER = "counter"  # 只增不减的计数器
    GAUGE = "gauge"      # 可增可减的仪表盘
    HISTOGRAM = "histogram"  # 直方图，记录数值分布
    SUMMARY = "summary"  # 汇总，类似直方图但提供分位数


class MetricsRegistry:
    """
    指标注册表
    
    管理系统中所有监控指标。
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._metrics = {}
                cls._instance._descriptions = {}
                cls._instance._metric_types = {}
                cls._instance._labels = {}
                cls._instance._start_time = time.time()
            return cls._instance
    
    def register(self, name: str, description: str, metric_type: str, 
                 labels: Optional[List[str]] = None, default_value: float = 0.0) -> None:
        """
        注册一个新指标
        
        参数:
            name (str): 指标名称
            description (str): 指标描述
            metric_type (str): 指标类型，如counter、gauge
            labels (List[str], optional): 标签列表
            default_value (float, optional): 默认值
        """
        if labels is None:
            labels = []

        if name in self._metrics:
            logger.warning(f"指标 {name} 已存在，将被覆盖")
        
        self._metrics[name] = {}
        self._descriptions[name] = description
        self._metric_types[name] = metric_type
        self._labels[name] = labels
        
        # 如果没有标签，则初始化为默认值
        if not labels:
            self._metrics[name] = default_value
    
    def get(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """
        获取指标值
        
        参数:
            name (str): 指标名称
            labels (Dict[str, str], optional): 标签键值对
            
        返回:
            float: 指标值
        
        异常:
            KeyError: 指标不存在
        """
        if name not in self._metrics:
            raise KeyError(f"指标 {name} 未注册")
        
        if not self._labels[name]:
            return self._metrics[name]
        
        if labels is None:
            raise ValueError(f"指标 {name} 需要标签 {self._labels[name]}")
        
        label_key = self._make_label_key(labels)
        if label_key not in self._metrics[name]:
            # 如果标签组合不存在，则初始化为0
            self._metrics[name][label_key] = 0.0
            
        return self._metrics[name][label_key]
    
    def set(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        设置指标值
        
        参数:
            name (str): 指标名称
            value (float): 指标值
            labels (Dict[str, str], optional): 标签键值对
            
        异常:
            KeyError: 指标不存在
            ValueError: 指标类型为counter但value小于当前值
        """
        if name not in self._metrics:
            raise KeyError(f"指标 {name} 未注册")
        
        # Counter类型只能增加，不能减少
        if self._metric_types[name] == MetricType.COUNTER and self._get_current_value(name, labels) > value:
            raise ValueError(f"计数器 {name} 只能增加，不能减少")
        
        if not self._labels[name]:
            self._metrics[name] = value
            return
        
        if labels is None:
            raise ValueError(f"指标 {name} 需要标签 {self._labels[name]}")
        
        label_key = self._make_label_key(labels)
        self._metrics[name][label_key] = value
    
    def inc(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        增加指标值
        
        参数:
            name (str): 指标名称
            value (float, optional): 增加的值，默认为1.0
            labels (Dict[str, str], optional): 标签键值对
            
        异常:
            KeyError: 指标不存在
        """
        current = self._get_current_value(name, labels)
        self.set(name, current + value, labels)
    
    def dec(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        减少指标值(仅适用于gauge类型)
        
        参数:
            name (str): 指标名称
            value (float, optional): 减少的值，默认为1.0
            labels (Dict[str, str], optional): 标签键值对
            
        异常:
            KeyError: 指标不存在
            ValueError: 指标类型为counter
        """
        if name not in self._metrics:
            raise KeyError(f"指标 {name} 未注册")
        
        if self._metric_types[name] == MetricType.COUNTER:
            raise ValueError(f"计数器 {name} 不能减少")
        
        current = self._get_current_value(name, labels)
        self.set(name, current - value, labels)
    
    def _get_current_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """获取当前指标值，如果不存在则返回0"""
        try:
            return self.get(name, labels)
        except KeyError:
            return 0.0
    
    def _make_label_key(self, labels: Dict[str, str]) -> str:
        """将标签字典转换为字符串键"""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        获取所有指标数据
        
        返回:
            Dict[str, Any]: 包含所有指标数据的字典
        """
        result = {}
        for name in self._metrics:
            result[name] = {
                "value": self._metrics[name],
                "description": self._descriptions[name],
                "type": self._metric_types[name],
                "labels": self._labels[name]
            }
        return result
    
    def get_prometheus_metrics(self) -> str:
        """
        获取Prometheus格式的指标数据
        
        返回:
            str: Prometheus格式的指标数据
        """
        lines = []
        
        # 添加系统基础指标
        self._add_system_metrics()
        
        # 添加运行时间指标
        uptime = time.time() - self._start_time
        if "process_uptime_seconds" in self._metrics:
            self.set("process_uptime_seconds", uptime)
        
        # 转换指标为Prometheus格式
        for name, metric_data in self._metrics.items():
            # 添加帮助信息和类型信息
            lines.append(f"# HELP {name} {self._descriptions.get(name, '')}")
            lines.append(f"# TYPE {name} {self._metric_types.get(name, 'untyped')}")
            
            # 添加指标值
            if not self._labels[name]:
                # 没有标签的简单指标
                lines.append(f"{name} {metric_data}")
            else:
                # 有标签的指标
                for label_key, value in metric_data.items():
                    if not label_key:  # 跳过空标签键
                        continue
                    
                    # 解析标签串为字典
                    label_pairs = {}
                    for pair in label_key.split("|"):
                        if "=" in pair:
                            k, v = pair.split("=", 1)
                            label_pairs[k] = v
                    
                    # 构建标签字符串
                    label_str = ",".join(f'{k}="{v}"' for k, v in label_pairs.items())
                    lines.append(f"{name}{{{label_str}}} {value}")
        
        return "\n".join(lines)
    
    def _add_system_metrics(self) -> None:
        """添加系统基础指标"""
        # 进程指标
        process = psutil.Process(os.getpid())
        
        # CPU使用率
        if "process_cpu_usage_percent" in self._metrics:
            self.set("process_cpu_usage_percent", process.cpu_percent(interval=0.1))
        
        # 内存使用
        if "process_memory_usage_bytes" in self._metrics:
            mem_info = process.memory_info()
            self.set("process_memory_usage_bytes", mem_info.rss)
        
        # 打开的文件数
        if "process_open_files" in self._metrics:
            self.set("process_open_files", len(process.open_files()))
        
        # 系统内存
        if "system_memory_usage_percent" in self._metrics:
            self.set("system_memory_usage_percent", psutil.virtual_memory().percent)
        
        # 系统CPU
        if "system_cpu_usage_percent" in self._metrics:
            self.set("system_cpu_usage_percent", psutil.cpu_percent(interval=0.1))
    
    def reset(self) -> None:
        """
        重置所有指标
        """
        for name in self._metrics:
            if not self._labels[name]:
                self._metrics[name] = 0.0
            else:
                self._metrics[name] = {}


# 全局指标注册表实例
_metrics_registry = None


def get_metrics_registry() -> MetricsRegistry:
    """
    获取全局指标注册表实例
    
    返回:
        MetricsRegistry: 指标注册表实例
    """
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = MetricsRegistry()
        # 注册系统基础指标
        _register_system_metrics(_metrics_registry)
    return _metrics_registry


def _register_system_metrics(registry: MetricsRegistry) -> None:
    """
    注册系统基础指标
    
    参数:
        registry (MetricsRegistry): 指标注册表实例
    """
    # 进程指标
    registry.register(
        "process_uptime_seconds",
        "进程运行时间（秒）",
        MetricType.GAUGE
    )
    
    registry.register(
        "process_cpu_usage_percent",
        "进程CPU使用率（百分比）",
        MetricType.GAUGE
    )
    
    registry.register(
        "process_memory_usage_bytes",
        "进程内存使用量（字节）",
        MetricType.GAUGE
    )
    
    registry.register(
        "process_open_files",
        "进程打开的文件数",
        MetricType.GAUGE
    )
    
    # 系统指标
    registry.register(
        "system_memory_usage_percent",
        "系统内存使用率（百分比）",
        MetricType.GAUGE
    )
    
    registry.register(
        "system_cpu_usage_percent",
        "系统CPU使用率（百分比）",
        MetricType.GAUGE
    )
    
    # API请求指标
    registry.register(
        "api_requests_total",
        "API请求总数",
        MetricType.COUNTER,
        ["endpoint", "method", "status"]
    )
    
    registry.register(
        "api_request_duration_seconds",
        "API请求处理时间（秒）",
        MetricType.HISTOGRAM,
        ["endpoint", "method"]
    )
    
    # 缓存指标
    registry.register(
        "cache_hits_total",
        "缓存命中次数",
        MetricType.COUNTER,
        ["cache_type"]
    )
    
    registry.register(
        "cache_misses_total",
        "缓存未命中次数",
        MetricType.COUNTER,
        ["cache_type"]
    )
    
    registry.register(
        "cache_size",
        "缓存大小",
        MetricType.GAUGE,
        ["cache_type"]
    )
    
    # 异步任务指标
    registry.register(
        "async_tasks_total",
        "异步任务总数",
        MetricType.COUNTER,
        ["status"]
    )
    
    registry.register(
        "async_task_duration_seconds",
        "异步任务执行时间（秒）",
        MetricType.HISTOGRAM,
        ["task_type"]
    )
    
    # 分析API指标
    registry.register(
        "analysis_requests_total",
        "分析请求总数",
        MetricType.COUNTER,
        ["analysis_type"]
    )
    
    registry.register(
        "analysis_duration_seconds",
        "分析处理时间（秒）",
        MetricType.HISTOGRAM,
        ["analysis_type"]
    )


def increment_request_count(endpoint: str, method: str, status: int) -> None:
    """
    增加API请求计数
    
    参数:
        endpoint (str): API端点
        method (str): 请求方法（GET, POST等）
        status (int): HTTP状态码
    """
    registry = get_metrics_registry()
    registry.inc("api_requests_total", labels={
        "endpoint": endpoint,
        "method": method,
        "status": str(status)
    })


def record_request_duration(endpoint: str, method: str, duration: float) -> None:
    """
    记录API请求处理时间
    
    参数:
        endpoint (str): API端点
        method (str): 请求方法（GET, POST等）
        duration (float): 处理时间（秒）
    """
    registry = get_metrics_registry()
    registry.inc("api_request_duration_seconds", value=duration, labels={
        "endpoint": endpoint,
        "method": method
    })


def increment_cache_hit(cache_type: str) -> None:
    """
    增加缓存命中计数
    
    参数:
        cache_type (str): 缓存类型（memory, redis等）
    """
    registry = get_metrics_registry()
    registry.inc("cache_hits_total", labels={"cache_type": cache_type})


def increment_cache_miss(cache_type: str) -> None:
    """
    增加缓存未命中计数
    
    参数:
        cache_type (str): 缓存类型（memory, redis等）
    """
    registry = get_metrics_registry()
    registry.inc("cache_misses_total", labels={"cache_type": cache_type})


def increment_async_task(status: str) -> None:
    """
    增加异步任务计数
    
    参数:
        status (str): 任务状态（pending, running, completed, failed等）
    """
    registry = get_metrics_registry()
    registry.inc("async_tasks_total", labels={"status": status})


def record_async_task_duration(task_type: str, duration: float) -> None:
    """
    记录异步任务执行时间
    
    参数:
        task_type (str): 任务类型
        duration (float): 执行时间（秒）
    """
    registry = get_metrics_registry()
    registry.inc("async_task_duration_seconds", value=duration, labels={
        "task_type": task_type
    })


def increment_analysis_request(analysis_type: str) -> None:
    """
    增加分析请求计数
    
    参数:
        analysis_type (str): 分析类型（trend, attribution, root_cause等）
    """
    registry = get_metrics_registry()
    registry.inc("analysis_requests_total", labels={"analysis_type": analysis_type})


def record_analysis_duration(analysis_type: str, duration: float) -> None:
    """
    记录分析处理时间
    
    参数:
        analysis_type (str): 分析类型（trend, attribution, root_cause等）
        duration (float): 处理时间（秒）
    """
    registry = get_metrics_registry()
    registry.inc("analysis_duration_seconds", value=duration, labels={
        "analysis_type": analysis_type
    })


def set_cache_size(cache_type: str, size: int) -> None:
    """
    设置缓存大小指标
    
    参数:
        cache_type (str): 缓存类型
        size (int): 缓存大小
    """
    registry = get_metrics_registry()
    registry.set("cache_size", size, {"type": cache_type})


def record_cache_operation_time(cache_type: str, operation: str, duration: float) -> None:
    """
    记录缓存操作时间
    
    参数:
        cache_type (str): 缓存类型
        operation (str): 操作类型
        duration (float): 操作耗时(秒)
    """
    registry = get_metrics_registry()
    registry.set("cache_operation_duration_seconds", duration, {"type": cache_type, "operation": operation}) 