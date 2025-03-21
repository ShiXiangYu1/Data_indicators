"""
配置设置
======

管理应用程序的配置设置，支持从环境变量、配置文件等加载配置。
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings:
    """
    应用程序配置设置类
    
    负责加载和管理应用程序的所有配置项，支持从多种来源加载配置。
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        参数:
            config_file (str, optional): 配置文件路径，默认为None
        """
        # 基础配置
        self.app_name = "数据指标平台"
        self.version = "0.1.0"
        self.debug = False
        
        # API配置
        self.api_host = "127.0.0.1"
        self.api_port = 5000
        self.api_prefix = "/api"
        
        # 日志配置
        self.log_level = "INFO"
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.log_file = "data_insight.log"
        
        # 数据库配置
        self.db_uri = "sqlite:///data_insight.db"
        
        # 加载配置
        self._load_from_env()
        if config_file:
            self._load_from_file(config_file)
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # 应用基础配置
        self.app_name = os.environ.get("DATA_INSIGHT_APP_NAME", self.app_name)
        self.version = os.environ.get("DATA_INSIGHT_VERSION", self.version)
        self.debug = os.environ.get("DATA_INSIGHT_DEBUG", "false").lower() == "true"
        
        # API配置
        self.api_host = os.environ.get("DATA_INSIGHT_API_HOST", self.api_host)
        self.api_port = int(os.environ.get("DATA_INSIGHT_API_PORT", self.api_port))
        self.api_prefix = os.environ.get("DATA_INSIGHT_API_PREFIX", self.api_prefix)
        
        # 日志配置
        self.log_level = os.environ.get("DATA_INSIGHT_LOG_LEVEL", self.log_level)
        self.log_file = os.environ.get("DATA_INSIGHT_LOG_FILE", self.log_file)
        
        # 数据库配置
        self.db_uri = os.environ.get("DATA_INSIGHT_DB_URI", self.db_uri)
    
    def _load_from_file(self, config_file: str):
        """
        从配置文件加载配置
        
        参数:
            config_file (str): 配置文件路径
        """
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = PROJECT_ROOT / config_path
            
        if not config_path.exists():
            logging.warning(f"配置文件不存在: {config_path}")
            return
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # 更新配置
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
    
    def get_log_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        返回:
            Dict[str, Any]: 日志配置
        """
        log_level = getattr(logging, self.log_level)
        
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.log_format
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "default"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": self.log_file,
                    "level": log_level,
                    "formatter": "default"
                }
            },
            "loggers": {
                "data_insight": {
                    "handlers": ["console", "file"],
                    "level": log_level,
                    "propagate": False
                }
            },
            "root": {
                "handlers": ["console"],
                "level": log_level
            }
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        获取API配置
        
        返回:
            Dict[str, Any]: API配置
        """
        return {
            "host": self.api_host,
            "port": self.api_port,
            "prefix": self.api_prefix,
            "debug": self.debug
        }
    
    def get_db_config(self) -> Dict[str, Any]:
        """
        获取数据库配置
        
        返回:
            Dict[str, Any]: 数据库配置
        """
        return {
            "uri": self.db_uri
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典
        
        返回:
            Dict[str, Any]: 配置字典
        """
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "api": self.get_api_config(),
            "log": self.get_log_config(),
            "db": self.get_db_config()
        } 