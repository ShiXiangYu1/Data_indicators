#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标平台启动测试脚本
====================

用于测试数据指标平台应用启动。
"""

import os
import sys
import logging
from flask import Flask, jsonify

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger("launch_app")

def create_test_app():
    """创建测试应用"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "测试应用启动成功！"
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "message": "测试应用运行正常"})
    
    return app

def launch_data_insight():
    """尝试启动数据指标平台应用"""
    try:
        # 尝试导入数据指标平台的创建函数
        from data_insight.api import create_app
        
        # 创建应用
        app = create_app()
        
        # 输出服务信息
        logger.info("=" * 50)
        logger.info("数据指标平台应用创建成功，尝试启动...")
        logger.info("=" * 50)
        
        # 启动服务
        app.run(host="0.0.0.0", port=9000, debug=True)
        
    except Exception as e:
        logger.error(f"启动数据指标平台失败: {str(e)}")
        logger.error("回退到测试应用")
        
        # 创建并启动测试应用
        app = create_test_app()
        app.run(host="0.0.0.0", port=9000, debug=True)

if __name__ == "__main__":
    logger.info("启动数据指标平台或测试应用...")
    launch_data_insight() 