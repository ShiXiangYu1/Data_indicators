#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试运行脚本
==========

运行数据指标平台的所有测试。
"""

import unittest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
    """运行所有测试"""
    test_loader = unittest.TestLoader()
    
    # 发现并加载所有测试
    test_suite = test_loader.discover(
        start_dir=os.path.dirname(__file__),
        pattern='test_*.py'
    )
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 返回测试结果，成功返回0，失败返回1
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests()) 