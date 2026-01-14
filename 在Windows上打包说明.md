# 在Windows系统上打包LocalBlast可执行文件

## 📋 前提条件

1. **Windows系统**（必须在Windows上打包，macOS无法打包Windows exe）
2. **Python 3.7+** 已安装
3. **Git**（可选，用于克隆代码）

## 🚀 快速打包步骤

### 方法一：从GitHub下载代码后打包（推荐）

1. **下载代码**
   - 访问：https://github.com/Bupoo123/LocalBlast
   - 点击 "Code" → "Download ZIP"
   - 解压到任意文件夹（如：`C:\LocalBlast`）

2. **打开命令提示符**
   - 按 `Win + R`，输入 `cmd`，回车
   - 切换到代码目录：
     ```cmd
     cd C:\LocalBlast
     ```

3. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. **运行打包脚本**
   ```cmd
   build_windows_exe.bat
   ```

5. **等待打包完成**
   - 打包过程可能需要5-10分钟
   - 完成后会生成 `LocalBlast_Windows_Installer_YYYYMMDD` 文件夹

6. **压缩分发**
   - 将生成的文件夹压缩成ZIP
   - 文件名建议：`LocalBlast_Windows_v1.0_Installer.zip`

### 方法二：手动打包

如果脚本无法运行，可以手动执行：

```cmd
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 打包应用
pyinstaller --onefile ^
    --name LocalBlast ^
    --add-data "templates;templates" ^
    --add-data "species_db.json;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=werkzeug ^
    --hidden-import=PIL ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --console ^
    blast_app.py

# 3. 创建安装包目录
mkdir LocalBlast_Windows_Installer
copy dist\LocalBlast.exe LocalBlast_Windows_Installer\
copy species_db.json LocalBlast_Windows_Installer\
xcopy /E /I /Y templates LocalBlast_Windows_Installer\templates

# 4. 复制一键安装和启动脚本（从代码中复制）
```

## 📦 打包后的文件

打包完成后，`LocalBlast_Windows_Installer_YYYYMMDD` 文件夹包含：

- `LocalBlast.exe` - 主程序（包含所有Python依赖）
- `一键安装.bat` - 环境检查脚本
- `启动LocalBlast.bat` - 启动程序脚本
- `使用说明.txt` - 使用说明
- `species_db.json` - 参比序列数据库
- `templates/` - HTML模板文件夹

## ⚠️ 注意事项

1. **必须在Windows系统上打包**
   - macOS无法打包Windows exe文件
   - 如果只有macOS，可以：
     - 使用Windows虚拟机
     - 使用GitHub Actions自动打包（见下方）

2. **打包时间**
   - 首次打包可能需要10-15分钟
   - 后续打包会快一些（5-10分钟）

3. **文件大小**
   - exe文件大约50-100MB（包含所有依赖）
   - 完整安装包大约100-150MB

## 🔧 故障排除

### 问题1：PyInstaller安装失败

**解决方案：**
```cmd
pip install --upgrade pip
pip install pyinstaller
```

### 问题2：打包时提示缺少模块

**解决方案：**
```cmd
pip install -r requirements.txt
```

### 问题3：exe文件无法运行

**可能原因：**
- 被杀毒软件拦截
- 缺少系统库

**解决方案：**
- 将exe添加到杀毒软件白名单
- 确保Windows系统已更新

## 🎯 使用GitHub Actions自动打包（可选）

如果想自动化打包，可以设置GitHub Actions：

1. 代码已包含 `.github/workflows/create-windows-release.yml`
2. 在GitHub上创建Release时会自动打包
3. 或者手动触发workflow

## 📝 分发给同事

打包完成后：

1. 将 `LocalBlast_Windows_Installer_YYYYMMDD` 文件夹压缩成ZIP
2. 文件名：`LocalBlast_Windows_v1.0_Installer.zip`
3. 同时提供 `分发指南_可执行文件版.md` 作为安装说明
4. 分发给同事

## ✅ 验证打包

打包完成后，建议：

1. 在干净的Windows系统上测试
2. 确保exe可以正常运行
3. 确保所有功能正常
