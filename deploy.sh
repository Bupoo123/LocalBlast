#!/bin/bash
# LocalBlast Docker 快速部署脚本

set -e

echo "=========================================="
echo "LocalBlast Docker 部署脚本"
echo "=========================================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "⚠️  警告: 未找到 docker-compose"
    echo "将使用 docker 命令直接部署"
    USE_COMPOSE=false
else
    USE_COMPOSE=true
    echo "✅ 找到 Docker Compose"
fi

# 检查必需文件
echo "检查必需文件..."
REQUIRED_FILES=(
    "Dockerfile"
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

# 创建数据目录
echo "创建数据目录..."
mkdir -p uploads results
echo "✅ 数据目录已创建"
echo ""

# 构建镜像
echo "=========================================="
echo "构建 Docker 镜像..."
echo "=========================================="
if [ "$USE_COMPOSE" = true ]; then
    docker compose build
else
    docker build -t localblast:latest .
fi

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "✅ 镜像构建成功"
echo ""

# 停止旧容器（如果存在）
echo "停止旧容器..."
if [ "$USE_COMPOSE" = true ]; then
    docker compose down 2>/dev/null || true
else
    docker stop localblast 2>/dev/null || true
    docker rm localblast 2>/dev/null || true
fi
echo "✅ 旧容器已停止"
echo ""

# 启动服务
echo "=========================================="
echo "启动服务..."
echo "=========================================="
if [ "$USE_COMPOSE" = true ]; then
    docker compose up -d
else
    docker run -d \
        --name localblast \
        -p 5001:5001 \
        -v "$(pwd)/uploads:/app/uploads" \
        -v "$(pwd)/results:/app/results" \
        -v "$(pwd)/species_db.json:/app/species_db.json" \
        --restart unless-stopped \
        localblast:latest
fi

if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败"
    exit 1
fi

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo "=========================================="
echo "检查服务状态..."
echo "=========================================="
if [ "$USE_COMPOSE" = true ]; then
    docker compose ps
    if docker compose ps | grep -q "Up"; then
        STATUS="运行中"
    else
        STATUS="未运行"
    fi
else
    if docker ps | grep -q "localblast"; then
        STATUS="运行中"
        docker ps | grep localblast
    else
        STATUS="未运行"
    fi
fi

echo ""
if [ "$STATUS" = "运行中" ]; then
    echo "✅ 部署成功！"
    echo ""
    echo "=========================================="
    echo "服务信息"
    echo "=========================================="
    echo "服务地址: http://localhost:5001"
    
    # 获取服务器IP（如果在服务器上运行）
    if command -v hostname &> /dev/null; then
        SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "未知")
        if [ "$SERVER_IP" != "未知" ] && [ "$SERVER_IP" != "" ]; then
            echo "服务器地址: http://$SERVER_IP:5001"
        fi
    fi
    
    echo ""
    echo "常用命令:"
    if [ "$USE_COMPOSE" = true ]; then
        echo "  查看日志: docker compose logs -f"
        echo "  停止服务: docker compose down"
        echo "  重启服务: docker compose restart"
    else
        echo "  查看日志: docker logs -f localblast"
        echo "  停止服务: docker stop localblast"
        echo "  重启服务: docker restart localblast"
    fi
    echo "=========================================="
else
    echo "❌ 部署失败，服务未运行"
    echo ""
    echo "请查看日志排查问题:"
    if [ "$USE_COMPOSE" = true ]; then
        echo "  docker compose logs"
    else
        echo "  docker logs localblast"
    fi
    exit 1
fi
