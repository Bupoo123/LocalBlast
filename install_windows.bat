@echo off
chcp 65001 >nul
echo ==========================================
echo LocalBlast Windows 安装脚本
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [√] 检测到管理员权限
) else (
    echo [!] 警告: 未检测到管理员权限，某些操作可能需要管理员权限
)
echo.

REM 检查Python是否安装
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorLevel% == 0 (
    python --version
    echo [√] Python已安装
) else (
    echo [×] 未找到Python
    echo.
    echo 请先安装Python 3.7或更高版本：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python（安装时勾选"Add Python to PATH"）
    echo 3. 安装完成后重新运行此脚本
    pause
    exit /b 1
)
echo.

REM 检查pip
echo [2/4] 检查pip...
python -m pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [√] pip已安装
) else (
    echo [×] pip未找到，正在安装...
    python -m ensurepip --upgrade
)
echo.

REM 安装Python依赖
echo [3/4] 安装Python依赖包...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorLevel% == 0 (
    echo [√] Python依赖安装完成
) else (
    echo [×] Python依赖安装失败
    pause
    exit /b 1
)
echo.

REM 检查BLAST+
echo [4/4] 检查BLAST+工具...
where blastn >nul 2>&1
if %errorLevel% == 0 (
    blastn -version
    echo [√] BLAST+已安装
) else (
    echo [!] 未找到BLAST+工具
    echo.
    echo 请安装BLAST+工具：
    echo 1. 访问 https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
    echo 2. 下载适合Windows的安装包（例如：ncbi-blast-*-win64.exe）
    echo 3. 运行安装程序，安装时选择"Add to PATH"
    echo 4. 安装完成后重新运行此脚本验证
    echo.
    echo 或者，如果您已经安装了BLAST+但未添加到PATH，请手动添加BLAST+的bin目录到系统PATH
    echo.
    set /p continue="是否继续？(Y/N): "
    if /i not "%continue%"=="Y" (
        exit /b 1
    )
)
echo.

echo ==========================================
echo 安装完成！
echo ==========================================
echo.
echo 使用方法：
echo 1. 双击运行 start_windows.bat 启动程序
echo 2. 在浏览器中访问 http://localhost:5001
echo.
pause

