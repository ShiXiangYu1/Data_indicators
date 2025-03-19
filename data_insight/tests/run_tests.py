#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试运行脚本
==========

用于一键运行所有测试，包括单元测试、Web界面测试、API测试、集成测试、端到端测试和性能测试。
"""

import os
import sys
import unittest
import argparse
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)


def discover_and_run_tests(test_dir, pattern="test_*.py", test_type="所有测试"):
    """发现并运行测试"""
    start_time = time.time()
    logger.info(f"开始运行{test_type}")
    
    # 发现测试
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=test_dir,
        pattern=pattern
    )
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 计算运行时间和结果
    end_time = time.time()
    run_time = end_time - start_time
    
    # 输出测试结果摘要
    logger.info(f"{test_type}完成，耗时: {run_time:.2f}秒")
    logger.info(f"运行测试: {result.testsRun}")
    logger.info(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"失败: {len(result.failures)}")
    logger.info(f"错误: {len(result.errors)}")
    
    return result


def run_all_tests(include_performance=False, include_e2e=True, include_integration=True):
    """运行所有测试"""
    # 记录总体开始时间
    overall_start = time.time()
    
    # 获取测试目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建结果目录
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 测试类别及其目录
    test_categories = [
        {"name": "单元测试", "dir": os.path.join(base_dir, "unit"), "pattern": "test_*.py"},
        {"name": "Web界面测试", "dir": os.path.join(base_dir, "web"), "pattern": "test_*.py"},
        {"name": "API测试", "dir": os.path.join(base_dir, "api"), "pattern": "test_*.py"},
    ]
    
    # 是否包括集成测试
    if include_integration:
        test_categories.append(
            {"name": "集成测试", "dir": os.path.join(base_dir, "integration"), "pattern": "test_*.py"}
        )
    
    # 是否包括端到端测试
    if include_e2e:
        test_categories.append(
            {"name": "端到端测试", "dir": os.path.join(base_dir, "e2e"), "pattern": "test_*.py"}
        )
    
    # 是否包括性能测试
    if include_performance:
        test_categories.append(
            {"name": "性能测试", "dir": os.path.join(base_dir, "performance"), "pattern": "test_*.py"}
        )
    
    # 记录测试结果
    all_results = {}
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    # 运行每个类别的测试
    for category in test_categories:
        if os.path.exists(category["dir"]):
            try:
                result = discover_and_run_tests(
                    category["dir"], 
                    category["pattern"], 
                    category["name"]
                )
                
                # 记录结果
                all_results[category["name"]] = {
                    "tests": result.testsRun,
                    "failures": len(result.failures),
                    "errors": len(result.errors)
                }
                
                total_tests += result.testsRun
                total_failures += len(result.failures)
                total_errors += len(result.errors)
                
                # 如果有测试错误，打印详情
                if result.failures or result.errors:
                    logger.warning(f"{category['name']}中有失败或错误，详情如下:")
                    
                    for failure in result.failures:
                        logger.warning(f"失败: {failure[0]}")
                        logger.warning(f"原因: {failure[1]}\n")
                    
                    for error in result.errors:
                        logger.warning(f"错误: {error[0]}")
                        logger.warning(f"原因: {error[1]}\n")
            
            except Exception as e:
                logger.error(f"运行{category['name']}时发生错误: {str(e)}")
                all_results[category["name"]] = {
                    "tests": 0,
                    "failures": 0,
                    "errors": 1,
                    "exception": str(e)
                }
                total_errors += 1
        else:
            logger.warning(f"{category['name']}目录不存在: {category['dir']}")
    
    # 计算总运行时间
    overall_end = time.time()
    overall_time = overall_end - overall_start
    
    # 输出总体测试摘要
    logger.info("\n========== 测试运行总结 ==========")
    logger.info(f"总运行时间: {overall_time:.2f}秒")
    logger.info(f"总测试数: {total_tests}")
    logger.info(f"总成功数: {total_tests - total_failures - total_errors}")
    logger.info(f"总失败数: {total_failures}")
    logger.info(f"总错误数: {total_errors}")
    logger.info("========== 各分类测试结果 ==========")
    
    for category, result in all_results.items():
        if "exception" in result:
            logger.info(f"{category}: 运行出错 - {result['exception']}")
        else:
            success = result["tests"] - result["failures"] - result["errors"]
            success_rate = (success / result["tests"] * 100) if result["tests"] > 0 else 0
            logger.info(f"{category}: 测试 {result['tests']}, 成功 {success} ({success_rate:.1f}%), "
                       f"失败 {result['failures']}, 错误 {result['errors']}")
    
    # 返回测试是否全部通过
    return total_failures == 0 and total_errors == 0


def setup_test_environment():
    """设置测试环境变量和依赖"""
    # 设置测试环境变量
    os.environ["TEST_MODE"] = "True"
    os.environ["TEST_API_TOKEN"] = "test-token-for-testing"
    
    # 将项目根目录添加到系统路径中
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    logger.info(f"测试环境已设置，项目根目录: {project_root}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="运行数据指标分析系统的测试套件")
    parser.add_argument("--all", action="store_true", help="运行所有测试，包括性能测试")
    parser.add_argument("--unit", action="store_true", help="仅运行单元测试")
    parser.add_argument("--web", action="store_true", help="仅运行Web界面测试")
    parser.add_argument("--api", action="store_true", help="仅运行API测试")
    parser.add_argument("--integration", action="store_true", help="仅运行集成测试")
    parser.add_argument("--e2e", action="store_true", help="仅运行端到端测试")
    parser.add_argument("--performance", action="store_true", help="仅运行性能测试")
    parser.add_argument("--skip-integration", action="store_true", help="跳过集成测试")
    parser.add_argument("--skip-e2e", action="store_true", help="跳过端到端测试")
    parser.add_argument("--skip-performance", action="store_true", help="跳过性能测试")
    
    return parser.parse_args()


if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置测试环境
    setup_test_environment()
    
    # 根据参数决定运行哪些测试
    if args.unit:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "unit"), "test_*.py", "单元测试")
    elif args.web:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "web"), "test_*.py", "Web界面测试")
    elif args.api:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "api"), "test_*.py", "API测试")
    elif args.integration:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "integration"), "test_*.py", "集成测试")
    elif args.e2e:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "e2e"), "test_*.py", "端到端测试")
    elif args.performance:
        discover_and_run_tests(os.path.join(os.path.dirname(__file__), "performance"), "test_*.py", "性能测试")
    else:
        # 默认运行所有测试但跳过性能测试
        include_performance = args.all or not args.skip_performance
        include_e2e = not args.skip_e2e
        include_integration = not args.skip_integration
        
        success = run_all_tests(
            include_performance=include_performance, 
            include_e2e=include_e2e,
            include_integration=include_integration
        )
        
        # 根据测试结果设置退出代码
        sys.exit(0 if success else 1) 