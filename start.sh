#!/bin/bash
# 考研网站启动脚本
# 通过 nginx 反向代理对外提供服务；Flask 默认监听 5000 端口

set -e

echo "=========================================="
echo "  考研复习网站 - 启动脚本"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 仅在服务器本地加载密钥，.env 已被 .gitignore 排除
if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

if [ -z "${OPENCLAW_API_TOKEN:-}" ]; then
    echo "缺少 OPENCLAW_API_TOKEN：请在项目目录的 .env 文件中配置后再启动。"
    exit 1
fi

# 安装依赖
echo "[1/4] 安装依赖..."
pip3 install flask reportlab fpdf2 -q --break-system-packages 2>/dev/null || \
pip3 install flask reportlab fpdf2 -q --ignore-installed --break-system-packages 2>/dev/null

# 生成PDF（如需要）
if [ ! -f "pdfs/english/level1.pdf" ]; then
    echo "[2/4] 首次启动，生成词汇PDF..."
    python3 generate_pdfs.py
else
    echo "[2/4] PDF已存在，跳过生成"
fi

# 杀掉旧进程
if pgrep -f "${SCRIPT_DIR}/app.py" > /dev/null 2>&1; then
    echo "[3/4] 停止旧服务器..."
    pkill -f "${SCRIPT_DIR}/app.py" || true
    sleep 1
fi

# 启动服务器
echo "[4/4] 启动Flask服务器..."
nohup python3 app.py > server.log 2>&1 &
sleep 2

# 获取本机IP
HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "=========================================="
echo "  ✅ 服务器已启动！"
echo "  外网地址由 nginx 配置决定"
echo "  Flask 本机地址: http://localhost:5000"
echo "  日志文件: ${SCRIPT_DIR}/server.log"
echo "=========================================="
