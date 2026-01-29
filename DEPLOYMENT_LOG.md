# LocalBlast Docker 部署日志

**部署日期**：2026年1月15日  
**部署环境**：阿里云 ECS (华东1-杭州)  
**服务器IP**：120.26.172.158  
**容器名称**：localblast

---

## 📋 部署概览

本次部署将 LocalBlast 应用容器化并部署到阿里云 ECS 服务器，实现了完整的 Docker 化部署，包括 BLAST+、Chrome、ChromeDriver 等所有依赖的集成。

---

## 🚀 部署步骤

### 1. 准备阶段

#### 1.1 创建 Docker 相关文件
- ✅ 创建 `Dockerfile` - 基于 Python 3.9-slim，包含所有系统依赖
- ✅ 创建 `docker-compose.yml` - Docker Compose 配置文件
- ✅ 创建 `.dockerignore` - 排除不需要的文件
- ✅ 创建 `DOCKER_DEPLOY.md` - 部署文档

#### 1.2 推送到代码仓库
- ✅ 创建 `docker` 分支
- ✅ 推送到 GitHub 和 Gitee

---

### 2. 服务器环境准备

#### 2.1 服务器配置
- **规格**：2核 CPU，2GB 内存，40GB 系统盘
- **操作系统**：Linux (已预装 Docker 26.1.3)
- **地域**：华东1（杭州）

#### 2.2 克隆代码
```bash
git clone -b docker https://gitee.com/bupoo/LocalBlast.git
cd LocalBlast
```

---

### 3. Docker 镜像构建

#### 3.1 首次构建遇到的问题

**问题1：docker-compose 命令不可用**
- **错误**：`/usr/local/bin/docker-compose: line 1: syntax error near unexpected token 'newline'`
- **原因**：docker-compose 安装不正确或版本不兼容
- **解决方案**：使用 `docker compose`（新版本，注意是空格）或直接使用 `docker` 命令

**问题2：Docker 权限问题**
- **错误**：`permission denied while trying to connect to the Docker daemon socket`
- **原因**：当前用户没有 Docker 权限
- **解决方案**：使用 `sudo` 执行 docker 命令，或添加用户到 docker 组

**问题3：找不到 Dockerfile**
- **错误**：`ERROR: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory`
- **原因**：目录结构嵌套，Dockerfile 在 `LocalBlast/LocalBlast/` 目录下
- **解决方案**：进入正确的目录 `cd LocalBlast/LocalBlast`

#### 3.2 优化构建过程

**问题4：apt-get 下载缓慢**
- **现象**：`apt-get update` 步骤耗时很长（200+秒）
- **原因**：使用 Debian 官方源，国内访问慢
- **解决方案**：在 Dockerfile 中添加国内镜像源配置
```dockerfile
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
```

**问题5：Chrome 安装失败**
- **错误1**：`apt-key: not found` - 新版本 Debian 已弃用 apt-key
- **错误2**：Google 访问受限 - 无法从 Google 官方源下载 Chrome
- **解决方案**：
  - 使用新方法安装 Chrome（gpg --dearmor）
  - 直接下载 Chrome deb 包安装
  - 使用 `wget` 下载 Chrome deb 包

**问题6：Python pip 下载慢**
- **解决方案**：使用清华镜像源
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3.3 最终构建成功
```bash
sudo docker build -t localblast:latest .
```
- **构建时间**：约 82 秒
- **镜像大小**：约 1-2GB

---

### 4. 容器运行

#### 4.1 启动容器
```bash
sudo docker run -d \
  --name localblast \
  -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/species_db.json:/app/species_db.json \
  --restart unless-stopped \
  localblast:latest
```

#### 4.2 验证服务
- ✅ 容器启动成功
- ✅ 服务运行在 5001 端口
- ✅ 可以通过 `http://120.26.172.158:5001` 访问

---

### 5. ChromeDriver 安装（关键问题）

#### 5.1 问题发现
- **现象**：PNG 生成功能无法使用
- **检查结果**：
  - ✅ Chrome 已安装：Google Chrome 144.0.7559.59
  - ✅ selenium 已安装：4.14.0
  - ✅ Pillow 已安装：10.0.0
  - ❌ ChromeDriver 未找到

#### 5.2 尝试解决过程

**尝试1：使用 webdriver-manager 自动下载**
- **错误**：`Could not reach host. Are you offline?`
- **原因**：容器内无法访问 Google 服务器（被墙）

**尝试2：使用国内镜像源下载**
- **错误1**：npm 镜像 404 - 版本不存在
- **错误2**：GitHub Releases 404 - 版本路径错误
- **原因**：镜像源没有对应版本或路径不正确

**尝试3：从主机上传文件**
- **问题1**：SSH 密码认证失败
  - **原因**：密码不正确或服务器配置问题
  - **解决方案**：重置 root 用户密码
- **问题2**：scp 命令执行位置错误
  - **错误**：在服务器上执行 scp（应该在本机执行）
  - **解决方案**：在 Mac 上执行 scp 上传

**尝试4：在服务器上直接下载**
- **问题**：服务器也无法访问 Google 服务器
- **解决方案**：在 Mac 上下载后上传

#### 5.3 最终解决方案

**步骤1：在 Mac 上下载 ChromeDriver**
- 从 Chrome for Testing 下载页面下载对应版本
- 文件：`chromedriver-linux64.zip`
- 版本：144.0.7559.59（匹配 Chrome 版本）

**步骤2：上传到服务器**
```bash
# 在 Mac 上执行
scp chromedriver-linux64/chromedriver root@120.26.172.158:/tmp/chromedriver
```

**步骤3：复制到容器**
```bash
# 在服务器上执行
sudo docker cp /tmp/chromedriver localblast:/usr/local/bin/chromedriver
sudo docker exec -it localblast chmod +x /usr/local/bin/chromedriver
```

**步骤4：创建符号链接**
- **问题**：代码查找路径是 `/app/chromedriver`，但文件在 `/usr/local/bin/chromedriver`
- **解决方案**：创建符号链接
```bash
docker exec -it localblast ln -s /usr/local/bin/chromedriver /app/chromedriver
```

**步骤5：重启容器**
```bash
docker restart localblast
```

#### 5.4 验证成功
- ✅ ChromeDriver 版本：144.0.7559.59
- ✅ 符号链接创建成功
- ✅ PNG 功能正常工作

---

## 🔧 遇到的问题总结

### 网络相关问题
1. **Debian 官方源访问慢** → 使用国内镜像源（中科大镜像）
2. **Google 服务被墙** → 本地下载后上传
3. **Python pip 下载慢** → 使用清华镜像源

### 权限相关问题
1. **Docker 权限不足** → 使用 sudo 或添加用户到 docker 组
2. **SSH 密码认证失败** → 重置 root 密码

### 路径相关问题
1. **Dockerfile 路径错误** → 进入正确的目录
2. **ChromeDriver 路径不匹配** → 创建符号链接

### 工具版本问题
1. **apt-key 已弃用** → 使用 gpg --dearmor 新方法
2. **docker-compose 不可用** → 使用 docker compose 或直接 docker 命令

---

## ✅ 最终配置

### 容器信息
- **镜像名称**：localblast:latest
- **容器名称**：localblast
- **端口映射**：5001:5001
- **数据卷挂载**：
  - `./uploads:/app/uploads`
  - `./results:/app/results`
  - `./species_db.json:/app/species_db.json`

### 已安装组件
- ✅ Python 3.9
- ✅ BLAST+ (ncbi-blast+)
- ✅ Google Chrome 144.0.7559.59
- ✅ ChromeDriver 144.0.7559.59
- ✅ Flask 3.0.0
- ✅ selenium 4.14.0
- ✅ Pillow 10.0.0
- ✅ 其他 Python 依赖

### 服务状态
- ✅ 服务正常运行
- ✅ 可通过公网访问：http://120.26.172.158:5001
- ✅ HTML 结果生成正常
- ✅ PNG 图片生成正常
- ✅ 批量处理功能正常

---

## 📝 经验总结

### 成功经验
1. **使用国内镜像源**：大幅提升构建速度
2. **分步解决问题**：先让服务运行，再解决 PNG 功能
3. **符号链接方案**：快速解决路径不匹配问题

### 改进建议
1. **Dockerfile 优化**：
   - 在构建时自动下载并安装 ChromeDriver
   - 使用多阶段构建减小镜像大小
   - 添加健康检查

2. **代码优化**：
   - 修改代码支持查找系统路径的 ChromeDriver
   - 改进错误提示信息

3. **部署流程优化**：
   - 创建自动化部署脚本
   - 添加部署前检查清单

---

## 🎯 后续优化方向

1. **持久化 ChromeDriver**：修改 Dockerfile，在构建时包含 ChromeDriver
2. **代码改进**：让代码自动查找系统 PATH 中的 ChromeDriver
3. **监控告警**：添加容器健康检查和监控
4. **备份策略**：定期备份数据和配置

---

## 📞 故障排除参考

### 常见问题
1. **容器无法启动**：检查端口是否被占用，查看日志 `docker logs localblast`
2. **PNG 功能不可用**：检查 ChromeDriver 是否存在 `docker exec -it localblast chromedriver --version`
3. **服务无法访问**：检查安全组是否开放 5001 端口

### 常用命令
```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f localblast

# 进入容器
docker exec -it localblast bash

# 重启容器
docker restart localblast

# 查看资源使用
docker stats localblast
```

---

**部署完成时间**：2026年1月15日 15:00  
**部署状态**：✅ 成功  
**功能状态**：✅ 全部正常
