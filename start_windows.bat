@echo off
chcp 65001 >nul
title LocalBlast - 本地BLAST工具

echo ==========================================
echo LocalBlast - 本地BLAST工具
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python，请先运行 install_windows.bat 安装
    pause
    exit /b 1
)

REM 检查BLAST+
where blastn >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] 未找到BLAST+工具
    echo 请确保BLAST+已安装并添加到系统PATH
    echo 按任意键继续（如果BLAST+已安装但未在PATH中，程序可能无法正常工作）
    pause >nul
)

REM 检查依赖
python -c "import flask" >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] Python依赖未安装，正在安装...
    python -m pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo [错误] 依赖安装失败，请运行 install_windows.bat
        pause
        exit /b 1
    )
)

echo [√] 环境检查完成
echo.
echo ==========================================
echo 正在启动BLAST服务...
echo ==========================================
echo.
echo 服务地址: http://localhost:5001
echo.
echo 提示：
echo - 保持此窗口打开以运行服务
echo - 关闭此窗口将停止服务
echo - 按 Ctrl+C 也可以停止服务
echo.
echo ==========================================
echo.

REM 启动Flask应用
python blast_app.py

pause






