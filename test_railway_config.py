#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Railway配置测试脚本
================

用于验证应用是否满足Railway部署要求。
"""

import os
import sys
import socket
import requests
import importlib.util
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("railway_test")


def check_port_variable():
    """检查应用是否正确使用PORT环境变量"""
    logger.info("检查PORT环境变量处理...")
    
    # 模拟Railway环境
    test_port = 9876
    os.environ["PORT"] = str(test_port)
    
    try:
        # 尝试导入create_app函数
        spec = importlib.util.find_spec("data_insight.api")
        if not spec:
            logger.error("找不到data_insight.api模块，请确保项目结构正确")
            return False
            
        # 验证应用是否使用PORT环境变量
        from data_insight.api import create_app
        app = create_app()
        
        # 检查配置中是否包含PORT环境变量
        if hasattr(app, 'config') and 'PORT' in app.config:
            if app.config['PORT'] == test_port or app.config['PORT'] == str(test_port):
                logger.info("✅ 应用正确处理了PORT环境变量")
                return True
        
        logger.warning("⚠️ 未检测到应用配置中有PORT环境变量，这可能在Railway部署时导致问题")
        return False
        
    except Exception as e:
        logger.error(f"❌ 检查PORT环境变量时出错: {str(e)}")
        return False
    finally:
        # 清理环境变量
        if "PORT" in os.environ:
            del os.environ["PORT"]


def check_procfile():
    """检查Procfile是否存在且格式正确"""
    logger.info("检查Procfile配置...")
    
    if not os.path.exists("Procfile"):
        logger.error("❌ 找不到Procfile，请创建该文件")
        return False
    
    with open("Procfile", "r") as f:
        content = f.read().strip()
    
    if not content.startswith("web:"):
        logger.error("❌ Procfile格式不正确，必须以'web:'开头")
        return False
    
    if "$PORT" not in content:
        logger.error("❌ Procfile中未使用$PORT环境变量")
        return False
    
    logger.info("✅ Procfile配置正确")
    return True


def check_requirements():
    """检查requirements.txt是否包含必要依赖"""
    logger.info("检查requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        logger.error("❌ 找不到requirements.txt，请创建该文件")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_packages = ["gunicorn", "flask"]
    missing_packages = []
    
    for package in required_packages:
        if package not in content.lower():
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ requirements.txt缺少必要依赖: {', '.join(missing_packages)}")
        return False
    
    logger.info("✅ requirements.txt包含必要依赖")
    return True


def check_railway_json():
    """检查railway.json是否存在且配置合理"""
    logger.info("检查railway.json配置...")
    
    import json
    
    if not os.path.exists("railway.json"):
        logger.warning("⚠️ 未找到railway.json，这不是必需的，但推荐添加以优化部署")
        return True
    
    try:
        with open("railway.json", "r") as f:
            config = json.load(f)
        
        if "deploy" in config and "startCommand" in config["deploy"]:
            start_command = config["deploy"]["startCommand"]
            if "$PORT" not in start_command:
                logger.warning("⚠️ railway.json中的startCommand未包含$PORT环境变量")
            else:
                logger.info("✅ railway.json配置正确")
                return True
    except Exception as e:
        logger.error(f"❌ 解析railway.json时出错: {str(e)}")
        return False


def check_health_endpoint():
    """检查健康检查端点是否存在"""
    logger.info("检查健康检查端点...")
    
    try:
        # 尝试导入create_app函数
        from data_insight.api import create_app
        app = create_app()
        
        # 使用测试客户端测试健康检查端点
        with app.test_client() as client:
            response = client.get('/api/health')
            
            if response.status_code == 200:
                logger.info("✅ 健康检查端点可访问")
                return True
            else:
                logger.warning(f"⚠️ 健康检查端点返回非200状态码: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ 检查健康检查端点时出错: {str(e)}")
        return False


def main():
    """主函数，执行所有检查"""
    logger.info("="*50)
    logger.info("Railway部署配置检查开始")
    logger.info("="*50)
    
    # 加载环境变量
    load_dotenv()
    
    # 执行检查
    checks = [
        ("PORT环境变量处理", check_port_variable),
        ("Procfile配置", check_procfile),
        ("requirements.txt检查", check_requirements),
        ("railway.json配置", check_railway_json),
        ("健康检查端点", check_health_endpoint)
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            logger.error(f"执行{name}检查时发生错误: {str(e)}")
            results.append((name, False))
    
    # 汇总结果
    logger.info("\n" + "="*50)
    logger.info("Railway部署配置检查结果")
    logger.info("="*50)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{name}: {status}")
        all_passed = all_passed and result
    
    logger.info("="*50)
    if all_passed:
        logger.info("🎉 所有检查通过，应用已准备好部署到Railway")
    else:
        logger.info("⚠️ 部分检查未通过，请修复上述问题后再部署到Railway")


if __name__ == "__main__":
    main() 