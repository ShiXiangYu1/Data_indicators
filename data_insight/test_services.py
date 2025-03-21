#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务测试脚本
==========

测试数据指标平台的服务初始化和基本功能。
"""

import os
import sys
import logging
import traceback

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def test_services_init():
    """测试服务初始化"""
    try:
        from data_insight.services import init_services
        
        # 初始化服务
        result = init_services()
        
        if result:
            print("服务初始化成功！")
        else:
            print("服务初始化失败！")
            
        return result
    except Exception as e:
        print(f"服务初始化异常: {str(e)}")
        traceback.print_exc()
        return False

def test_service_imports():
    """测试服务导入"""
    services = [
        "AsyncTaskService", 
        "MetricService", 
        "ChartService", 
        "AnalysisService", 
        "PredictionService", 
        "RecommendationService"
    ]
    
    success_count = 0
    failed_count = 0
    
    try:
        print("开始导入服务模块...")
        from data_insight.services import (
            AsyncTaskService, 
            MetricService, 
            ChartService, 
            AnalysisService, 
            PredictionService, 
            RecommendationService
        )
        print("所有服务模块导入成功！")
        
        for service_name in services:
            service_class = locals()[service_name]
            print(f"成功导入 {service_name}")
            try:
                # 尝试实例化服务
                service_instance = service_class()
                print(f"成功实例化 {service_name}")
                success_count += 1
            except Exception as e:
                print(f"实例化 {service_name} 失败: {str(e)}")
                traceback.print_exc()
                failed_count += 1
        
        print(f"\n服务测试结果: {success_count} 个成功, {failed_count} 个失败")
        return success_count > 0
    except Exception as e:
        print(f"服务导入异常: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("测试服务导入...")
    import_result = test_service_imports()
    
    print("\n" + "=" * 50)
    print("测试服务初始化...")
    init_result = test_services_init()
    
    print("\n" + "=" * 50)
    if import_result and init_result:
        print("测试全部通过！")
    else:
        print("测试部分失败，请查看日志！")
    print("=" * 50) 