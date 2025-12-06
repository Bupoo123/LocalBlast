# LocalBlast v1.2.0 发布说明

## 🎉 功能增强版本

LocalBlast v1.2.0 在 v1.1.0 的基础上，进一步增强了结果展示功能和Windows使用指南。

## ✨ 主要更新

### 功能增强

- 📊 **新增结果列** - 在BLAST结果表格中新增"Common Name"和"Taxid"列，提供更详细的物种信息
- 📝 **描述信息优化** - Description列统一显示为"None provided"，保持界面一致性
- 🔧 **Subject Descr优化** - Subject Descr字段显示为"None provided"，提供更清晰的提示信息

### 文档更新

- 📖 **Windows安装指南优化** - 更新了Windows使用指南，提供更详细的安装步骤和故障排除说明
- 💡 **使用说明改进** - 改进了README中的使用说明，使新用户更容易上手

### 界面改进

- 🎨 **表格列宽优化** - 为新增的Common Name和Taxid列设置了合适的列宽
- 📐 **布局调整** - 优化了表格布局，确保所有列都能正确显示

## 📦 下载

### 方法一：下载源码（推荐）

1. 点击右侧 **"Source code (zip)"** 下载完整源码
2. 解压到任意文件夹
3. 按照 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) 中的说明安装

### 方法二：使用Git克隆

```bash
git clone https://github.com/Bupoo123/LocalBlast.git
cd LocalBlast
git checkout codex/update-installation-instructions-and-html-output
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

## 🔄 从 v1.1.0 升级

如果您已经安装了 v1.1.0，只需：

1. 下载新版本源码或使用 `git pull` 更新
2. 重新运行 `install_windows.bat`（如果需要更新依赖）
3. 重启程序即可

## 📝 使用说明

### 单序列比对

1. 访问 http://localhost:5001
2. 输入或粘贴查询序列
3. 选择要比对的物种（或留空比对所有物种）
4. 点击"执行BLAST比对"
5. 查看结果，现在可以看到Common Name和Taxid信息

### 批量处理

1. 点击"批量上传"链接
2. 选择多个.seq文件
3. 等待处理完成
4. 下载包含HTML结果和CSV摘要的ZIP文件

## 🆕 新功能说明

### Common Name 和 Taxid 列

在BLAST结果表格中，现在会显示：
- **Common Name**：物种的通用名称
- **Taxid**：NCBI分类ID

这些信息有助于更准确地识别和分类比对结果。

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

**分支信息**：本版本基于 `codex/update-installation-instructions-and-html-output` 分支

