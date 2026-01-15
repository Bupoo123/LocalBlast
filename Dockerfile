# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

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
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

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
