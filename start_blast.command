#!/bin/bash
# LocalBlast macOS 启动脚本
# 双击此文件即可启动BLAST服务

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 设置终端窗口标题
echo -e "\033]0;LocalBlast - 本地BLAST工具\007"

# 清屏
clear

echo "=========================================="
echo "LocalBlast - 本地BLAST工具"
echo "=========================================="
echo ""

# 检查Python环境
echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo ""
    echo "请先安装Python 3.7或更高版本："
    echo "  方法1: 访问 https://www.python.org/downloads/"
    echo "  方法2: 使用Homebrew: brew install python3"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ $PYTHON_VERSION"
echo ""

# 检查BLAST+工具
echo "[2/3] 检查BLAST+工具..."
BLAST_FOUND=false
BLAST_PATH=""

# 尝试多个可能的路径
POSSIBLE_PATHS=(
    "blastn"  # 系统PATH中
    "/opt/homebrew/bin/blastn"  # macOS Homebrew (Apple Silicon)
    "/usr/local/bin/blastn"  # macOS Homebrew (Intel) 或标准位置
    "/usr/bin/blastn"  # Linux标准位置
)

for blast_path in "${POSSIBLE_PATHS[@]}"; do
    if command -v "$blast_path" &> /dev/null || [ -f "$blast_path" ]; then
        if "$blast_path" -version &> /dev/null; then
            BLAST_FOUND=true
            BLAST_PATH="$blast_path"
            BLAST_VERSION=$("$blast_path" -version 2>&1 | head -n 1)
            echo "✅ 找到BLAST+: $BLAST_VERSION"
            echo "   路径: $BLAST_PATH"
            break
        fi
    fi
done

if [ "$BLAST_FOUND" = false ]; then
    echo "⚠️  警告: 未找到BLAST+工具"
    echo ""
    echo "请先安装BLAST+："
    echo "  使用Homebrew: brew install blast"
    echo ""
    echo "或者从NCBI官网下载："
    echo "  https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/"
    echo ""
    read -p "是否继续？(y/n): " continue_choice
    if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 检查Python依赖
echo "[3/3] 检查Python依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  检测到缺少Python依赖，正在安装..."
    echo ""
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败"
        echo "请手动运行: pip3 install -r requirements.txt"
        echo ""
        read -p "按回车键退出..."
        exit 1
    fi
    echo ""
    echo "✅ Python依赖安装完成"
else
    echo "✅ Python依赖已安装"
fi
echo ""

# 启动服务
echo "=========================================="
echo "正在启动BLAST服务..."
echo "=========================================="
echo ""
echo "服务地址: http://localhost:5001"
echo ""
echo "提示："
echo "- 保持此窗口打开以运行服务"
echo "- 关闭此窗口将停止服务"
echo "- 按 Ctrl+C 也可以停止服务"
echo ""
echo "=========================================="
echo ""

# 启动Flask应用
python3 blast_app.py

# 如果程序退出，暂停以便查看错误信息
if [ $? -ne 0 ]; then
    echo ""
    echo "程序异常退出，请查看上方错误信息"
    echo ""
    read -p "按回车键关闭窗口..."
fi
