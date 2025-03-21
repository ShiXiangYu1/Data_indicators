#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由诊断工具
============

这个脚本提供了一些建议，帮助解决框架混用问题和API路由访问问题。
"""

import sys
import os
import requests
from urllib.parse import urljoin
import traceback

# 默认API地址
API_BASE = "http://127.0.0.1:8888"

def check_endpoint(base_url, path):
    """检查端点是否可访问"""
    url = urljoin(base_url, path)
    try:
        print(f"正在检查: {url}")
        response = requests.get(url, timeout=2)
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            print(f"  内容类型: {content_type}")
            
            # 尝试解析JSON
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"  响应键: {', '.join(data.keys())}")
                except:
                    print("  无法解析JSON响应")
            
            # 如果是HTML内容，显示标题
            elif 'text/html' in content_type:
                print("  内容类型: HTML")
                
            print("  检查成功 ✓")
            return True
        else:
            print(f"  检查失败 ✗ 状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"  检查失败 ✗ 错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print(" API路由诊断工具 ".center(80, '='))
    print("=" * 80)
    
    # Flask相关路径
    flask_paths = [
        "/",
        "/api/health",
        "/api/docs",
        "/api",
        "/api/metric",
        "/api/chart"
    ]
    
    # FastAPI相关路径
    fastapi_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/swagger",
        "/api-docs",
        "/v1/docs",
        "/api/v1/docs"
    ]
    
    print("\n检查Flask路径：")
    flask_success = 0
    for path in flask_paths:
        if check_endpoint(API_BASE, path):
            flask_success += 1
    
    print("\n检查FastAPI路径：")
    fastapi_success = 0
    for path in fastapi_paths:
        if check_endpoint(API_BASE, path):
            fastapi_success += 1
    
    print("\n诊断结果：")
    print(f"- Flask路径可访问: {flask_success}/{len(flask_paths)}")
    print(f"- FastAPI路径可访问: {fastapi_success}/{len(fastapi_paths)}")
    
    # 判断使用的框架
    if flask_success > fastapi_success:
        print("\n诊断结论: 主要使用Flask框架")
        if fastapi_success > 0:
            print("注意: 同时检测到FastAPI路径，存在框架混用情况")
    elif fastapi_success > flask_success:
        print("\n诊断结论: 主要使用FastAPI框架")
        if flask_success > 0:
            print("注意: 同时检测到Flask路径，存在框架混用情况")
    else:
        print("\n诊断结论: 无法确定主要使用的框架")
    
    print("\n解决方案建议：")
    if "/api/docs" not in [p for p in flask_paths if check_endpoint(API_BASE, p)]:
        print("1. API文档路由(/api/docs)不可访问，尝试以下解决方案：")
        
        if "/docs" in [p for p in fastapi_paths if check_endpoint(API_BASE, p)]:
            print("   - 使用FastAPI默认文档路径: http://127.0.0.1:8888/docs")
        elif "/swagger" in [p for p in fastapi_paths if check_endpoint(API_BASE, p)]:
            print("   - 使用Swagger文档路径: http://127.0.0.1:8888/swagger")
        elif "/redoc" in [p for p in fastapi_paths if check_endpoint(API_BASE, p)]:
            print("   - 使用ReDoc文档路径: http://127.0.0.1:8888/redoc")
        else:
            print("   - 检查api/app.py中的路由定义，确保文档路由正确注册")
            print("   - 考虑创建自定义文档路由，如修改api/__init__.py添加文档端点")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"执行诊断工具时出错: {e}")
        traceback.print_exc() 