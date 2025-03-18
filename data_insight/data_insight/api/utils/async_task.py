"""
异步任务处理
==========

提供异步处理大数据量请求的功能。
"""

import uuid
import time
import threading
import logging
import traceback
from typing import Dict, Any, Callable, List, Optional, Tuple
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('async_task')


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待处理
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    TIMEOUT = "timeout"      # 超时
    CANCELED = "canceled"    # 已取消


class Task:
    """异步任务类，表示一个异步处理的任务"""
    
    def __init__(self, task_id: str, func: Callable, args: Tuple, kwargs: Dict[str, Any], timeout: int = 300):
        """
        初始化任务
        
        参数:
            task_id (str): 任务ID
            func (Callable): 要执行的函数
            args (Tuple): 位置参数
            kwargs (Dict[str, Any]): 关键字参数
            timeout (int, optional): 超时时间（秒），默认5分钟
        """
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.timeout = timeout
        self.thread = None
    
    def run(self):
        """执行任务"""
        # 更新状态和开始时间
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
        
        # 创建线程执行任务
        self.thread = threading.Thread(target=self._execute)
        self.thread.daemon = True
        self.thread.start()
    
    def _execute(self):
        """实际执行函数的内部方法"""
        try:
            # 执行函数
            self.result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
        except Exception as e:
            # 捕获异常
            self.error = str(e)
            self.status = TaskStatus.FAILED
            logger.error(f"Task {self.task_id} failed: {e}")
            logger.error(traceback.format_exc())
        finally:
            # 更新结束时间
            self.end_time = datetime.now()
            
            # 清理引用，避免内存泄漏
            self.func = None
            self.args = None
            self.kwargs = None
    
    def cancel(self):
        """
        取消任务
        
        返回:
            bool: 是否成功取消
        """
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.CANCELED
            return True
        elif self.status == TaskStatus.RUNNING:
            # 正在运行的任务无法真正取消，只能标记为取消
            self.status = TaskStatus.CANCELED
            # 注意：我们不应该强制终止线程，这可能导致资源泄漏
            return True
        return False
    
    def check_timeout(self):
        """
        检查任务是否超时
        
        返回:
            bool: 是否超时
        """
        if self.status == TaskStatus.RUNNING and self.start_time:
            elapsed = datetime.now() - self.start_time
            if elapsed.total_seconds() > self.timeout:
                self.status = TaskStatus.TIMEOUT
                self.error = f"任务执行超时，超过{self.timeout}秒"
                return True
        return False
    
    def get_info(self):
        """
        获取任务信息
        
        返回:
            Dict[str, Any]: 任务信息
        """
        # 计算运行时间
        duration = None
        if self.start_time:
            if self.end_time:
                duration = (self.end_time - self.start_time).total_seconds()
            else:
                duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "error": self.error
        }


class TaskManager:
    """任务管理器，管理所有异步任务"""
    
    def __init__(self, max_tasks=100, cleanup_interval=300):
        """
        初始化任务管理器
        
        参数:
            max_tasks (int, optional): 最大任务数量，默认100
            cleanup_interval (int, optional): 清理间隔（秒），默认5分钟
        """
        self.tasks = {}
        self.max_tasks = max_tasks
        self.cleanup_interval = cleanup_interval
        self.lock = threading.Lock()
        
        # 启动清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_tasks, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_tasks(self):
        """清理已完成的任务"""
        while True:
            time.sleep(self.cleanup_interval)
            logger.info("开始任务清理")
            
            with self.lock:
                # 获取所有任务ID
                task_ids = list(self.tasks.keys())
                
                # 检查超时的任务
                for task_id in task_ids:
                    task = self.tasks.get(task_id)
                    if task:
                        task.check_timeout()
                
                # 清理已完成、失败、超时或取消的任务
                completed_statuses = [
                    TaskStatus.COMPLETED, 
                    TaskStatus.FAILED,
                    TaskStatus.TIMEOUT,
                    TaskStatus.CANCELED
                ]
                
                # 计算任务完成时间超过一天的任务
                one_day_ago = datetime.now() - timedelta(days=1)
                
                for task_id in task_ids:
                    task = self.tasks.get(task_id)
                    if task and (
                        # 任务已经结束且结束时间超过一天
                        (task.status in completed_statuses and task.end_time and task.end_time < one_day_ago) or
                        # 或者任务创建时间超过一天且从未启动
                        (task.status == TaskStatus.PENDING and task.start_time is None and 
                         task.end_time is None and task.thread is None)
                    ):
                        logger.info(f"清理任务 {task_id}")
                        del self.tasks[task_id]
            
            logger.info(f"任务清理完成。剩余{len(self.tasks)}个任务")
    
    def create_task(self, func, *args, **kwargs):
        """
        创建新任务
        
        参数:
            func (Callable): 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        返回:
            str: 任务ID
        
        异常:
            RuntimeError: 当任务数量超过限制时
        """
        with self.lock:
            # 检查任务数量是否超过限制
            if len(self.tasks) >= self.max_tasks:
                raise RuntimeError(f"任务数量过多。最大允许数量: {self.max_tasks}")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 从kwargs中提取timeout参数，如果有的话
            timeout = kwargs.pop('_timeout', 300)
            
            # 创建任务
            task = Task(task_id, func, args, kwargs, timeout)
            self.tasks[task_id] = task
            
            # 启动任务
            task.run()
            
            return task_id
    
    def get_task(self, task_id):
        """
        获取任务
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Task or None: 任务实例，如果不存在则返回None
        """
        return self.tasks.get(task_id)
    
    def get_task_info(self, task_id):
        """
        获取任务信息
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Dict[str, Any] or None: 任务信息，如果不存在则返回None
        """
        task = self.get_task(task_id)
        return task.get_info() if task else None
    
    def get_task_result(self, task_id):
        """
        获取任务结果
        
        参数:
            task_id (str): 任务ID
            
        返回:
            Tuple[bool, Any, str]: 元组(是否完成, 结果, 错误信息)
        """
        task = self.get_task(task_id)
        if not task:
            return False, None, "任务不存在"
        
        # 检查任务状态
        if task.status == TaskStatus.COMPLETED:
            return True, task.result, None
        elif task.status == TaskStatus.FAILED:
            return True, None, task.error
        elif task.status == TaskStatus.TIMEOUT:
            return True, None, "任务执行超时"
        elif task.status == TaskStatus.CANCELED:
            return True, None, "任务已取消"
        else:
            return False, None, f"任务仍在处理中，当前状态: {task.status.value}"
    
    def cancel_task(self, task_id):
        """
        取消任务
        
        参数:
            task_id (str): 任务ID
            
        返回:
            bool: 是否成功取消
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        return task.cancel()
    
    def get_all_tasks(self):
        """
        获取所有任务信息
        
        返回:
            List[Dict[str, Any]]: 所有任务的信息列表
        """
        with self.lock:
            return [task.get_info() for task in self.tasks.values()]


# 创建全局任务管理器实例
task_manager = TaskManager()


def run_async(timeout=300):
    """
    异步执行装饰器
    
    将函数转换为异步执行的任务。
    
    参数:
        timeout (int, optional): 超时时间（秒），默认5分钟
        
    返回:
        callable: 包装后的函数
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 将超时参数传递给任务创建函数
            kwargs['_timeout'] = timeout
            
            # 创建异步任务
            task_id = task_manager.create_task(f, *args, **kwargs)
            
            # 返回任务ID
            return {
                "task_id": task_id,
                "status": "accepted",
                "message": "任务已接受并异步处理中"
            }
        
        return wrapper
    
    return decorator 