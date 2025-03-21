#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API端点测试脚本
=============

测试各个API端点的可用性，帮助定位问题。
"""

import requests
import webbrowser
import logging
from urllib.parse import urljoin
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# API基础URL
BASE_URL = "http://127.0.0.1:8888"

def test_endpoint(path, description=None, open_browser=False):
    """测试API端点是否可用"""
    url = urljoin(BASE_URL, path)
    desc = description or path
    
    try:
        logger.info(f"测试端点: {desc} ({url})")
        response = requests.get(url, timeout=3)
        status_code = response.status_code
        
        if status_code == 200:
            logger.info(f"✅ 成功 (状态码: {status_code})")
            
            # 打印响应头信息
            content_type = response.headers.get('Content-Type', 'unknown')
            logger.info(f"  Content-Type: {content_type}")
            
            # 如果是HTML或JSON，打印一部分响应内容
            if 'text/html' in content_type:
                # 提取HTML标题
                if '<title>' in response.text:
                    title = response.text.split('<title>')[1].split('</title>')[0]
                    logger.info(f"  HTML标题: {title}")
                else:
                    # 打印前100个字符
                    logger.info(f"  HTML内容 (前100个字符): {response.text[:100]}...")
            elif 'application/json' in content_type:
                # 打印JSON格式
                try:
                    json_data = response.json()
                    logger.info(f"  JSON响应: {json_data}")
                except:
                    logger.warning("  无法解析JSON响应")
            
            # 如果需要在浏览器中打开
            if open_browser:
                logger.info(f"  在浏览器中打开: {url}")
                webbrowser.open(url)
                
            return True
        else:
            logger.warning(f"❌ 失败 (状态码: {status_code})")
            return False
    except Exception as e:
        logger.error(f"❌ 错误: {e}")
        return False

def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info(" API端点测试 ".center(70, "="))
    logger.info("=" * 70)
    
    # 确保服务器正在运行
    root_available = test_endpoint("/", "根路径")
    if not root_available:
        logger.warning("根路径返回404，这可能是正常的，因为API可能没有定义根路径处理程序")
    
    # 测试健康检查端点
    health_available = test_endpoint("/api/health", "健康检查")
    if not health_available:
        logger.error("健康检查端点不可用，API服务可能存在问题！")
        return False
    
    # 测试API文档端点
    logger.info("\n测试API文档相关端点:")
    
    # 1. 直接定义在__init__.py中的路由
    test_endpoint("/api/docs", "API文档路由 (直接定义)")
    test_endpoint("/api/docs/endpoints", "API端点列表")
    
    # 2. 通过蓝图注册的路由
    test_endpoint("/api/docs", "API文档路由 (蓝图)")
    test_endpoint("/api/docs/swagger", "Swagger文档")
    test_endpoint("/api/docs/redoc", "ReDoc文档")
    test_endpoint("/api/docs/openapi.json", "OpenAPI规范")
    
    # 3. 可能的FastAPI路由
    test_endpoint("/docs", "FastAPI文档")
    test_endpoint("/redoc", "FastAPI ReDoc")
    
    # 4. 其他流行的文档路径
    test_endpoint("/swagger", "Swagger UI")
    test_endpoint("/swagger-ui.html", "Swagger UI HTML")
    
    logger.info("\n测试其他API端点:")
    test_endpoint("/api/metric/analyze", "指标分析")
    test_endpoint("/api/chart/analyze", "图表分析")
    
    logger.info("\n打开浏览器访问API文档:")
    # 尝试在浏览器中打开可能存在的文档路由
    api_docs_urls = [
        "/api/docs",
        "/api/health",
        "/api",
        "/docs"
    ]
    
    for url in api_docs_urls:
        if test_endpoint(url, f"浏览器访问: {url}", open_browser=True):
            logger.info(f"成功在浏览器中打开: {url}")
            time.sleep(1)  # 间隔1秒，避免浏览器过载
    
    logger.info("\n测试完成！")
    
    return True

if __name__ == "__main__":
    main() 