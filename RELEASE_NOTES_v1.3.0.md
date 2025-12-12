# LocalBlast v1.3.0 发布说明

## 🎉 兼容性和文档优化版本

LocalBlast v1.3.0 主要优化了Windows安装指南和兼容性说明，提供了更清晰的安装步骤和Python版本兼容性指导。

## ✨ 主要更新

### 兼容性说明

- 🐍 **Python版本兼容性** - 明确说明Pillow建议使用Python 3.8-3.11版本，避免兼容性问题
- 📦 **依赖安装优化** - 更新了依赖安装说明，特别强调了Pillow的版本兼容性

### 文档优化

- 📖 **Windows安装指南优化** - 详细说明了使用命令提示符启动程序的方法
- 🔧 **启动方式改进** - 推荐使用CMD命令提示符启动，而不是直接双击bat文件
- 💡 **命令修正** - 修正了Windows下的cd命令，添加了`/d`参数以支持跨驱动器切换

### 界面一致性

- 🎨 **描述信息统一** - Description列统一显示为"None provided"，保持界面一致性

## 📦 下载

### 方法一：下载源码（推荐）

1. 点击右侧 **"Source code (zip)"** 下载完整源码
2. 解压到任意文件夹
3. 按照 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) 中的说明安装

### 方法二：使用Git克隆

```bash
git clone https://github.com/Bupoo123/LocalBlast.git
cd LocalBlast
git checkout codex/update-installation-instructions-and-compatibility-notes
```

## 🚀 快速安装（Windows）

### ⚠️ 重要提示：Python版本兼容性

**推荐使用 Python 3.8、3.9、3.10 或 3.11**

如果使用其他版本，Pillow可能安装失败。建议优先使用上述版本以避免兼容性问题。

### 安装步骤

1. **安装Python 3.8-3.11**
   - 下载：https://www.python.org/downloads/
   - **重要**：安装时勾选 "Add Python to PATH"
   - 推荐版本：Python 3.8、3.9、3.10 或 3.11

2. **安装BLAST+**
   - 下载：https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
   - 下载Windows版本（如：`ncbi-blast-*-win64.exe`）
   - **重要**：安装时选择 "Add to PATH"

3. **安装依赖**
   - 双击运行 `install_windows.bat`
   - 或手动运行：`pip install -r requirements.txt`

4. **启动程序**
   - **推荐方式**：打开命令提示符（CMD），切换到项目目录：
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
2. 检查Python版本是否符合要求（推荐3.8-3.11）
3. 重新运行 `install_windows.bat`（如果需要更新依赖）
4. 使用CMD命令提示符启动程序

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

## ⚠️ 常见问题

### Pillow安装失败

**问题**：安装依赖时Pillow安装失败

**解决方案**：
- 确保使用Python 3.8、3.9、3.10或3.11版本
- 如果使用其他版本，建议卸载并安装推荐的Python版本
- 重新运行 `install_windows.bat`

### 启动问题

**问题**：双击bat文件无法启动

**解决方案**：
- 使用命令提示符（CMD）启动程序
- 切换到项目目录：`cd /d C:\path\to\LocalBlast`
- 运行：`python blast_app.py`

### 路径问题

**问题**：cd命令无法切换到项目目录

**解决方案**：
- 使用 `cd /d` 命令以支持跨驱动器切换
- 例如：`cd /d D:\LocalBlast`

## 🔧 系统要求

- **Python**：3.8、3.9、3.10 或 3.11（推荐）
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

**分支信息**：本版本基于 `codex/update-installation-instructions-and-compatibility-notes` 分支

**版本历史**：
- v1.0.0 - 初始版本
- v1.1.0 - 样式优化版本
- v1.2.0 - 功能增强版本（新增Common Name和Taxid列）
- **v1.3.0** - 兼容性和文档优化版本（当前版本）

