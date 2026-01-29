#!/bin/bash
# 批量上传文件到服务器

SERVER="ubuntu@172.17.71.123"
REMOTE_DIR="/opt/localblast"

echo "=========================================="
echo "上传文件到服务器"
echo "=========================================="
echo "服务器: $SERVER"
echo "目录: $REMOTE_DIR"
echo ""

# 上传单个文件
upload_file() {
    echo "上传 $1..."
    scp "$1" "$SERVER:$REMOTE_DIR/" || {
        echo "❌ 上传 $1 失败"
        exit 1
    }
}

# 上传目录
upload_dir() {
    echo "上传目录 $1..."
    scp -r "$1" "$SERVER:$REMOTE_DIR/" || {
        echo "❌ 上传目录 $1 失败"
        exit 1
    }
}

# 检查文件是否存在
check_file() {
    if [ ! -e "$1" ]; then
        echo "❌ 文件不存在: $1"
        exit 1
    fi
}

# 检查必需文件
echo "检查本地文件..."
check_file Dockerfile
check_file docker-compose.yml
check_file blast_app.py
check_file species_db.json
check_file requirements.txt
check_file chromedriver-linux64.zip
check_file templates

echo "✅ 所有文件存在"
echo ""

# 创建远程目录
echo "创建远程目录..."
ssh "$SERVER" "mkdir -p $REMOTE_DIR" || {
    echo "❌ 无法连接到服务器或创建目录"
    exit 1
}

echo ""

# 上传所有必需文件
upload_file Dockerfile
upload_file docker-compose.yml
upload_file blast_app.py
upload_file species_db.json
upload_file requirements.txt
upload_file chromedriver-linux64.zip
upload_dir templates

echo ""
echo "=========================================="
echo "✅ 所有文件已上传成功！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. SSH登录服务器:"
echo "   ssh $SERVER"
echo ""
echo "2. 进入项目目录:"
echo "   cd $REMOTE_DIR"
echo ""
echo "3. 构建并启动服务:"
echo "   docker compose build"
echo "   docker compose up -d"
echo "   docker compose logs -f"
echo ""
