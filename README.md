# LocalBlast

本地化BLAST序列比对工具 - 支持blastn（DNA序列比对）

## 简介

LocalBlast 是一个本地化的BLAST序列比对工具，支持blastn（DNA序列比对）功能，可以比对用户输入的查询序列与预定义的物种参考序列。无需连接NCBI服务器，所有比对在本地完成，保护数据隐私。

## 功能特点

- 🧬 支持DNA序列比对（blastn）
- 🎯 预置多种常见病原体参考序列
- 📊 生成美观的HTML结果页面
- 🚀 本地运行，数据安全
- 💻 简洁易用的Web界面

## 系统要求

1. **Python 3.7+**
2. **BLAST+工具** - 需要安装NCBI BLAST+命令行工具

### 安装BLAST+

#### macOS
```bash
brew install blast
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ncbi-blast+

# CentOS/RHEL
sudo yum install ncbi-blast+
```

#### Windows
**推荐：使用自动安装脚本**
1. 下载项目文件
2. 双击运行 `install_windows.bat`（会自动检查并安装依赖）
3. 双击运行 `start_windows.bat` 启动程序
4. 详细说明请查看 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)

**手动安装：**
从NCBI官网下载安装包：
https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/localblast.git
cd localblast
```

### 2. 安装依赖
```bash
pip3 install -r requirements.txt
```

### 3. 验证BLAST安装
```bash
blastn -version
```

### 4. 启动服务
```bash
python3 blast_app.py
# 或使用启动脚本
./start_blast.sh
```

### 5. 访问界面
打开浏览器访问：**http://localhost:5001**

## 使用方法

1. 在文本框中输入或粘贴查询序列（支持FASTA格式）
2. 从下拉菜单中选择要比对的物种
3. 点击"执行BLAST比对"按钮
4. 查看比对结果

## 项目结构

```
localblast/
├── blast_app.py          # Flask后端服务
├── species_db.json       # 物种数据库
├── templates/
│   └── blast_input.html  # 前端输入界面
├── requirements.txt      # Python依赖
├── start_blast.sh        # 启动脚本
└── README.md            # 项目说明
```

## API接口

### GET /api/species
获取所有可用物种列表

### POST /api/blast
执行BLAST比对

请求体：
```json
{
  "query_sequence": "ATGCGATCGATCG...",
  "species_id": 1
}
```

响应：
```json
{
  "success": true,
  "html": "<html>...</html>",
  "results_count": 1
}
```

## 扩展数据库

要添加更多物种，编辑 `species_db.json` 文件，添加新的物种条目：
```json
{
  "id": 11,
  "name": "物种名称",
  "code": "代码",
  "sequence": "ATCG序列...",
  "length": 序列长度
}
```

## 注意事项

1. 确保BLAST+工具已正确安装并在PATH中
2. 查询序列只能包含A、T、C、G字符
3. 首次运行可能需要一些时间来创建BLAST数据库
4. 如果遇到端口占用问题，可以修改 `blast_app.py` 中的端口号

## 故障排除

### BLAST未找到
如果提示"BLAST+未安装"，请检查：
- BLAST+是否正确安装
- 是否在系统PATH中

### 端口被占用
macOS上端口5000可能被AirPlay Receiver占用，程序默认使用5001端口。

### 比对失败
- 检查查询序列格式是否正确
- 确保序列只包含ATCG字符
- 查看控制台错误信息

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Created with ❤️ for bioinformatics research
