# Docker 构建和部署指南

## 一、本地构建 Docker 镜像

### 1. 准备工作

确保以下文件存在：
- `Dockerfile`
- `docker-compose.yml`
- `chromedriver-linux64.zip`（ChromeDriver压缩包）
- `blast_app.py`
- `species_db.json`
- `requirements.txt`
- `templates/` 目录

### 2. 构建镜像

```bash
cd /Users/bupoo/Github/localblast
docker build -t localblast:latest .
```

构建过程可能需要几分钟，会执行以下步骤：
- 安装系统依赖（BLAST+、Chrome等）
- 安装ChromeDriver
- 安装Python依赖
- 复制应用文件

### 3. 验证镜像

```bash
# 查看镜像
docker images | grep localblast

# 测试运行（可选）
docker run -d -p 5001:5001 --name localblast-test localblast:latest
docker logs localblast-test
docker stop localblast-test && docker rm localblast-test
```

## 二、部署到服务器

### 方法一：使用 Docker Compose（推荐）

#### 1. 上传文件到服务器

将以下文件/目录上传到服务器：

```bash
# 必需文件
- Dockerfile
- docker-compose.yml
- chromedriver-linux64.zip
- blast_app.py
- species_db.json
- requirements.txt
- templates/ 目录

# 可选：创建部署目录
mkdir -p /opt/localblast
cd /opt/localblast
```

#### 2. 使用 SCP 上传（从本地Mac）

```bash
# 上传整个项目（排除不需要的文件）
scp -r \
  Dockerfile \
  docker-compose.yml \
  chromedriver-linux64.zip \
  blast_app.py \
  species_db.json \
  requirements.txt \
  templates/ \
  user@your-server:/opt/localblast/
```

#### 3. 在服务器上构建和启动

```bash
# SSH登录服务器
ssh user@your-server

# 进入项目目录
cd /opt/localblast

# 构建镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 查看状态
docker compose ps
```

#### 4. 访问服务

服务将在 `http://your-server-ip:5001` 上运行

### 方法二：直接使用 Docker 命令

#### 1. 在服务器上构建

```bash
cd /opt/localblast
docker build -t localblast:latest .
```

#### 2. 运行容器

```bash
# 创建数据目录
mkdir -p /opt/localblast/uploads /opt/localblast/results

# 运行容器
docker run -d \
  --name localblast \
  -p 5001:5001 \
  -v /opt/localblast/uploads:/app/uploads \
  -v /opt/localblast/results:/app/results \
  -v /opt/localblast/species_db.json:/app/species_db.json \
  --restart unless-stopped \
  localblast:latest

# 查看日志
docker logs -f localblast
```

## 三、服务器部署检查清单

### 1. 服务器要求

- ✅ Docker 已安装（版本 20.10+）
- ✅ Docker Compose 已安装（可选，推荐）
- ✅ 端口 5001 已开放（防火墙配置）
- ✅ 至少 2GB 可用内存
- ✅ 至少 5GB 可用磁盘空间

### 2. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 5001/tcp
sudo ufw reload

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

### 3. 验证部署

```bash
# 检查容器状态
docker ps | grep localblast

# 检查服务响应
curl http://localhost:5001/

# 检查BLAST+是否可用
docker exec localblast blastn -version

# 检查ChromeDriver是否可用
docker exec localblast chromedriver --version
```

## 四、常用管理命令

### 启动/停止服务

```bash
# 使用 Docker Compose
docker compose up -d          # 启动
docker compose stop           # 停止
docker compose restart        # 重启
docker compose down           # 停止并删除容器

# 使用 Docker 命令
docker start localblast        # 启动
docker stop localblast         # 停止
docker restart localblast      # 重启
docker rm -f localblast        # 删除容器
```

### 查看日志

```bash
# Docker Compose
docker compose logs -f         # 实时日志
docker compose logs --tail=100 # 最近100行

# Docker 命令
docker logs -f localblast      # 实时日志
docker logs --tail=100 localblast  # 最近100行
```

### 更新应用

```bash
# 1. 停止服务
docker compose down

# 2. 更新代码文件（通过git pull或scp）

# 3. 重新构建镜像
docker compose build

# 4. 启动服务
docker compose up -d
```

### 备份数据

```bash
# 备份结果文件
tar -czf localblast-results-$(date +%Y%m%d).tar.gz /opt/localblast/results

# 备份上传文件
tar -czf localblast-uploads-$(date +%Y%m%d).tar.gz /opt/localblast/uploads

# 备份数据库
cp /opt/localblast/species_db.json /opt/localblast/species_db.json.backup
```

## 五、故障排查

### 1. 容器无法启动

```bash
# 查看详细错误
docker compose logs

# 检查镜像是否存在
docker images | grep localblast

# 检查端口是否被占用
netstat -tuln | grep 5001
```

### 2. BLAST+ 未找到

```bash
# 进入容器检查
docker exec -it localblast bash
blastn -version
exit
```

### 3. ChromeDriver 问题

```bash
# 检查ChromeDriver
docker exec localblast chromedriver --version

# 检查Chrome
docker exec localblast google-chrome --version
```

### 4. 内存不足

```bash
# 查看容器资源使用
docker stats localblast

# 如果内存不足，可以限制容器内存
# 在 docker-compose.yml 中添加：
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

## 六、生产环境优化建议

### 1. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. 配置 HTTPS

使用 Let's Encrypt 或云服务商提供的 SSL 证书

### 3. 设置自动重启

在 `docker-compose.yml` 中已包含 `restart: unless-stopped`

### 4. 日志管理

```bash
# 配置日志轮转
docker run ... --log-opt max-size=10m --log-opt max-file=3 ...
```

## 七、快速部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "开始部署 LocalBlast..."

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    exit 1
fi

# 构建镜像
echo "构建 Docker 镜像..."
docker compose build

# 停止旧容器
echo "停止旧容器..."
docker compose down

# 启动新容器
echo "启动服务..."
docker compose up -d

# 等待服务启动
sleep 5

# 检查状态
if docker compose ps | grep -q "Up"; then
    echo "✅ 部署成功！"
    echo "服务地址: http://$(hostname -I | awk '{print $1}'):5001"
else
    echo "❌ 部署失败，请查看日志: docker compose logs"
    exit 1
fi
```

使用：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 八、注意事项

1. **ChromeDriver 版本**：确保 `chromedriver-linux64.zip` 与 Chrome 版本兼容
2. **数据持久化**：使用 volumes 挂载 `uploads` 和 `results` 目录
3. **资源限制**：根据服务器配置调整内存和CPU限制
4. **安全**：生产环境建议配置防火墙和访问控制
5. **备份**：定期备份 `species_db.json` 和结果文件

## 九、联系支持

如遇到问题，请检查：
- Docker 日志：`docker compose logs`
- 容器状态：`docker compose ps`
- 系统资源：`docker stats`

---

**最后更新**: 2026-01-29
