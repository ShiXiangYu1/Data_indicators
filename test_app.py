#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的Flask应用测试
================

用于测试Flask服务是否能正常运行。
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "你好，数据指标平台测试成功！"

if __name__ == "__main__":
    print("测试应用启动在 http://0.0.0.0:8888/")
    app.run(host="0.0.0.0", port=8888, debug=True) 