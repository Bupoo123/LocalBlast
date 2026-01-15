# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 配置国内镜像源加速（提升构建速度）
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    (echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main" > /etc/apt/sources.list && \
     echo "deb https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
     echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main" >> /etc/apt/sources.list)

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # BLAST+工具
    ncbi-blast+ \
    # Chrome浏览器和ChromeDriver依赖
    wget \
    curl \
    gnupg \
    unzip \
    # Chrome运行依赖
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    # 其他工具
    && rm -rf /var/lib/apt/lists/*

# 安装Google Chrome
RUN wget -q --timeout=30 --tries=3 https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && \
    apt-get update && \
    apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb && \
    rm -rf /var/lib/apt/lists/* || \
    echo "警告: Chrome安装失败"

# 复制并安装ChromeDriver（使用本地zip文件，无需网络，支持完全离线部署）
COPY chromedriver-linux64.zip /tmp/chromedriver.zip
RUN unzip -q /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    ln -sf /usr/local/bin/chromedriver /app/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 && \
    chromedriver --version && \
    echo "ChromeDriver安装成功，PNG功能可用"

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖（使用清华镜像源加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用文件
COPY blast_app.py .
COPY species_db.json .
COPY templates/ ./templates/

# 创建必要的目录
RUN mkdir -p uploads results

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=blast_app.py

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python", "blast_app.py"]
