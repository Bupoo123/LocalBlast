# LocalBlast v1.4.0 发布说明

## 🎉 Query ID 优化版本

LocalBlast v1.4.0 优化了 Query ID 的生成方式，改为随机7位数（1-5开头），并统一了界面显示。

## ✨ 主要更新

### 功能优化

- 🎲 **Query ID 随机生成** - Query ID 现在使用随机7位数生成，第一位为1-5，后6位为0-9
- 📝 **Description 列统一** - Description 列统一显示为 "None"，保持界面一致性
- 🔢 **唯一性保证** - 每次生成结果时都会生成新的随机 Query ID，确保唯一性

### 界面改进

- 🎨 **显示优化** - Subject Descr 始终显示为 "None"
- 📊 **表格一致性** - 所有描述相关字段统一显示格式

## 📦 下载

### 方法一：下载源码（推荐）

1. 点击右侧 **"Source code (zip)"** 下载完整源码
2. 解压到任意文件夹
3. 按照 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) 中的说明安装

### 方法二：使用Git克隆

```bash
git clone https://github.com/Bupoo123/LocalBlast.git
cd LocalBlast
git checkout v1.4.0
```

## 🚀 快速安装（Windows）

1. **安装Python 3.7+**
   - 下载：https://www.python.org/downloads/
   - **重要**：安装时勾选 "Add Python to PATH"
   - 推荐版本：Python 3.8、3.9、3.10 或 3.11（避免Pillow兼容性问题）

2. **安装BLAST+**
   - 下载：https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
   - 下载Windows版本（如：`ncbi-blast-*-win64.exe`）
   - **重要**：安装时选择 "Add to PATH"

3. **安装依赖**
   - 双击运行 `install_windows.bat`
   - 或手动运行：`pip install -r requirements.txt`

4. **启动程序**
   - 打开命令提示符（CMD），切换到项目目录：
     ```cmd
     cd /d C:\path\to\LocalBlast
     python blast_app.py
     ```
   - 等待显示"服务地址: http://localhost:5001"后，在浏览器中打开 http://localhost:5001

## 📋 详细安装说明

- **Windows用户**：请查看 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- **macOS/Linux用户**：请查看 [README.md](README.md)

## 🔄 从旧版本升级

如果您已经安装了旧版本，只需：

1. 下载新版本源码或使用 `git pull` 更新
2. 重新运行 `install_windows.bat`（如果需要更新依赖）
3. 重启程序即可

## 📝 使用说明

### 单序列比对

1. 访问 http://localhost:5001
2. 输入或粘贴查询序列
3. 选择要比对的物种（或留空比对所有物种）
4. 点击"执行BLAST比对"
5. 查看结果，每次都会生成新的随机 Query ID

### 批量处理

1. 点击"批量上传"链接
2. 选择多个.seq文件
3. 等待处理完成
4. 下载包含HTML结果和CSV摘要的ZIP文件

## 🆕 新功能说明

### 随机 Query ID

- **格式**：7位数字
- **第一位**：1-5（随机）
- **后6位**：0-9（随机）
- **示例**：`1234567`、`4567890`、`2345678` 等

每次执行 BLAST 比对时，系统会自动生成一个新的随机 Query ID，确保每个结果都有唯一的标识符。

## 🔧 系统要求

- **Python**：3.7+（推荐 3.8-3.11）
- **BLAST+**：最新版本
- **磁盘空间**：至少 500MB 可用空间

## 📚 文档

- [README.md](README.md) - 项目说明和API文档
- [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) - Windows详细安装指南
- [分发说明.md](分发说明.md) - 打包分发指南

## 🐛 已知问题

- 首次运行需要创建BLAST数据库，可能需要一些时间
- Windows用户需要确保Python和BLAST+已添加到系统PATH
- 使用Python 3.12+可能导致Pillow安装问题，建议使用3.8-3.11

## 🙏 致谢

感谢所有使用和反馈的用户！

## 📄 许可证

本项目仅供学习和研究使用。

---

**下载地址**：点击右侧 "Source code (zip)" 下载完整源码包

**版本历史**：
- v1.0.0 - 初始版本
- v1.1.0 - 样式优化版本
- v1.2.0 - 功能增强版本（新增Common Name和Taxid列）
- v1.3.0 - 兼容性和文档优化版本
- **v1.4.0** - Query ID 优化版本（当前版本）

