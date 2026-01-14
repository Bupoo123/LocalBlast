# 使用GitHub Actions自动打包Windows可执行文件

## 🎯 说明

由于PyInstaller不支持跨平台打包，无法在macOS上直接打包Windows exe文件。但可以使用GitHub Actions在云端自动打包！

## 🚀 使用方法

### 方法一：手动触发（推荐）

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "准备打包Windows exe"
   git push origin main
   ```

2. **在GitHub上触发workflow**
   - 访问：https://github.com/Bupoo123/LocalBlast/actions
   - 点击左侧 "Build Windows Executable"
   - 点击右侧 "Run workflow" 按钮
   - 选择分支（通常是 `main`）
   - 点击 "Run workflow"

3. **等待打包完成**
   - 打包过程大约需要5-10分钟
   - 可以在Actions页面查看进度

4. **下载打包结果**
   - 打包完成后，在Actions页面找到对应的workflow运行
   - 点击进入详情页
   - 在 "Artifacts" 部分下载 `LocalBlast-Windows-Installer.zip`

### 方法二：通过Tag自动触发

1. **创建并推送tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动打包**
   - GitHub会自动触发打包
   - 打包完成后会自动创建Release
   - 可以在Releases页面下载

## 📦 打包结果

打包完成后会生成：
- `LocalBlast_Windows_Installer_YYYYMMDD.zip`
- 包含所有必要文件：
  - `LocalBlast.exe` - 主程序（包含所有Python依赖）
  - `一键安装.bat` - 环境检查脚本
  - `启动LocalBlast.bat` - 启动程序脚本
  - `使用说明.txt` - 使用说明
  - `species_db.json` - 参比序列数据库
  - `templates/` - HTML模板文件夹

## ✅ 优势

- ✅ **不需要Windows系统** - 在macOS上就可以操作
- ✅ **自动化** - 一键触发，自动打包
- ✅ **云端执行** - 使用GitHub的Windows runner
- ✅ **可重复** - 随时可以重新打包

## 📝 分发给同事

1. **下载打包结果**
   - 从GitHub Actions下载ZIP文件

2. **分发给同事**
   - 直接发送ZIP文件
   - 或上传到网盘/文件服务器

3. **提供安装说明**
   - 同时发送 `分发指南_可执行文件版.md`
   - 或让同事查看ZIP中的 `使用说明.txt`

## 🔧 故障排除

### 问题1：找不到workflow

**解决方案：**
- 确保 `.github/workflows/build-windows-exe.yml` 文件已提交到GitHub
- 刷新GitHub页面

### 问题2：打包失败

**可能原因：**
- 代码有错误
- 依赖安装失败

**解决方案：**
- 查看Actions页面的错误日志
- 检查代码是否有语法错误
- 确保requirements.txt中的依赖都是有效的

### 问题3：下载的ZIP文件损坏

**解决方案：**
- 重新触发workflow打包
- 或使用其他方法下载

## 🎉 快速开始

1. **推送代码**
   ```bash
   git push origin main
   ```

2. **在GitHub上触发workflow**
   - 访问 Actions 页面
   - 点击 "Run workflow"

3. **等待并下载**
   - 等待5-10分钟
   - 下载打包结果

就这么简单！
