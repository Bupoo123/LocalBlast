@echo off
chcp 65001 >nul
echo ==========================================
echo LocalBlast Windows 可执行文件打包脚本
echo ==========================================
echo.
echo 此脚本将使用PyInstaller打包Python应用为exe文件
echo.

REM 检查Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [1/4] 检查PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在安装PyInstaller...
    python -m pip install pyinstaller
    if %errorLevel% neq 0 (
        echo [错误] PyInstaller安装失败
        pause
        exit /b 1
    )
)

echo [2/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist blast_app.spec del /q blast_app.spec

echo [2.5/4] 下载ChromeDriver（可选）...
if not exist drivers mkdir drivers
python -c "try:
    from webdriver_manager.chrome import ChromeDriverManager
    import os, shutil, glob
    path = ChromeDriverManager().install()
    # 修复路径问题
    if 'THIRD_PARTY_NOTICES' in path:
        dir_path = os.path.dirname(path)
        actual_path = os.path.join(dir_path, 'chromedriver.exe')
        if os.path.exists(actual_path):
            path = actual_path
        else:
            # 在.wdm目录中查找
            wdm_base = os.path.expanduser('~/.wdm')
            if os.path.exists(wdm_base):
                drivers = glob.glob(os.path.join(wdm_base, '**/chromedriver.exe'), recursive=True)
                if drivers:
                    path = drivers[0]
    if os.path.exists(path):
        shutil.copy(path, 'drivers\\chromedriver.exe')
        print('ChromeDriver已下载')
except Exception as e:
    print(f'ChromeDriver下载失败: {e}')" 2>nul
if exist drivers\chromedriver.exe (
    echo [√] ChromeDriver已下载
) else (
    echo [!] ChromeDriver下载失败，PNG功能将尝试在线下载
)

echo [3/4] 使用PyInstaller打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

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
    --icon=NONE ^
    blast_app.py

if %errorLevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/4] 创建安装包...
set PACKAGE_NAME=LocalBlast_Windows_Installer
set PACKAGE_DIR=%PACKAGE_NAME%_%date:~0,4%%date:~5,2%%date:~8,2%

if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%

REM 复制exe文件
copy dist\LocalBlast.exe %PACKAGE_DIR%\ >nul

REM 复制必要文件
copy species_db.json %PACKAGE_DIR%\ >nul
xcopy /E /I /Y templates %PACKAGE_DIR%\templates >nul

REM 复制ChromeDriver（如果存在）
if exist drivers\chromedriver.exe (
    copy drivers\chromedriver.exe %PACKAGE_DIR%\ >nul
    echo [√] 已包含ChromeDriver
) else (
    echo [!] ChromeDriver未找到，PNG功能可能需要网络连接
)

REM 创建一键安装脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo title LocalBlast - 一键安装
echo.
echo ==========================================
echo LocalBlast - 一键安装程序
echo ==========================================
echo.
echo 此脚本将自动检查并安装所需环境
echo.
echo [1/3] 检查Python环境...
echo.
python --version ^>nul 2^>^&1
if %%errorLevel%% neq 0 (
    echo [×] 未找到Python
    echo.
    echo 请先安装Python 3.7或更高版本：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python（安装时勾选"Add Python to PATH"）
    echo 3. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)
python --version
echo [√] Python已安装
echo.
echo [2/3] 检查BLAST+工具...
echo.
where blastn ^>nul 2^>^&1
if %%errorLevel%% neq 0 (
    echo [×] 未找到BLAST+工具
    echo.
    echo 请安装BLAST+工具：
    echo 1. 访问 https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
    echo 2. 下载Windows版本（如：ncbi-blast-*-win64.exe）
    echo 3. 运行安装程序，安装时选择"Add to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)
blastn -version
echo [√] BLAST+已安装
echo.
echo [3/3] 环境检查完成！
echo.
echo ==========================================
echo 安装完成！
echo ==========================================
echo.
echo 现在可以：
echo 1. 双击运行 "启动LocalBlast.bat" 启动程序
echo 2. 在浏览器中访问 http://localhost:5001
echo.
pause
) > %PACKAGE_DIR%\一键安装.bat

REM 创建启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo title LocalBlast - 本地BLAST工具
echo.
echo ==========================================
echo LocalBlast - 本地BLAST工具
echo ==========================================
echo.
echo 正在启动服务...
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
LocalBlast.exe
pause
) > %PACKAGE_DIR%\启动LocalBlast.bat

REM 创建说明文件
(
echo LocalBlast Windows 可执行文件安装包
echo.
echo ==========================================
echo 快速开始
echo ==========================================
echo.
echo 1. 双击运行 "一键安装.bat" 检查环境
echo 2. 双击运行 "启动LocalBlast.bat" 启动程序
echo 3. 在浏览器中访问 http://localhost:5001
echo.
echo ==========================================
echo 系统要求
echo ==========================================
echo.
echo 1. Python 3.7+ （从 https://www.python.org/downloads/ 下载）
echo 2. BLAST+工具 （从 https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ 下载）
echo.
echo ==========================================
echo 文件说明
echo ==========================================
echo.
echo - LocalBlast.exe: 主程序（已包含所有Python依赖）
echo - 一键安装.bat: 环境检查脚本
echo - 启动LocalBlast.bat: 启动程序脚本
echo - species_db.json: 参比序列数据库
echo - templates/: HTML模板文件夹
echo.
echo ==========================================
echo 注意事项
echo ==========================================
echo.
echo 1. 首次使用前请先运行"一键安装.bat"检查环境
echo 2. BLAST+工具需要单独安装（无法打包到exe中）
echo 3. 如果遇到问题，请查看错误提示或联系技术支持
echo.
) > %PACKAGE_DIR%\使用说明.txt

echo.
echo [√] 打包完成！
echo.
echo 打包目录: %PACKAGE_DIR%
echo.
echo 下一步：
echo 1. 将 %PACKAGE_DIR% 文件夹压缩成ZIP
echo 2. 分发给同事
echo 3. 提醒同事先运行"一键安装.bat"检查环境
echo.
pause
