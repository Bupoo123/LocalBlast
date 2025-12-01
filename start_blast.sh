#!/bin/bash
# 本地化BLAST工具启动脚本

echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python"
    exit 1
fi

echo "正在检查BLAST+工具..."
if ! command -v blastn &> /dev/null; then
    echo "警告: 未找到BLAST+工具"
    echo "请先安装BLAST+："
    echo "  macOS: brew install blast"
    echo "  Linux: sudo apt-get install ncbi-blast+"
    exit 1
fi

echo "正在检查Python依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "正在安装Python依赖..."
    pip3 install -r requirements.txt
fi

echo "启动BLAST服务..."
echo ""
echo "=========================================="
echo "BLAST服务已启动！"
echo "访问 http://localhost:5001 使用BLAST工具"
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""
python3 blast_app.py

