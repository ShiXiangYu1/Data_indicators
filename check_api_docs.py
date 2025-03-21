#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查API文档路由是否可用
================

这个脚本会检查API文档路由是否可用，以及其他可能的API文档路径。
"""

import requests
import logging
import json
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://127.0.0.1:8888"

def check_route(base_url, path, description=None):
    """检查指定路由是否可用"""
    url = urljoin(base_url, path)
    route_desc = description or path
    
    try:
        logger.info(f"正在检查 {route_desc}: {url}")
        response = requests.get(url, timeout=2)
        
        status = response.status_code
        logger.info(f"  状态码: {status}")
        
        if status == 200:
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"  内容类型: {content_type}")
            
            # 如果是JSON，尝试打印内容
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    logger.info(f"  响应摘要: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                except Exception as e:
                    logger.warning(f"  无法解析JSON: {e}")
            
            logger.info(f"  ✅ 路由可用")
            return True
        else:
            logger.warning(f"  ❌ 路由不可用 (状态码: {status})")
            return False
            
    except requests.RequestException as e:
        logger.error(f"  ❌ 请求失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info(" API文档路由检查 ".center(80, "="))
    logger.info("=" * 80)
    
    # 首先检查服务器是否运行
    if not check_route(BASE_URL, "/", "API根路径"):
        logger.error("API服务器未运行，请确保服务已启动")
        return 1
    
    logger.info("\n检查主要API路由:")
    check_route(BASE_URL, "/api/health", "API健康检查")
    
    logger.info("\n检查API文档相关路由:")
    docs_routes = [
        "/api/docs",
        "/api/docs/endpoints",
        "/docs",
        "/swagger",
        "/redoc",
        "/openapi.json",
        "/api-docs",
        "/api/swagger-ui",
        "/api/swagger",
        "/api/redoc",
        "/swagger-ui.html",
    ]
    
    available_routes = 0
    for route in docs_routes:
        if check_route(BASE_URL, route, f"文档路由 ({route})"):
            available_routes += 1
    
    if available_routes > 0:
        logger.info(f"\n✅ 找到 {available_routes} 个可用的API文档路由")
    else:
        logger.warning("\n❌ 未找到任何可用的API文档路由")
        logger.info("\n可能的解决方案:")
        logger.info("1. 检查API服务器配置，确保已注册文档路由")
        logger.info("2. 如果使用Flask，检查在create_app函数中是否正确注册了api_docs路由")
        logger.info("3. 如果使用FastAPI，检查是否启用了docs")
        logger.info("4. 可以创建一个自定义的文档页面并将其作为静态文件提供")
    
    return 0

if __name__ == "__main__":
    main() 