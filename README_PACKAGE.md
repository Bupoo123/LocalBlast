# LocalBlast Windows 可执行文件打包指南

本指南帮助您将LocalBlast打包成Windows可执行文件（.exe），方便分发给同事使用。

## 📦 打包步骤

### 前提条件

1. **Windows系统**（必须在Windows上打包）
2. **Python 3.7+** 已安装
3. **所有依赖已安装**（运行过 `pip install -r requirements.txt`）

### 打包方法

#### 方法一：使用打包脚本（推荐）

1. **运行打包脚本**
   ```cmd
   build_windows_exe.bat
   ```

2. **等待打包完成**
   - 脚本会自动安装PyInstaller（如果未安装）
   - 打包过程可能需要5-10分钟
   - 完成后会生成 `LocalBlast_Windows_Installer_YYYYMMDD` 文件夹

3. **压缩分发**
   - 将生成的文件夹压缩成ZIP
   - 文件名建议：`LocalBlast_Windows_v1.0.zip`

#### 方法二：手动打包

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

# 3. 复制文件到打包目录
# - dist\LocalBlast.exe
# - species_db.json
# - templates\ 文件夹
```

## 📋 打包后的文件结构

```
LocalBlast_Windows_Installer_YYYYMMDD/
├── LocalBlast.exe          # 主程序（包含所有Python依赖）
├── 一键安装.bat            # 环境检查脚本
├── 启动LocalBlast.bat      # 启动程序脚本
├── 使用说明.txt            # 使用说明
├── species_db.json         # 参比序列数据库
└── templates/              # HTML模板文件夹
    ├── batch_blast.html
    ├── blast_input.html
    ├── user_manual.html
    └── sequence_template.seq
```

## 🎯 给同事的安装说明

### 系统要求

1. **Windows 7 或更高版本**（推荐 Windows 10/11）
2. **Python 3.7+**（如果使用exe版本，Python是可选的，但BLAST+需要）
3. **BLAST+工具**（必须安装）

### 安装步骤

1. **解压文件**
   - 将ZIP文件解压到任意文件夹（如：`C:\LocalBlast`）

2. **运行一键安装脚本**
   - 双击运行 `一键安装.bat`
   - 脚本会自动检查Python和BLAST+是否已安装
   - 如果缺少，会提示安装方法

3. **启动程序**
   - 双击运行 `启动LocalBlast.bat`
   - 等待看到 "服务地址: http://localhost:5001" 提示
   - 在浏览器中打开 http://localhost:5001

## ⚠️ 重要说明

### 关于BLAST+工具

- **BLAST+无法打包到exe中**，必须单独安装
- 下载地址：https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
- 安装时务必选择 "Add to PATH"

### 关于Python依赖

- **exe文件已包含所有Python依赖**（Flask、Pillow、selenium等）
- 同事**不需要**安装Python依赖
- 但**仍需要安装Python**（某些功能可能需要）

### 关于PNG生成功能

- PNG生成功能需要Chrome浏览器
- 如果系统没有Chrome，PNG生成会失败，但HTML文件仍会正常生成

## 🔧 故障排除

### 问题1：打包失败

**可能原因：**
- PyInstaller未正确安装
- 缺少某些依赖

**解决方案：**
```cmd
pip install --upgrade pyinstaller
pip install -r requirements.txt
```

### 问题2：exe文件无法运行

**可能原因：**
- 被杀毒软件拦截
- 缺少必要的系统库

**解决方案：**
- 将exe文件添加到杀毒软件白名单
- 确保Windows系统已更新

### 问题3：找不到BLAST+工具

**解决方案：**
- 确保BLAST+已安装并添加到PATH
- 打开新的命令提示符窗口测试：`blastn -version`

## 📝 分发建议

1. **创建安装包说明**
   - 包含系统要求
   - 包含安装步骤
   - 包含常见问题解答

2. **提供技术支持**
   - 提供联系方式
   - 准备常见问题解答

3. **测试安装包**
   - 在干净的Windows系统上测试
   - 确保所有功能正常

## 🎉 优势

使用exe打包的优势：
- ✅ 不需要安装Python依赖
- ✅ 一键启动，使用简单
- ✅ 包含所有必要的文件
- ✅ 适合IT基础较弱的用户

但仍需要：
- ⚠️ 安装BLAST+工具（无法打包）
- ⚠️ 可能需要安装Python（某些功能）
