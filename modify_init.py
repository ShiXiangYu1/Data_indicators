#!/usr/bin/env python
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
    import_pattern = r"(# 导入蓝图[\s\S]*?)(# 注册蓝图)"
    import_match = re.search(import_pattern, content)
    
    if not import_match:
        logger.warning("无法找到导入蓝图的位置，尝试使用备选模式")
        import_pattern = r"(from data_insight\.api\.routes[\s\S]*?)(# 注册蓝图)"
        import_match = re.search(import_pattern, content)
    
    if import_match:
        # 添加导入语句
        imports = import_match.group(1)
        new_imports = imports + "\nfrom data_insight.api.routes.api_docs import bp as api_docs_bp\n"
        content = content.replace(imports, new_imports)
        
        # 查找注册蓝图的位置
        register_pattern = r"(# 注册蓝图[\s\S]*?)(# 如果以后还有更多蓝图)"
        register_match = re.search(register_pattern, content)
        
        if register_match:
            registers = register_match.group(1)
            new_registers = registers + "\n    app.register_blueprint(api_docs_bp)"
            content = content.replace(registers, new_registers)
            
            # 写回文件
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"已修改API初始化文件: {init_file}")
            logger.info("已注册API文档蓝图")
            return True
        else:
            logger.error("无法找到注册蓝图的位置")
            
            # 尝试手动添加在其他蓝图注册后
            register_pattern = r"(app\.register_blueprint\(.*?\))"
            register_matches = list(re.finditer(register_pattern, content))
            
            if register_matches:
                last_register = register_matches[-1].group(0)
                new_register = last_register + "\n    app.register_blueprint(api_docs_bp)"
                content = content.replace(last_register, new_register)
                
                # 写回文件
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"已使用备选方式修改API初始化文件: {init_file}")
                logger.info("已注册API文档蓝图")
                return True
    else:
        logger.error("无法找到导入蓝图的位置，尝试直接修改文件")
        
        # 尝试直接添加到文件末尾
        with open(init_file, 'a', encoding='utf-8') as f:
            f.write("\n\n# 添加API文档路由\n")
            f.write("from data_insight.api.routes.api_docs import bp as api_docs_bp\n\n")
            f.write("# 在create_app函数中添加以下代码：\n")
            f.write("# app.register_blueprint(api_docs_bp)\n")
        
        logger.warning(f"已在文件末尾添加注释说明: {init_file}")
        logger.warning("请手动修改create_app函数，注册api_docs_bp蓝图")
    
    return False

if __name__ == "__main__":
    modify_init_file()
