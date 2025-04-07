#!/bin/bash

# XMonitor生产环境启动脚本
# 这个脚本用于在生产环境中启动XMonitor服务

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 激活Python虚拟环境
source "$PROJECT_DIR/venv/bin/activate"

# 工作目录
cd "$PROJECT_DIR"

# 检查Gunicorn是否已安装
if ! pip show gunicorn > /dev/null; then
    echo "正在安装Gunicorn..."
    pip install gunicorn
fi

# 检查是否有.env文件，如果没有则从示例创建
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo "警告: 已从示例创建.env文件，但您需要编辑此文件并填入您的实际配置信息"
    else
        echo "错误: 找不到.env或.env.example文件，请创建.env文件并配置必要的环境变量"
        exit 1
    fi
fi

# 确保日志目录存在
mkdir -p "$PROJECT_DIR/logs"

# 启动Gunicorn
echo "启动XMonitor服务..."
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class=gevent \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level=info \
    --access-logfile="$PROJECT_DIR/logs/access.log" \
    --error-logfile="$PROJECT_DIR/logs/error.log" \
    --chdir "$PROJECT_DIR" \
    "src.app:app" 