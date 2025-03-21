#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask路由调试工具
===============

打印Flask应用中所有已注册的路由，帮助调试404错误。
"""

import os
import sys
import importlib
import logging

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def debug_flask_routes():
    """导入Flask应用并打印所有已注册的路由"""
    try:
        # 打印系统路径
        logger.info("Python路径：")
        for p in sys.path:
            logger.info(f" - {p}")
        
        # 直接导入Flask应用
        logger.info("尝试直接从data_insight.api导入create_app...")
        sys.path.insert(0, os.path.join(current_dir, 'data_insight'))
        
        # 尝试直接从data_insight.api导入
        from data_insight.api import create_app
        
        # 创建一个应用实例
        logger.info("创建Flask应用实例...")
        app = create_app()
        
        # 打印所有已注册的路由
        logger.info("=" * 80)
        logger.info(" 已注册的Flask路由 ".center(80, "="))
        logger.info("=" * 80)
        
        # 按路径长度排序，使输出更加美观
        routes = []
        for rule in app.url_map.iter_rules():
            methods = sorted(list(rule.methods))
            # 排除HEAD和OPTIONS方法，它们通常是自动添加的
            methods = [m for m in methods if m not in ['HEAD', 'OPTIONS']]
            if methods:  # 只显示有实际HTTP方法的路由
                routes.append((rule.rule, rule.endpoint, ", ".join(methods)))
        
        # 按路径排序
        routes.sort(key=lambda x: x[0])
        
        # 按表格形式输出路由信息
        fmt = "{:<50} {:<30} {:<20}"
        logger.info(fmt.format("路由路径", "端点函数", "HTTP方法"))
        logger.info("-" * 80)
        
        for route, endpoint, methods in routes:
            logger.info(fmt.format(route, endpoint, methods))
        
        logger.info("=" * 80)
        logger.info(f"总共找到 {len(routes)} 个已注册路由")
        logger.info("=" * 80)
        
        # 检查API文档相关路由
        api_docs_routes = [
            "/api/docs",
            "/api/docs/endpoints",
            "/docs",
            "/swagger",
            "/redoc",
            "/api-docs",
            "/openapi.json",
        ]
        
        logger.info("检查API文档相关路由:")
        for route_path in api_docs_routes:
            route = next((r for r in routes if r[0] == route_path), None)
            if route:
                logger.info(f"✅ {route_path:<20} - 端点: {route[1]:<30} - 方法: {route[2]}")
            else:
                logger.warning(f"❌ {route_path:<20} - 未注册")
        
        # 检查是否有/api前缀的路由
        api_routes = [r for r in routes if r[0].startswith("/api")]
        
        logger.info("\n/api前缀的路由:")
        for route in api_routes:
            logger.info(f"- {route[0]:<40} - 端点: {route[1]}")
        
        return 0
        
    except ImportError as e:
        logger.error(f"导入Flask应用失败: {e}")
        logger.error(f"错误详情: {str(e)}")
        logger.error("\n尝试以下解决方案:")
        logger.error("1. 确保已安装所有依赖: pip install -r requirements.txt")
        logger.error("2. 将当前目录添加到PYTHONPATH: set PYTHONPATH=%PYTHONPATH%;.")
        logger.error("3. 检查导入路径是否正确")
        
        # 检查可能的导入位置
        possible_paths = [
            os.path.join(current_dir, 'data_insight'),
            os.path.join(current_dir, 'data_insight', 'data_insight'),
            current_dir
        ]
        
        logger.error("\n尝试在以下路径中查找模块:")
        for path in possible_paths:
            api_path = os.path.join(path, 'api')
            if os.path.exists(api_path):
                logger.info(f"发现模块路径: {api_path}")
            else:
                logger.error(f"路径不存在: {api_path}")
        
        return 1
    except Exception as e:
        logger.error(f"调试路由时出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(debug_flask_routes()) 