@echo off
chcp 65001 >nul
echo ========================================
echo 启动后端服务...
echo ========================================
cd backend

REM 检查虚拟环境是否存在
if not exist venv (
    echo 创建虚拟环境...
    py -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败，请确保已安装Python
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖是否已安装
if not exist venv\Scripts\fastapi.exe (
    echo 安装依赖包...
    py -m pip install --upgrade pip
    if errorlevel 1 (
        echo 错误: pip升级失败
        pause
        exit /b 1
    )
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo 依赖已安装，跳过...
)

echo.
echo 启动服务器...
echo 后端地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

py main.py

pause

