#!/bin/bash
# LocalBlast 服务器更新脚本
# 用于更新已部署的 LocalBlast 服务

set -e

# 服务器配置
SERVER_USER="ubuntu"
SERVER_IP="172.17.71.123"
SERVER_PASSWORD="Matridx01"
REMOTE_DIR="/opt/localblast"

echo "=========================================="
echo "LocalBlast 服务器更新脚本"
echo "=========================================="
echo "服务器: $SERVER_USER@$SERVER_IP"
echo "目录: $REMOTE_DIR"
echo ""

# 检查必需文件
echo "检查本地文件..."
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "blast_app.py"
    "species_db.json"
    "requirements.txt"
    "chromedriver-linux64.zip"
    "templates"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo "❌ 缺少必需文件:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 所有必需文件存在"
echo ""

# 检查 sshpass 是否安装（用于密码认证）
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  未安装 sshpass，正在安装..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ 请先安装 Homebrew，然后运行: brew install hudochenkov/sshpass/sshpass"
            exit 1
        fi
    else
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

echo "=========================================="
echo "步骤 1: 连接到服务器并停止旧服务"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /opt/localblast || cd ~/localblast || { echo "未找到项目目录，将创建新目录"; mkdir -p /opt/localblast; cd /opt/localblast; }

echo "停止旧容器..."
if command -v docker-compose &> /dev/null; then
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
elif docker compose version &> /dev/null 2>&1; then
    docker compose down 2>/dev/null || true
else
    docker stop localblast 2>/dev/null || true
    docker rm localblast 2>/dev/null || true
fi

echo "✅ 旧服务已停止"
ENDSSH

echo ""
echo "=========================================="
echo "步骤 2: 上传文件到服务器"
echo "=========================================="

# 创建远程目录
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "mkdir -p $REMOTE_DIR"

# 上传文件
echo "上传 Dockerfile..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no Dockerfile "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 docker-compose.yml..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no docker-compose.yml "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 blast_app.py..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no blast_app.py "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 species_db.json..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no species_db.json "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 requirements.txt..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no requirements.txt "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 chromedriver-linux64.zip..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no chromedriver-linux64.zip "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "上传 templates 目录..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r templates "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"

echo "✅ 所有文件已上传"
echo ""

echo "=========================================="
echo "步骤 3: 在服务器上构建和启动服务"
echo "=========================================="

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << ENDSSH
cd $REMOTE_DIR

echo "创建数据目录..."
mkdir -p uploads results

echo "构建 Docker 镜像..."
if command -v docker-compose &> /dev/null; then
    docker-compose build
elif docker compose version &> /dev/null 2>&1; then
    docker compose build
else
    docker build -t localblast:latest .
fi

if [ \$? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "✅ 镜像构建成功"
echo ""

echo "启动服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
elif docker compose version &> /dev/null 2>&1; then
    docker compose up -d
else
    docker run -d \
        --name localblast \
        -p 5001:5001 \
        -v \$(pwd)/uploads:/app/uploads \
        -v \$(pwd)/results:/app/results \
        -v \$(pwd)/species_db.json:/app/species_db.json \
        --restart unless-stopped \
        localblast:latest
fi

echo "等待服务启动..."
sleep 5

echo ""
echo "检查服务状态..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
    docker compose ps 2>/dev/null || docker-compose ps
else
    docker ps | grep localblast || echo "容器未运行"
fi

echo ""
echo "✅ 服务已启动"
ENDSSH

echo ""
echo "=========================================="
echo "更新完成！"
echo "=========================================="
echo ""
echo "服务地址: http://$SERVER_IP:5001"
echo ""
echo "查看日志命令:"
echo "  sshpass -p '$SERVER_PASSWORD' ssh $SERVER_USER@$SERVER_IP 'cd $REMOTE_DIR && docker compose logs -f'"
echo ""
echo "或者直接SSH登录查看:"
echo "  ssh $SERVER_USER@$SERVER_IP"
echo "  cd $REMOTE_DIR"
echo "  docker compose logs -f"
echo ""
