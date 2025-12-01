# LocalBlast v1.1.0 发布说明

## 🎉 样式优化版本

LocalBlast v1.1.0 主要优化了BLAST结果页面的样式和布局，使界面更加美观和易用。

## ✨ 主要更新

### 界面优化

- 🎨 **页面宽度调整** - 将页面最大宽度从1400px优化为1100px，更符合阅读习惯
- 📊 **摘要表格优化** - 摘要表格宽度缩小为50%，只占据左侧，布局更紧凑
- 🏷️ **标签页样式** - 标签页从圆角改为直角，更简洁现代
- 📏 **表格样式优化** - 优化表格边框、对齐方式和分隔线样式
- 🎯 **对齐方式** - 所有表格内容居中显示，表头字体改为regular

### 细节改进

- ✅ Subject Descr 始终显示 "None"
- ✅ Graphics 和 MSA Viewer 按钮移到 "select all" 行右侧
- ✅ Download 和 Select columns 字体加粗显示
- ✅ 表头三角形符号移到下一行，checkbox列不显示三角形
- ✅ 移除标签页和表格之间的白色细线
- ✅ 表格顶部添加3px蓝色边框，与Descriptions标签背景色一致

## 📦 下载

### 方法一：下载源码（推荐）

1. 点击右侧 **"Source code (zip)"** 下载完整源码
2. 解压到任意文件夹
3. 按照 [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) 中的说明安装

### 方法二：使用Git克隆

```bash
git clone https://github.com/Bupoo123/LocalBlast.git
cd LocalBlast
git checkout v1.1.0
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

## 🔄 从 v1.0.0 升级

如果您已经安装了 v1.0.0，只需：

1. 下载新版本源码或使用 `git pull` 更新
2. 重新运行 `install_windows.bat`（如果需要更新依赖）
3. 重启程序即可

## 📝 使用说明

### 单序列比对

1. 访问 http://localhost:5001
2. 输入或粘贴查询序列
3. 选择要比对的物种（或留空比对所有物种）
4. 点击"执行BLAST比对"
5. 查看优化后的结果页面

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

