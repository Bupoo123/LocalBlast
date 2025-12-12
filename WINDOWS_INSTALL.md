# LocalBlast Windows 安装指南

本指南将帮助您在Windows系统上安装和运行LocalBlast工具。

## 📋 系统要求

- Windows 7 或更高版本（推荐 Windows 10/11）
- 至少 500MB 可用磁盘空间
- 网络连接（用于下载依赖）

## 🚀 快速安装（推荐）

### 方法一：自动安装（最简单）

1. **下载项目文件**
   - 从GitHub下载整个项目文件夹
   - 或使用Git克隆：`git clone https://github.com/Bupoo123/LocalBlast.git`

2. **运行安装脚本**
   - 双击运行 `install_windows.bat`
   - 脚本会自动检查并安装所需组件
   - 按照提示完成安装
   - 如果使用 Python 3.8、3.9、3.10 或 3.11 以外的版本，Pillow 可能安装失败，建议优先使用上述版本

3. **启动程序**
   - 打开命令提示符（CMD），切换到项目目录
     ```cmd
     cd /d C:\path\to\LocalBlast
     python blast_app.py
     ```
   - 等待服务启动（会显示"服务地址: http://localhost:5001"）
   - 在浏览器中打开 http://localhost:5001

### 方法二：手动安装

如果自动安装遇到问题，可以按照以下步骤手动安装：

#### 步骤1：安装Python

1. 访问 https://www.python.org/downloads/
2. 下载Python 3.7或更高版本（推荐Python 3.9+）
3. **重要**：安装时务必勾选 **"Add Python to PATH"**
4. 点击"Install Now"完成安装
5. 验证安装：打开命令提示符（CMD），输入 `python --version`，应该显示Python版本

#### 步骤2：安装BLAST+

1. 访问NCBI BLAST+下载页面：
   https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

2. 下载Windows版本（例如：`ncbi-blast-*-win64.exe`）

3. 运行安装程序：
   - **重要**：安装时选择 **"Add to PATH"** 选项
   - 或者记住安装路径（通常是 `C:\Program Files\NCBI\blast-*\bin`）

4. 验证安装：
   - 打开新的命令提示符窗口
   - 输入 `blastn -version`
   - 如果显示版本信息，说明安装成功

   **如果提示"不是内部或外部命令"**：
   - 需要手动添加BLAST+到PATH：
     1. 右键"此电脑" → "属性" → "高级系统设置"
     2. 点击"环境变量"
     3. 在"系统变量"中找到"Path"，点击"编辑"
     4. 点击"新建"，添加BLAST+的bin目录路径（例如：`C:\Program Files\NCBI\blast-2.14.0+\bin`）
     5. 点击"确定"保存
     6. **重新打开命令提示符**，再次验证

#### 步骤3：安装Python依赖

1. 打开命令提示符（CMD）
2. 切换到项目目录：
   ```cmd
   cd /d C:\path\to\LocalBlast
   ```
3. 安装依赖：
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

#### 步骤4：启动程序

1. 打开命令提示符，切换到项目目录（避免直接双击 `start_windows.bat`）
   ```cmd
   cd /d C:\path\to\LocalBlast
   ```
2. 启动服务：
   ```cmd
   python blast_app.py
   ```
3. 在浏览器中访问：http://localhost:5001

## 🔧 常见问题

### 问题1：提示"Python未找到"

**解决方案：**
- 确保Python已安装
- 检查是否在安装时勾选了"Add Python to PATH"
- 如果没有，需要手动添加到PATH（方法同BLAST+）
- 或者重新安装Python，这次记得勾选"Add Python to PATH"

### 问题2：提示"BLAST+未安装"

**解决方案：**
- 确保BLAST+已安装
- 检查BLAST+是否在系统PATH中
- 打开新的命令提示符，输入 `blastn -version` 验证
- 如果不在PATH中，按照步骤2的方法手动添加

### 问题3：端口5001被占用

**解决方案：**
- 修改 `blast_app.py` 文件，找到最后几行的端口设置
- 将 `app.run(port=5001)` 改为其他端口（如5002）
- 重新启动程序

### 问题4：依赖安装失败

**解决方案：**
- 确保网络连接正常
- 尝试使用国内镜像源：
  ```cmd
  python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- 如果某个包安装失败，可以单独安装：
  ```cmd
  python -m pip install 包名
  ```

### 问题5：双击.bat文件后窗口立即关闭

**解决方案：**
- 右键点击.bat文件 → "编辑"
- 在文件末尾添加 `pause`
- 保存后重新运行
- 或者使用命令提示符运行，这样可以看到错误信息

## 📦 打包分发

如果您想将程序打包给其他同事使用，可以：

1. **方法一：直接分发文件夹**
   - 将整个项目文件夹压缩
   - 确保包含所有文件（特别是 `species_db.json` 和 `templates` 文件夹）
   - 同事解压后，按照上述步骤安装Python和BLAST+
   - 运行 `install_windows.bat` 和 `start_windows.bat`

2. **方法二：创建便携版（需要Windows环境）**
   - 使用PyInstaller打包（需要Windows系统）：
     ```cmd
     pip install pyinstaller
     pyinstaller --onefile --windowed --name LocalBlast blast_app.py
     ```
   - 注意：BLAST+仍需要单独安装

## 📝 使用说明

1. **启动程序**：在命令提示符中切换到项目目录并运行 `python blast_app.py`
2. **打开浏览器**：访问 http://localhost:5001
3. **单序列比对**：
   - 在"序列输入"页面输入或粘贴序列
   - 选择要比对的物种（或留空比对所有物种）
   - 点击"执行BLAST比对"
4. **批量处理**：
   - 点击"批量上传"链接
   - 选择多个.seq文件
   - 等待处理完成
   - 下载结果ZIP文件

## 🆘 获取帮助

如果遇到问题：
1. 查看控制台输出的错误信息
2. 检查Python和BLAST+是否正确安装
3. 查看项目GitHub页面的Issues
4. 联系项目维护者

## 📄 许可证

本项目仅供学习和研究使用。

