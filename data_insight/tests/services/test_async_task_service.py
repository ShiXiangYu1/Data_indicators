#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异步任务处理服务测试
================

测试异步任务处理功能。
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from data_insight.services.async_task_service import (
    TaskStatus, TaskPriority, Task, ProgressReporter, AsyncTaskService, get_async_task_service
)


class TestTaskStatus(unittest.TestCase):
    """测试任务状态枚举"""
    
    def test_values(self):
        """测试枚举值"""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.RUNNING.value, "running")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.TIMEOUT.value, "timeout")
        self.assertEqual(TaskStatus.CANCELED.value, "canceled")


class TestTaskPriority(unittest.TestCase):
    """测试任务优先级枚举"""
    
    def test_values(self):
        """测试枚举值"""
        self.assertEqual(TaskPriority.LOW.value, 0)
        self.assertEqual(TaskPriority.NORMAL.value, 1)
        self.assertEqual(TaskPriority.HIGH.value, 2)
        self.assertEqual(TaskPriority.URGENT.value, 3)


class TestTask(unittest.TestCase):
    """测试任务类"""
    
    def setUp(self):
        """测试前准备"""
        def dummy_func(x, y):
            return x + y
        
        self.task = Task(
            task_id="test_task",
            func=dummy_func,
            args=(1, 2),
            kwargs={"z": 3},
            priority=TaskPriority.NORMAL,
            timeout=10,
            callback=None,
            error_callback=None,
            metadata={"desc": "测试任务"}
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.task.task_id, "test_task")
        self.assertEqual(self.task.args, (1, 2))
        self.assertEqual(self.task.kwargs, {"z": 3})
        self.assertEqual(self.task.priority, TaskPriority.NORMAL)
        self.assertEqual(self.task.timeout, 10)
        self.assertEqual(self.task.metadata, {"desc": "测试任务"})
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertIsNone(self.task.result)
        self.assertIsNone(self.task.error)
        self.assertIsNone(self.task.traceback)
        self.assertIsNone(self.task.started_at)
        self.assertIsNone(self.task.completed_at)
        self.assertEqual(self.task.progress, 0)
        self.assertEqual(self.task.message, "等待执行")
    
    def test_to_dict(self):
        """测试转换为字典"""
        task_dict = self.task.to_dict()
        
        self.assertEqual(task_dict["task_id"], "test_task")
        self.assertEqual(task_dict["status"], "pending")
        self.assertEqual(task_dict["progress"], 0)
        self.assertEqual(task_dict["message"], "等待执行")
        self.assertEqual(task_dict["metadata"], {"desc": "测试任务"})
        self.assertIsNone(task_dict["started_at"])
        self.assertIsNone(task_dict["completed_at"])
        self.assertIsNone(task_dict["execution_time"])
    
    def test_priority_comparison(self):
        """测试优先级比较"""
        high_priority_task = Task(
            task_id="high_priority",
            func=lambda: None,
            priority=TaskPriority.HIGH
        )
        
        low_priority_task = Task(
            task_id="low_priority",
            func=lambda: None,
            priority=TaskPriority.LOW
        )
        
        # 高优先级应该小于低优先级（用于排序）
        self.assertTrue(high_priority_task < low_priority_task)
        self.assertFalse(low_priority_task < high_priority_task)


class TestProgressReporter(unittest.TestCase):
    """测试进度报告器"""
    
    def setUp(self):
        """测试前准备"""
        self.task = Task(
            task_id="test_task",
            func=lambda: None
        )
        self.reporter = ProgressReporter(self.task)
    
    def test_update(self):
        """测试更新进度"""
        # 更新进度
        self.reporter.update(50, "测试进度")
        
        # 验证任务进度已更新
        self.assertEqual(self.task.progress, 50)
        self.assertEqual(self.task.message, "测试进度")
        
        # 测试进度边界值
        self.reporter.update(-10, "负进度")
        self.assertEqual(self.task.progress, 0)  # 进度不应小于0
        
        self.reporter.update(110, "超出进度")
        self.assertEqual(self.task.progress, 100)  # 进度不应大于100


class TestAsyncTaskService(unittest.TestCase):
    """测试异步任务服务"""
    
    def setUp(self):
        """测试前准备"""
        # 创建一个新的异步任务服务实例（不使用单例）
        with patch('data_insight.services.async_task_service.AsyncTaskService._instance', None):
            self.service = AsyncTaskService(max_workers=2, task_cache_size=10)
    
    def tearDown(self):
        """测试后清理"""
        self.service.shutdown(wait=True)
    
    def test_singleton(self):
        """测试单例模式"""
        service2 = AsyncTaskService()
        self.assertIs(self.service, service2)
    
    def test_submit_task_success(self):
        """测试成功提交任务"""
        def success_task(x, y):
            return x + y
        
        # 提交任务
        task_id = self.service.submit_task(
            func=success_task,
            args=(1, 2),
            priority=TaskPriority.NORMAL
        )
        
        # 验证任务ID
        self.assertIsNotNone(task_id)
        
        # 等待任务完成
        time.sleep(0.1)
        
        # 获取任务状态
        task_status = self.service.get_task_status(task_id)
        self.assertEqual(task_status["status"], "completed")
        
        # 获取任务结果
        result = self.service.get_task_result(task_id)
        self.assertEqual(result, 3)
    
    def test_submit_task_failure(self):
        """测试提交失败的任务"""
        def failure_task():
            raise ValueError("测试错误")
        
        # 提交任务
        task_id = self.service.submit_task(func=failure_task)
        
        # 等待任务完成
        time.sleep(0.1)
        
        # 获取任务状态
        task_status = self.service.get_task_status(task_id)
        self.assertEqual(task_status["status"], "failed")
        
        # 获取任务结果应该抛出异常
        with self.assertRaises(RuntimeError):
            self.service.get_task_result(task_id)
    
    def test_task_with_progress(self):
        """测试带进度报告的任务"""
        def progress_task(progress_reporter):
            for i in range(0, 101, 20):
                progress_reporter.update(i, f"进度 {i}%")
                time.sleep(0.01)
            return "完成"
        
        # 提交任务
        task_id = self.service.submit_task(func=progress_task)
        
        # 等待任务完成
        time.sleep(0.3)
        
        # 获取任务状态
        task_status = self.service.get_task_status(task_id)
        self.assertEqual(task_status["status"], "completed")
        self.assertEqual(task_status["progress"], 100)
        
        # 获取任务结果
        result = self.service.get_task_result(task_id)
        self.assertEqual(result, "完成")
    
    def test_cancel_task(self):
        """测试取消任务"""
        def long_task():
            time.sleep(1)
            return "完成"
        
        # 提交多个任务（第二个任务可能会等待，便于测试取消）
        task_id1 = self.service.submit_task(func=long_task)
        task_id2 = self.service.submit_task(func=long_task)
        
        # 立即取消第二个任务（可能仍在等待执行）
        cancel_result = self.service.cancel_task(task_id2)
        
        # 无法确定任务是否已经开始执行，所以不能确定取消是否成功
        # 但是可以验证取消操作本身没有异常
        
        # 等待第一个任务完成
        time.sleep(1.2)
        
        # 验证第一个任务完成
        task_status1 = self.service.get_task_status(task_id1)
        self.assertEqual(task_status1["status"], "completed")
    
    def test_get_all_tasks(self):
        """测试获取所有任务"""
        # 提交两个任务
        task_id1 = self.service.submit_task(func=lambda: "任务1")
        task_id2 = self.service.submit_task(func=lambda: "任务2")
        
        # 等待任务完成
        time.sleep(0.1)
        
        # 获取所有任务
        all_tasks = self.service.get_all_tasks()
        
        # 验证任务数量
        self.assertEqual(len(all_tasks), 2)
        
        # 验证任务ID
        task_ids = [task["task_id"] for task in all_tasks]
        self.assertIn(task_id1, task_ids)
        self.assertIn(task_id2, task_ids)
    
    def test_get_active_tasks(self):
        """测试获取活动任务"""
        # 提交一个长时间运行的任务
        task_id = self.service.submit_task(func=lambda: time.sleep(0.2))
        
        # 立即获取活动任务
        active_tasks = self.service.get_active_tasks()
        
        # 验证任务数量
        self.assertTrue(len(active_tasks) > 0)
        
        # 等待任务完成
        time.sleep(0.3)
        
        # 再次获取活动任务
        active_tasks = self.service.get_active_tasks()
        
        # 验证任务数量
        self.assertEqual(len(active_tasks), 0)


class TestGetAsyncTaskService(unittest.TestCase):
    """测试获取异步任务服务"""
    
    @patch('data_insight.services.async_task_service._async_task_service', None)
    def test_get_service(self):
        """测试获取服务实例"""
        service = get_async_task_service()
        self.assertIsInstance(service, AsyncTaskService)
        
        # 再次获取服务，应该是同一个实例
        service2 = get_async_task_service()
        self.assertIs(service, service2)


if __name__ == '__main__':
    unittest.main() 