#!/bin/bash
# 应用启动脚本

set -e

# 设置默认值
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-info}
export MAX_REQUESTS=${MAX_REQUESTS:-1000}
export MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}
export TIMEOUT=${TIMEOUT:-120}

# 打印启动信息
echo "====================================================="
echo "数据指标分析系统启动 - $(date)"
echo "====================================================="
echo "应用版本: 1.0.0"
echo "环境: ${ENVIRONMENT:-production}"
echo "端口: ${PORT}"
echo "工作进程: ${WORKERS}"
echo "日志级别: ${LOG_LEVEL}"
echo "====================================================="

# 检查环境变量
if [ -z "$REDIS_URL" ]; then
    echo "[警告] REDIS_URL 未设置，将使用内存缓存"
fi

# 等待依赖服务
echo "检查依赖服务..."
# 如果有Redis，则检查连接
if [ ! -z "$REDIS_URL" ]; then
    echo "等待Redis服务就绪..."
    # 添加等待逻辑
fi

# 运行数据库迁移（如果需要）
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "运行数据库迁移..."
    # 添加数据库迁移命令
fi

# 初始化应用
echo "初始化应用..."
# 添加任何需要的初始化命令

# 启动应用
echo "启动应用服务器..."
exec gunicorn data_insight.app:app \
    --bind 0.0.0.0:${PORT} \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level ${LOG_LEVEL} \
    --max-requests ${MAX_REQUESTS} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER} \
    --timeout ${TIMEOUT} \
    --access-logfile - \
    --error-logfile - \
    --capture-output 