#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务初始化模块测试
==============

测试服务初始化功能。
"""

import unittest
from unittest.mock import patch, MagicMock

from data_insight.services import init_services


class TestServiceInit(unittest.TestCase):
    """测试服务初始化功能"""
    
    @patch('data_insight.services.logging')
    def test_init_services(self, mock_logging):
        """测试服务初始化函数"""
        # 模拟服务初始化过程
        result = init_services()
        
        # 验证初始化成功
        self.assertTrue(result)
        
        # 验证日志记录
        mock_logging.info.assert_called_with("所有服务初始化完成")
    
    @patch('data_insight.services.logging')
    @patch('data_insight.services.init_services')
    def test_init_services_on_import(self, mock_init, mock_logging):
        """测试导入模块时的服务初始化"""
        # 重新导入模块，触发初始化
        with patch.dict('sys.modules', {'data_insight.services': None}):
            import importlib
            importlib.reload(__import__('data_insight.services'))
        
        # 验证初始化函数被调用
        mock_init.assert_called_once()


if __name__ == '__main__':
    unittest.main() 