"""
请求速率限制中间件
==============

限制API请求频率，防止滥用。
"""

import time
from functools import wraps
from flask import request, jsonify, current_app
import threading


class RateLimiter:
    """
    请求速率限制器
    
    使用滑动窗口算法限制每个客户端的请求频率。
    """
    
    def __init__(self, limit=60, window=60):
        """
        初始化速率限制器
        
        参数:
            limit (int): 窗口期内的最大请求数
            window (int): 窗口期大小，单位为秒
        """
        self.limit = limit
        self.window = window
        self.clients = {}
        self.lock = threading.Lock()
        
        # 启动清理过期记录的线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_records, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_expired_records(self):
        """清理过期的客户端记录，每分钟运行一次"""
        while True:
            time.sleep(60)  # 每60秒清理一次
            now = time.time()
            with self.lock:
                for client_id in list(self.clients.keys()):
                    # 过滤掉过期的请求记录
                    self.clients[client_id] = [
                        timestamp for timestamp in self.clients.get(client_id, [])
                        if now - timestamp < self.window
                    ]
                    # 如果客户端没有有效记录，则删除
                    if not self.clients[client_id]:
                        del self.clients[client_id]
    
    def is_allowed(self, client_id):
        """
        检查客户端是否允许请求
        
        参数:
            client_id (str): 客户端标识
            
        返回:
            bool: 是否允许
        """
        now = time.time()
        
        with self.lock:
            # 获取客户端的请求时间戳列表
            timestamps = self.clients.get(client_id, [])
            
            # 过滤掉过期的请求记录
            valid_timestamps = [ts for ts in timestamps if now - ts < self.window]
            
            # 检查是否超过限制
            if len(valid_timestamps) >= self.limit:
                return False
            
            # 记录新的请求
            valid_timestamps.append(now)
            self.clients[client_id] = valid_timestamps
            
            return True
    
    def get_remaining(self, client_id):
        """
        获取客户端剩余的请求次数
        
        参数:
            client_id (str): 客户端标识
            
        返回:
            int: 剩余的请求次数
        """
        now = time.time()
        
        with self.lock:
            # 获取客户端的请求时间戳列表
            timestamps = self.clients.get(client_id, [])
            
            # 过滤掉过期的请求记录
            valid_timestamps = [ts for ts in timestamps if now - ts < self.window]
            
            # 计算剩余请求次数
            return max(0, self.limit - len(valid_timestamps))


# 创建全局速率限制器实例
rate_limiter = RateLimiter()


def rate_limit(f):
    """
    请求速率限制装饰器
    
    限制每个客户端的请求频率。
    
    参数:
        f (callable): 被装饰的函数
        
    返回:
        callable: 包装后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 如果处于调试模式，则跳过速率限制
        if current_app.debug:
            return f(*args, **kwargs)
        
        # 获取客户端标识（优先使用API令牌，其次使用IP地址）
        client_id = request.headers.get('X-API-Token', request.remote_addr)
        
        # 检查是否允许请求
        if not rate_limiter.is_allowed(client_id):
            remaining = 0
            reset_time = int(time.time()) + rate_limiter.window
            
            # 设置速率限制响应头
            headers = {
                'X-RateLimit-Limit': str(rate_limiter.limit),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(reset_time),
                'Retry-After': str(rate_limiter.window)
            }
            
            return jsonify({
                'error': '请求频率过高',
                'message': f'超过速率限制，请在{rate_limiter.window}秒后重试',
                'status_code': 429
            }), 429, headers
        
        # 获取剩余的请求次数
        remaining = rate_limiter.get_remaining(client_id)
        reset_time = int(time.time()) + rate_limiter.window
        
        # 执行原函数并获取响应
        response = f(*args, **kwargs)
        
        # 如果响应是元组，则第一个元素是响应对象
        if isinstance(response, tuple):
            resp_obj = response[0]
            resp_status = response[1] if len(response) > 1 else 200
            resp_headers = response[2] if len(response) > 2 else {}
            
            # 添加速率限制响应头
            resp_headers.update({
                'X-RateLimit-Limit': str(rate_limiter.limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            })
            
            return resp_obj, resp_status, resp_headers
        else:
            # 直接返回的是响应对象
            resp_obj = response
            
            # 添加速率限制响应头
            resp_obj.headers.update({
                'X-RateLimit-Limit': str(rate_limiter.limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            })
            
            return resp_obj
    
    return decorated 