# 服务器更新指南 - 手动步骤

## 服务器信息
- **服务器**: ubuntu@172.17.71.123
- **密码**: Matridx01
- **目录**: /opt/localblast

## 更新步骤

### 方法一：使用更新脚本（需要先安装 sshpass）

#### 1. 安装 sshpass（macOS）

```bash
brew install hudochenkov/sshpass/sshpass
```

#### 2. 运行更新脚本

```bash
cd /Users/bupoo/Github/localblast
./update_server.sh
```

### 方法二：手动更新（推荐）

#### 步骤 1: 停止旧服务

```bash
ssh ubuntu@172.17.71.123
# 输入密码: Matridx01

cd /opt/localblast
# 或者如果项目在其他位置
cd ~/localblast

# 停止旧容器
docker compose down
# 或者
docker-compose down
# 或者
docker stop localblast && docker rm localblast
```

#### 步骤 2: 从本地 Mac 上传文件

在本地 Mac 终端执行：

```bash
cd /Users/bupoo/Github/localblast

# 上传文件（需要输入密码）
scp Dockerfile ubuntu@172.17.71.123:/opt/localblast/
scp docker-compose.yml ubuntu@172.17.71.123:/opt/localblast/
scp blast_app.py ubuntu@172.17.71.123:/opt/localblast/
scp species_db.json ubuntu@172.17.71.123:/opt/localblast/
scp requirements.txt ubuntu@172.17.71.123:/opt/localblast/
scp chromedriver-linux64.zip ubuntu@172.17.71.123:/opt/localblast/

# 上传 templates 目录
scp -r templates ubuntu@172.17.71.123:/opt/localblast/
```

#### 步骤 3: 在服务器上构建和启动

```bash
ssh ubuntu@172.17.71.123
cd /opt/localblast

# 创建数据目录（如果不存在）
mkdir -p uploads results

# 构建镜像
docker compose build
# 或者
docker-compose build
# 或者
docker build -t localblast:latest .

# 启动服务
docker compose up -d
# 或者
docker-compose up -d
# 或者
docker run -d \
  --name localblast \
  -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/species_db.json:/app/species_db.json \
  --restart unless-stopped \
  localblast:latest

# 查看日志
docker compose logs -f
```

#### 步骤 4: 验证服务

```bash
# 检查容器状态
docker ps | grep localblast

# 检查服务响应
curl http://localhost:5001/

# 查看日志
docker compose logs -f
```

## 一键上传脚本（本地 Mac 执行）

创建并运行以下脚本，可以批量上传所有文件：

```bash
#!/bin/bash
# 批量上传文件到服务器

SERVER="ubuntu@172.17.71.123"
REMOTE_DIR="/opt/localblast"

echo "上传文件到服务器..."

# 上传单个文件
upload_file() {
    echo "上传 $1..."
    scp "$1" "$SERVER:$REMOTE_DIR/"
}

# 上传目录
upload_dir() {
    echo "上传目录 $1..."
    scp -r "$1" "$SERVER:$REMOTE_DIR/"
}

# 上传所有必需文件
upload_file Dockerfile
upload_file docker-compose.yml
upload_file blast_app.py
upload_file species_db.json
upload_file requirements.txt
upload_file chromedriver-linux64.zip
upload_dir templates

echo "✅ 所有文件已上传"
echo ""
echo "现在请SSH登录服务器执行构建和启动命令："
echo "  ssh $SERVER"
echo "  cd $REMOTE_DIR"
echo "  docker compose build"
echo "  docker compose up -d"
```

保存为 `upload_files.sh`，然后：

```bash
chmod +x upload_files.sh
./upload_files.sh
```

## 常见问题

### 1. 如果找不到项目目录

```bash
ssh ubuntu@172.17.71.123
sudo mkdir -p /opt/localblast
sudo chown ubuntu:ubuntu /opt/localblast
cd /opt/localblast
```

### 2. 如果端口被占用

```bash
# 检查端口占用
sudo netstat -tuln | grep 5001

# 停止占用端口的进程
docker stop $(docker ps -q --filter "publish=5001")
```

### 3. 如果构建失败

```bash
# 查看详细错误
docker compose build --no-cache

# 检查磁盘空间
df -h
```

### 4. 如果服务无法启动

```bash
# 查看日志
docker compose logs

# 检查容器状态
docker ps -a | grep localblast
```

## 更新后验证

1. **访问服务**: http://172.17.71.123:5001
2. **检查功能**: 上传一个测试文件，验证BLAST功能
3. **检查PNG生成**: 验证PNG图片生成功能是否正常

## 回滚（如果需要）

如果新版本有问题，可以回滚到旧版本：

```bash
ssh ubuntu@172.17.71.123
cd /opt/localblast

# 停止新容器
docker compose down

# 使用旧镜像（如果有）
docker run -d \
  --name localblast \
  -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/species_db.json:/app/species_db.json \
  --restart unless-stopped \
  localblast:old  # 使用旧标签
```

---

**提示**: 建议配置 SSH 密钥认证，避免每次输入密码。
