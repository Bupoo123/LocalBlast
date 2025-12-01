# LocalBlast v1.0.0 发布说明

## 🎉 首个稳定版本

LocalBlast v1.0.0 是一个功能完整的本地化BLAST序列比对工具，支持单序列和批量序列比对。

## ✨ 主要功能

- 🧬 **DNA序列比对（blastn）** - 支持本地blastn比对，无需连接NCBI服务器
- 🎯 **预置94种常见病原体参考序列** - 开箱即用
- 📊 **美观的HTML结果页面** - 模仿NCBI BLAST结果界面
- 📦 **批量处理功能** - 支持批量上传.seq文件并生成CSV摘要
- 🚀 **统一数据库优化** - 快速比对所有物种
- 💻 **简洁的Web界面** - 易于使用的图形界面

## 📦 Windows用户快速开始

### 方法一：下载源码（推荐）

1. 点击右侧 **"Source code (zip)"** 下载完整源码
2. 解压到任意文件夹
3. 按照 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) 中的说明安装

### 方法二：使用Git克隆

```bash
git clone https://github.com/Bupoo123/LocalBlast.git
cd LocalBlast
```

## 🚀 快速安装（Windows）

1. **安装Python 3.7+**
   - 下载：https://www.python.org/downloads/
   - **重要**：安装时勾选 "Add Python to PATH"

2. **安装BLAST+**
   - 下载：https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
   - 下载Windows版本（如：`ncbi-blast-*-win64.exe`）
   - **重要**：安装时选择 "Add to PATH"

3. **安装依赖**
   - 双击运行 `install_windows.bat`
   - 或手动运行：`pip install -r requirements.txt`

4. **启动程序**
   - 双击运行 `start_windows.bat`
   - 在浏览器中访问 http://localhost:5001

## 📋 详细安装说明

- **Windows用户**：请查看 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- **macOS/Linux用户**：请查看 [README.md](README.md)

## 🆕 新功能

### v1.0.0 新增

- ✅ Windows一键安装脚本（`install_windows.bat`）
- ✅ Windows一键启动脚本（`start_windows.bat`）
- ✅ 批量处理功能（支持多文件上传）
- ✅ CSV摘要报告生成
- ✅ 统一数据库优化（提升比对速度）
- ✅ 完整的用户手册页面
- ✅ 详细的Windows安装文档

## 📝 使用说明

### 单序列比对

1. 访问 http://localhost:5001
2. 输入或粘贴查询序列
3. 选择要比对的物种（或留空比对所有物种）
4. 点击"执行BLAST比对"
5. 查看结果

### 批量处理

1. 点击"批量上传"链接
2. 选择多个.seq文件
3. 等待处理完成
4. 下载包含HTML结果和CSV摘要的ZIP文件

## 🔧 系统要求

- Python 3.7+
- BLAST+ 工具
- 至少 500MB 可用磁盘空间

## 📚 文档

- [README.md](README.md) - 项目说明和API文档
- [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) - Windows详细安装指南
- [分发说明.md](分发说明.md) - 打包分发指南

## 🐛 已知问题

- 首次运行需要创建BLAST数据库，可能需要一些时间
- Windows用户需要确保Python和BLAST+已添加到系统PATH

## 🙏 致谢

感谢所有使用和反馈的用户！

## 📄 许可证

本项目仅供学习和研究使用。

---

**下载地址**：点击右侧 "Source code (zip)" 下载完整源码包

