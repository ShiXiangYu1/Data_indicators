"""
API错误处理模块
=============

提供API统一的错误处理机制，包括全局异常处理和错误处理装饰器。
"""

import functools
import traceback
import logging
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException

# 获取日志记录器
logger = logging.getLogger(__name__)

class APIError(Exception):
    """API错误基类
    
    自定义API错误，可以指定状态码和错误消息
    """
    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def handle_exceptions(f):
    """异常处理装饰器
    
    捕获视图函数中的异常并返回适当的JSON响应
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            # 处理自定义API错误
            response = {
                'error': e.message
            }
            if e.details:
                response['details'] = e.details
            logger.warning(f"API错误: {e.message}", exc_info=True)
            return jsonify(response), e.status_code
        except HTTPException as e:
            # 处理HTTP异常
            logger.warning(f"HTTP错误: {str(e)}", exc_info=True)
            return jsonify({
                'error': str(e)
            }), e.code
        except Exception as e:
            # 处理未捕获的异常
            error_message = str(e)
            if current_app.config.get('DEBUG', False):
                # 在调试模式下包含堆栈跟踪
                error_details = traceback.format_exc()
                logger.error(f"未捕获的异常: {error_message}\n{error_details}")
                return jsonify({
                    'error': '服务器内部错误',
                    'message': error_message,
                    'traceback': error_details
                }), 500
            else:
                # 生产环境中只返回基本错误信息
                logger.error(f"未捕获的异常: {error_message}", exc_info=True)
                return jsonify({
                    'error': '服务器内部错误'
                }), 500
    return wrapper

def register_error_handlers(app):
    """注册全局错误处理器
    
    为Flask应用注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': '无效的请求'}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': '资源不存在'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': '不支持的请求方法'}), 405
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error("服务器内部错误", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500 