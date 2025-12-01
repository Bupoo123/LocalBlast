@echo off
chcp 65001 >nul
echo ==========================================
echo LocalBlast Windows 打包脚本
echo ==========================================
echo.
echo 此脚本将创建一个可分发的Windows包
echo.

REM 设置打包目录名
set PACKAGE_NAME=LocalBlast_Windows
set PACKAGE_DIR=%PACKAGE_NAME%_%date:~0,4%%date:~5,2%%date:~8,2%

echo 正在创建打包目录: %PACKAGE_DIR%
if exist %PACKAGE_DIR% (
    echo 目录已存在，正在删除...
    rmdir /s /q %PACKAGE_DIR%
)
mkdir %PACKAGE_DIR%

echo.
echo 正在复制文件...

REM 复制核心文件
copy blast_app.py %PACKAGE_DIR%\ >nul
copy species_db.json %PACKAGE_DIR%\ >nul
copy requirements.txt %PACKAGE_DIR%\ >nul
copy README.md %PACKAGE_DIR%\ >nul

REM 复制Windows脚本
copy install_windows.bat %PACKAGE_DIR%\ >nul
copy start_windows.bat %PACKAGE_DIR%\ >nul
copy WINDOWS_INSTALL.md %PACKAGE_DIR%\ >nul

REM 复制模板文件夹
xcopy /E /I /Y templates %PACKAGE_DIR%\templates >nul

REM 复制示例文件（可选）
if exist inputexample (
    xcopy /E /I /Y inputexample %PACKAGE_DIR%\inputexample >nul
)

echo [√] 文件复制完成

REM 创建说明文件
echo 正在创建安装说明...
(
echo LocalBlast Windows 安装包
echo.
echo 安装步骤：
echo 1. 确保已安装Python 3.7+（从 https://www.python.org/downloads/ 下载）
echo 2. 确保已安装BLAST+（从 https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ 下载）
echo 3. 双击运行 install_windows.bat 安装依赖
echo 4. 双击运行 start_windows.bat 启动程序
echo 5. 在浏览器中访问 http://localhost:5001
echo.
echo 详细说明请查看 WINDOWS_INSTALL.md
) > %PACKAGE_DIR%\安装说明.txt

echo [√] 打包完成！
echo.
echo 打包目录: %PACKAGE_DIR%
echo.
echo 下一步：
echo 1. 将 %PACKAGE_DIR% 文件夹压缩成ZIP
echo 2. 分发给同事
echo 3. 提醒同事先安装Python和BLAST+，然后运行install_windows.bat
echo.
pause

