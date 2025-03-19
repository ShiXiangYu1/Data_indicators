#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异步任务处理服务
=============

提供异步任务处理功能，支持长时间运行的分析任务。
"""

import os
import uuid
import time
import json
import logging
import threading
import traceback
from typing import Dict, Any, List, Callable, Optional, Tuple, Union
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future

# 设置日志记录器
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"     # 等待执行
    RUNNING = "running"     # 正在执行
    COMPLETED = "completed" # 执行完成
    FAILED = "failed"       # 执行失败
    TIMEOUT = "timeout"     # 执行超时
    CANCELED = "canceled"   # 已取消


class TaskPriority(int, Enum):
    """任务优先级枚举"""
    LOW = 0      # 低优先级
    NORMAL = 1   # 普通优先级
    HIGH = 2     # 高优先级
    URGENT = 3   # 紧急优先级


class Task:
    """
    异步任务
    
    表示一个异步执行的任务。
    """
    
    def __init__(self, task_id: str, func: Callable, args: Tuple = None, 
                 kwargs: Dict[str, Any] = None, priority: TaskPriority = TaskPriority.NORMAL,
                 timeout: int = None, callback: Callable = None, error_callback: Callable = None,
                 metadata: Dict[str, Any] = None):
        """
        初始化任务
        
        参数:
            task_id (str): 任务ID
            func (Callable): 要执行的函数
            args (Tuple, optional): 位置参数
            kwargs (Dict[str, Any], optional): 关键字参数
            priority (TaskPriority, optional): 任务优先级
            timeout (int, optional): 超时时间（秒）
            callback (Callable, optional): 完成回调函数
            error_callback (Callable, optional): 错误回调函数
            metadata (Dict[str, Any], optional): 任务元数据
        """
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.callback = callback
        self.error_callback = error_callback
        self.metadata = metadata or {}
        
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.traceback = None
        
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
        self.progress = 0
        self.message = "等待执行"
        self.future = None  # Future对象
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为字典
        
        返回:
            Dict[str, Any]: 任务字典
        """
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time": (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None,
            "wait_time": (self.started_at - self.created_at).total_seconds() if self.started_at else (datetime.now() - self.created_at).total_seconds(),
        }
    
    def __lt__(self, other):
        """用于优先级比较"""
        if isinstance(other, Task):
            return self.priority.value > other.priority.value  # 高优先级排在前面
        return NotImplemented


class ProgressReporter:
    """
    进度报告器
    
    用于报告任务执行进度。
    """
    
    def __init__(self, task: Task):
        """
        初始化进度报告器
        
        参数:
            task (Task): 关联的任务
        """
        self.task = task
    
    def update(self, progress: float, message: str = None) -> None:
        """
        更新进度
        
        参数:
            progress (float): 进度值（0-100）
            message (str, optional): 进度消息
        """
        if progress < 0:
            progress = 0
        elif progress > 100:
            progress = 100
        
        self.task.progress = progress
        if message:
            self.task.message = message
        
        logger.debug(f"任务 {self.task.task_id} 进度: {progress:.1f}%, {message or ''}")


class AsyncTaskService:
    """
    异步任务服务
    
    管理和执行异步任务。
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AsyncTaskService, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_workers: int = None, task_cache_size: int = 1000):
        """
        初始化异步任务服务
        
        参数:
            max_workers (int, optional): 最大工作线程数，默认为CPU核心数的2倍
            task_cache_size (int, optional): 任务缓存大小
        """
        if self._initialized:
            return
        
        # 确定最大工作线程数
        if max_workers is None:
            import multiprocessing
            max_workers = multiprocessing.cpu_count() * 2
        
        self.max_workers = max_workers
        self.task_cache_size = task_cache_size
        
        # 任务字典和优先级队列
        self.tasks = {}
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 清理线程
        self.cleanup_thread = None
        self.stop_cleanup = False
        
        self._initialized = True
        logger.info(f"初始化异步任务服务，最大工作线程数: {max_workers}")
        
        # 启动清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self) -> None:
        """启动清理线程"""
        if self.cleanup_thread is not None and self.cleanup_thread.is_alive():
            return
        
        self.stop_cleanup = False
        self.cleanup_thread = threading.Thread(target=self._cleanup_tasks, daemon=True)
        self.cleanup_thread.start()
        logger.debug("启动任务清理线程")
    
    def _cleanup_tasks(self) -> None:
        """清理过期任务"""
        while not self.stop_cleanup:
            try:
                # 当任务数量超过缓存大小时，清理已完成且超过1小时的任务
                if len(self.tasks) > self.task_cache_size:
                    now = datetime.now()
                    expired_tasks = []
                    
                    for task_id, task in self.tasks.items():
                        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT, TaskStatus.CANCELED):
                            if task.completed_at and (now - task.completed_at) > timedelta(hours=1):
                                expired_tasks.append(task_id)
                    
                    # 删除过期任务
                    for task_id in expired_tasks:
                        del self.tasks[task_id]
                    
                    if expired_tasks:
                        logger.debug(f"清理了 {len(expired_tasks)} 个过期任务")
            except Exception as e:
                logger.error(f"清理任务时发生错误: {str(e)}")
            
            # 每5分钟检查一次
            time.sleep(300)
    
    def _execute_task(self, task: Task) -> None:
        """
        执行任务
        
        参数:
            task (Task): 要执行的任务
        """
        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.message = "正在执行"
        
        # 创建进度报告器
        progress_reporter = ProgressReporter(task)
        
        try:
            # 添加进度报告器到关键字参数
            task.kwargs['progress_reporter'] = progress_reporter
            
            # 执行任务
            if task.timeout:
                # 如果设置了超时时间
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"任务执行超时 (>{task.timeout}秒)")
                
                # 设置超时处理
                original_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(task.timeout)
                
                try:
                    result = task.func(*task.args, **task.kwargs)
                finally:
                    # 恢复原始处理器并取消闹钟
                    signal.signal(signal.SIGALRM, original_handler)
                    signal.alarm(0)
            else:
                # 没有超时时间
                result = task.func(*task.args, **task.kwargs)
            
            # 任务成功完成
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.message = "执行完成"
            task.progress = 100
            
            # 调用回调函数
            if task.callback:
                try:
                    task.callback(task.task_id, result)
                except Exception as e:
                    logger.error(f"调用回调函数时发生错误: {str(e)}")
        
        except TimeoutError as e:
            # 任务超时
            task.status = TaskStatus.TIMEOUT
            task.error = str(e)
            task.traceback = traceback.format_exc()
            task.message = "执行超时"
            
            logger.warning(f"任务 {task.task_id} 执行超时")
            
            # 调用错误回调函数
            if task.error_callback:
                try:
                    task.error_callback(task.task_id, e)
                except Exception as cb_error:
                    logger.error(f"调用错误回调函数时发生错误: {str(cb_error)}")
        
        except Exception as e:
            # 任务执行失败
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.traceback = traceback.format_exc()
            task.message = f"执行失败: {str(e)}"
            
            logger.error(f"任务 {task.task_id} 执行失败: {str(e)}")
            logger.debug(task.traceback)
            
            # 调用错误回调函数
            if task.error_callback:
                try:
                    task.error_callback(task.task_id, e)
                except Exception as cb_error:
                    logger.error(f"调用错误回调函数时发生错误: {str(cb_error)}")
        
        finally:
            # 更新完成时间
            task.completed_at = datetime.now()
    
    def submit_task(self, func: Callable, args: Tuple = None, kwargs: Dict[str, Any] = None,
                   priority: TaskPriority = TaskPriority.NORMAL, timeout: int = None,
                   callback: Callable = None, error_callback: Callable = None,
                   metadata: Dict[str, Any] = None, task_id: str = None) -> str:
        """
        提交任务
        
        参数:
            func (Callable): 要执行的函数
            args (Tuple, optional): 位置参数
            kwargs (Dict[str, Any], optional): 关键字参数
            priority (TaskPriority, optional): 任务优先级
            timeout (int, optional): 超时时间（秒）
            callback (Callable, optional): 完成回调函数
            error_callback (Callable, optional): 错误回调函数
            metadata (Dict[str, Any], optional): 任务元数据
            task_id (str, optional): 自定义任务ID
            
        返回:
            str: 任务ID
        """
        # 生成任务ID
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # 创建任务
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            callback=callback,
            error_callback=error_callback,
            metadata=metadata
        )
        
        # 提交到线程池
        task.future = self.executor.submit(self._execute_task, task)
        
        # 存储任务
        self.tasks[task_id] = task
        
        logger.info(f"提交任务 {task_id}，优先级: {priority.name}")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Optional[Task]: 任务对象，如果不存在则返回None
        """
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Dict[str, Any]: 任务状态字典
            
        异常:
            ValueError: 如果任务不存在
        """
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"任务 {task_id} 不存在")
        
        return task.to_dict()
    
    def get_task_result(self, task_id: str, wait: bool = False, timeout: int = None) -> Any:
        """
        获取任务结果
        
        参数:
            task_id (str): 任务ID
            wait (bool, optional): 是否等待任务完成
            timeout (int, optional): 等待超时时间（秒）
            
        返回:
            Any: 任务结果
            
        异常:
            ValueError: 如果任务不存在
            RuntimeError: 如果任务执行失败
        """
        task = self.get_task(task_id)
        if task is None:
            raise ValueError(f"任务 {task_id} 不存在")
        
        if wait and task.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT, TaskStatus.CANCELED):
            try:
                # 等待任务完成
                task.future.result(timeout=timeout)
            except Exception:
                # 忽略异常，后面会检查任务状态
                pass
        
        # 检查任务状态
        if task.status == TaskStatus.FAILED:
            raise RuntimeError(f"任务执行失败: {task.error}\n{task.traceback}")
        elif task.status == TaskStatus.TIMEOUT:
            raise TimeoutError(f"任务执行超时: {task.error}")
        elif task.status == TaskStatus.CANCELED:
            raise RuntimeError("任务已取消")
        elif task.status != TaskStatus.COMPLETED:
            if wait:
                raise TimeoutError(f"等待任务完成超时")
            else:
                raise RuntimeError(f"任务尚未完成，当前状态: {task.status.value}")
        
        return task.result
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        参数:
            task_id (str): 任务ID
            
        返回:
            bool: 是否成功取消
        """
        task = self.get_task(task_id)
        if task is None:
            return False
        
        # 只能取消等待执行的任务
        if task.status == TaskStatus.PENDING:
            if task.future and task.future.cancel():
                task.status = TaskStatus.CANCELED
                task.completed_at = datetime.now()
                task.message = "已取消"
                logger.info(f"取消任务 {task_id}")
                return True
        
        return False
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务
        
        返回:
            List[Dict[str, Any]]: 任务状态字典列表
        """
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        获取活动任务
        
        返回:
            List[Dict[str, Any]]: 活动任务状态字典列表
        """
        return [task.to_dict() for task in self.tasks.values() 
                if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING)]
    
    def shutdown(self, wait: bool = True) -> None:
        """
        关闭异步任务服务
        
        参数:
            wait (bool, optional): 是否等待所有任务完成
        """
        # 停止清理线程
        self.stop_cleanup = True
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=1)
        
        # 关闭线程池
        self.executor.shutdown(wait=wait)
        
        logger.info("关闭异步任务服务")


# 全局异步任务服务实例
_async_task_service = None


def get_async_task_service() -> AsyncTaskService:
    """
    获取异步任务服务实例
    
    返回:
        AsyncTaskService: 异步任务服务实例
    """
    global _async_task_service
    
    if _async_task_service is None:
        _async_task_service = AsyncTaskService()
    
    return _async_task_service 