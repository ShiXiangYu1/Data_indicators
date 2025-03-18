from functools import wraps
from flask import jsonify
from typing import Callable, Any

def handle_api_error(f: Callable) -> Callable:
    """
    API错误处理装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'error': '参数错误',
                'message': str(e)
            }), 400
        except TypeError as e:
            return jsonify({
                'error': '类型错误',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'error': '服务器错误',
                'message': str(e)
            }), 500
    return decorated_function 