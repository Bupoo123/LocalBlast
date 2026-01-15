# LocalBlast Docker 部署指南

## 📦 快速开始

### 前提条件

- Docker 已安装（版本 20.10+）
- Docker Compose 已安装（版本 1.29+）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/localblast.git
cd localblast
git checkout docker  # 切换到docker分支
```

### 2. 使用 docker-compose 启动（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 访问服务

打开浏览器访问：**http://localhost:5001**

## 🚀 阿里云 ECS 部署

### 方法一：直接部署到已有服务器

1. **上传项目文件到服务器**

```bash
# 使用scp上传
scp -r /path/to/localblast root@your_server_ip:/opt/

# 或使用git clone
ssh root@your_server_ip
cd /opt
git clone https://github.com/yourusername/localblast.git
cd localblast
git checkout docker
```

2. **启动服务**

```bash
cd /opt/localblast
docker-compose up -d
```

3. **配置安全组**

在阿里云控制台：
- 进入 ECS 实例 → 安全组
- 添加入站规则：
  - 端口：5001
  - 协议：TCP
  - 源：0.0.0.0/0（或限制特定IP）

4. **访问服务**

通过公网IP访问：`http://your_server_ip:5001`

### 方法二：使用阿里云容器镜像服务（ACK）

1. **构建镜像并推送到阿里云容器镜像服务**

```bash
# 登录阿里云容器镜像服务
docker login --username=your_username registry.cn-hangzhou.aliyuncs.com

# 构建镜像
docker build -t registry.cn-hangzhou.aliyuncs.com/your_namespace/localblast:latest .

# 推送镜像
docker push registry.cn-hangzhou.aliyuncs.com/your_namespace/localblast:latest
```

2. **在ACK中创建应用**
   - 进入容器服务控制台
   - 创建无状态应用
   - 选择刚才推送的镜像
   - 设置端口映射：5001:5001
   - 配置存储卷（可选）

## 📋 手动部署（不使用docker-compose）

### 1. 构建镜像

```bash
docker build -t localblast:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name localblast \
  -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  --restart unless-stopped \
  localblast:latest
```

### 3. 查看日志

```bash
docker logs -f localblast
```

## 🔧 配置说明

### 环境变量

可以通过环境变量配置应用：

```yaml
# 在docker-compose.yml中添加
environment:
  - PYTHONUNBUFFERED=1
  - FLASK_ENV=production
  - FLASK_DEBUG=False
```

### 数据持久化

重要数据会保存在以下目录：
- `uploads/` - 用户上传的文件
- `results/` - 处理结果

这些目录已通过 volumes 挂载到主机，确保数据持久化。

### 更新应用

```bash
# 停止并删除旧容器
docker-compose down

# 重新构建镜像（如果有代码更新）
docker-compose build

# 启动新容器
docker-compose up -d
```

## 📊 资源监控

### 查看容器状态

```bash
docker ps
docker stats localblast
```

### 查看日志

```bash
# 实时日志
docker-compose logs -f

# 最近100行日志
docker-compose logs --tail 100
```

### 健康检查

容器包含健康检查，可以通过以下命令查看：

```bash
docker inspect localblast | grep Health -A 10
```

## 🔒 安全建议

### 1. 使用 Nginx 反向代理（推荐）

```nginx
# /etc/nginx/sites-available/localblast
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. 配置 SSL 证书（HTTPS）

使用 Let's Encrypt 或阿里云 SSL 证书：

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your_domain.com
```

### 3. 限制访问IP

在安全组中限制访问来源，只允许特定IP访问。

## 🐛 故障排除

### 问题1：无法访问服务

**检查步骤：**
1. 检查容器是否运行：`docker ps`
2. 检查端口映射：`docker port localblast`
3. 检查防火墙/安全组设置
4. 查看容器日志：`docker logs localblast`

### 问题2：BLAST功能不可用

**检查步骤：**
```bash
# 进入容器
docker exec -it localblast bash

# 检查BLAST+是否安装
blastn -version
```

### 问题3：PNG生成失败

**检查步骤：**
```bash
# 进入容器
docker exec -it localblast bash

# 检查Chrome是否安装
google-chrome --version
```

### 问题4：内存不足

如果服务器内存较小（如2GB），可能出现内存不足：

**解决方案：**
1. 升级服务器配置（推荐）
2. 限制容器内存使用：
```yaml
# 在docker-compose.yml中添加
deploy:
  resources:
    limits:
      memory: 1.5G
```

## 📝 性能优化

### 1. 使用多阶段构建（减小镜像大小）

当前Dockerfile已经比较精简，如需进一步优化可以使用多阶段构建。

### 2. 资源限制

在docker-compose.yml中添加资源限制：

```yaml
services:
  localblast:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 3. 定期清理

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune
```

## 📦 备份和恢复

### 备份数据

```bash
# 备份uploads和results目录
tar -czf localblast_backup_$(date +%Y%m%d).tar.gz uploads/ results/ species_db.json
```

### 恢复数据

```bash
# 解压备份文件
tar -xzf localblast_backup_YYYYMMDD.tar.gz

# 重启容器
docker-compose restart
```

## 🎯 生产环境建议

1. **使用域名访问**：配置域名解析到服务器IP
2. **启用HTTPS**：使用SSL证书加密传输
3. **定期备份**：备份重要数据和配置文件
4. **监控告警**：设置资源使用告警
5. **日志管理**：配置日志轮转和集中管理

## 📞 技术支持

如遇到问题，请：
1. 查看容器日志：`docker logs localblast`
2. 检查系统资源：`docker stats localblast`
3. 查看GitHub Issues

---

**最后更新**：2026-01-15
