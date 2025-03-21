#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标平台启动脚本
================

启动数据指标平台API服务。
"""

import os
import sys
import logging
import argparse
from data_insight.api import create_app
from data_insight.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data_insight.log")
    ]
)

logger = logging.getLogger("data_insight")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="数据指标平台服务启动脚本")
    parser.add_argument(
        "--host", 
        default=os.environ.get("DATA_INSIGHT_HOST", settings.api_host),
        help="服务主机地址，默认为127.0.0.1"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("DATA_INSIGHT_PORT", settings.api_port)),
        help="服务端口，默认为5000"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        default=os.environ.get("DATA_INSIGHT_DEBUG", "false").lower() == "true",
        help="是否启用调试模式"
    )
    parser.add_argument(
        "--config", 
        default=os.environ.get("DATA_INSIGHT_CONFIG"),
        help="配置文件路径"
    )
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 如果指定了配置文件，从文件加载配置
    if args.config:
        # 通过环境变量传递配置文件路径
        os.environ["DATA_INSIGHT_CONFIG_FILE"] = args.config
    
    # 创建应用
    app = create_app()
    
    # 输出服务信息
    logger.info("=" * 50)
    logger.info(f"数据指标平台 v{settings.version} 服务正在启动...")
    logger.info(f"调试模式: {'启用' if args.debug else '禁用'}")
    logger.info(f"API接口: http://{args.host}:{args.port}{settings.api_prefix}")
    logger.info(f"健康检查: http://{args.host}:{args.port}/api/health")
    logger.info(f"配置文件: {args.config if args.config else '使用默认配置'}")
    logger.info("=" * 50)
    
    # 启动服务
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 