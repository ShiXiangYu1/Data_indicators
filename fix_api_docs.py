#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复API文档路由
=============

此脚本用于修复API文档路由，确保/api/docs路径可访问。
通过创建静态HTML文件并注册路由来提供文档。
"""

import os
import sys
import logging
import shutil
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 静态文件目录
STATIC_DIR = Path("data_insight/data_insight/api/static")

def ensure_directory(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"创建目录: {directory}")

def fix_api_docs():
    """修复API文档路由"""
    # 确保静态文件目录存在
    ensure_directory(STATIC_DIR)
    
    # 复制api_docs.html到静态目录
    source_file = Path("api_docs.html")
    target_file = STATIC_DIR / "api_docs.html"
    
    if not source_file.exists():
        logger.error(f"源文件不存在: {source_file}")
        return False
    
    try:
        shutil.copy2(source_file, target_file)
        logger.info(f"已将文档文件复制到: {target_file}")
    except Exception as e:
        logger.error(f"复制文件时出错: {e}")
        return False
    
    # 创建或修改api_view.py文件来注册新路由
    api_view_path = Path("data_insight/data_insight/api/routes/api_docs.py")
    ensure_directory(api_view_path.parent)
    
    with open(api_view_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API文档路由
=========

提供API文档页面。
"""

import os
from flask import Blueprint, send_from_directory, redirect, url_for
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建蓝图
bp = Blueprint('api_docs', __name__, url_prefix='/api')

@bp.route('/docs')
def api_docs():
    """API文档页面"""
    # 返回静态HTML文件
    logger.info("访问API文档页面")
    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(os.path.dirname(os.path.dirname(module_dir)), 'api', 'static')
    return send_from_directory(static_dir, 'api_docs.html')

@bp.route('/docs/swagger')
def swagger_redirect():
    """重定向到API文档页面"""
    return redirect(url_for('api_docs.api_docs'))

@bp.route('/docs/redoc')
def redoc_redirect():
    """重定向到API文档页面"""
    return redirect(url_for('api_docs.api_docs'))

@bp.route('/docs/openapi.json')
def openapi_json():
    """OpenAPI规范JSON"""
    logger.info("访问OpenAPI规范JSON")
    # 在这里可以返回实际的OpenAPI规范
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "数据指标平台API",
            "description": "数据指标平台API文档",
            "version": "0.1.0"
        },
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "健康检查",
                    "description": "检查API服务是否正常运行",
                    "responses": {
                        "200": {
                            "description": "服务正常运行"
                        }
                    }
                }
            }
        }
    }
''')
    logger.info(f"已创建API文档路由文件: {api_view_path}")
    
    # 修改 __init__.py 文件，注册新的蓝图
    init_file = Path("data_insight/data_insight/api/__init__.py")
    if not init_file.exists():
        logger.error(f"API初始化文件不存在: {init_file}")
        return False
    
    # 创建一个修改初始化文件的Python脚本
    modify_script_path = Path("modify_init.py")
    with open(modify_script_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修改API初始化文件
===============

修改API初始化文件以注册新的API文档蓝图。
"""

import os
import re
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def modify_init_file():
    """修改__init__.py文件以注册新的蓝图"""
    init_file = "data_insight/data_insight/api/__init__.py"
    
    if not os.path.exists(init_file):
        logger.error(f"文件不存在: {init_file}")
        return False
    
    # 读取文件内容
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入api_docs蓝图
    if "from data_insight.api.routes.api_docs import bp as api_docs_bp" in content:
        logger.info("API文档蓝图已经导入，无需修改")
        return True
    
    # 查找导入蓝图的位置
    import_pattern = r"(# 导入蓝图.*?)(\n\s*# 注册蓝图)"
    import_match = re.search(import_pattern, content, re.DOTALL)
    
    if not import_match:
        logger.warning("无法找到导入蓝图的位置，尝试使用备选模式")
        import_pattern = r"(from data_insight.api.routes.*?)(\n\s*# 注册蓝图)"
        import_match = re.search(import_pattern, content, re.DOTALL)
    
    if import_match:
        # 添加导入语句
        imports = import_match.group(1)
        new_imports = imports + "\\nfrom data_insight.api.routes.api_docs import bp as api_docs_bp"
        content = content.replace(imports, new_imports)
        
        # 查找注册蓝图的位置
        register_pattern = r"(# 注册蓝图.*?)(# 如果以后还有更多蓝图)"
        register_match = re.search(register_pattern, content, re.DOTALL)
        
        if register_match:
            registers = register_match.group(1)
            new_registers = registers + "\\n    app.register_blueprint(api_docs_bp)"
            content = content.replace(registers, new_registers)
            
            # 写回文件
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"已修改API初始化文件: {init_file}")
            logger.info("已注册API文档蓝图")
            return True
        else:
            logger.error("无法找到注册蓝图的位置")
    else:
        logger.error("无法找到导入蓝图的位置")
    
    return False

if __name__ == "__main__":
    modify_init_file()
''')
    logger.info(f"已创建初始化文件修改脚本: {modify_script_path}")
    
    # 运行修改脚本
    logger.info("运行初始化文件修改脚本...")
    os.system(f"python {modify_script_path}")
    
    logger.info("API文档路由修复完成！")
    logger.info("请重启服务，然后访问 http://127.0.0.1:8888/api/docs")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if fix_api_docs() else 1) 