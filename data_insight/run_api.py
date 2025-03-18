#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据指标平台API服务启动脚本
======================

用于启动数据指标平台的Web API服务。

使用方法:
    python run_api.py [--host HOST] [--port PORT] [--debug]

参数:
    --host HOST: 监听的主机地址，默认为127.0.0.1
    --port PORT: 监听的端口，默认为5000
    --debug: 启用调试模式
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

from data_insight.api import create_app


def parse_arguments():
    """
    解析命令行参数
    
    返回:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='启动数据指标平台API服务')
    
    parser.add_argument('--host', 
                        type=str, 
                        default='127.0.0.1',
                        help='监听的主机地址（默认: 127.0.0.1）')
    
    parser.add_argument('--port', 
                        type=int, 
                        default=5000,
                        help='监听的端口（默认: 5000）')
    
    parser.add_argument('--debug', 
                        action='store_true',
                        help='启用调试模式')
    
    return parser.parse_args()


def setup_logging(debug=False):
    """
    配置日志
    
    参数:
        debug (bool): 是否启用调试模式
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载环境变量
    load_dotenv()
    
    # 设置环境变量
    if args.debug:
        os.environ['FLASK_DEBUG'] = 'true'
    
    # 配置日志
    setup_logging(args.debug)
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    print(f"数据指标平台API服务启动中...")
    print(f"API文档地址: http://{args.host}:{args.port}/api/docs")
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("服务已停止")
    except Exception as e:
        print(f"启动服务时发生错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 