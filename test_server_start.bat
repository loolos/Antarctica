@echo off
chcp 65001 >nul
echo ========================================
echo 测试后端服务器启动
echo ========================================
echo.

cd /d %~dp0

REM 检查虚拟环境
if not exist "backend\venv\Scripts\python.exe" (
    echo ❌ 虚拟环境不存在，请先运行 start_backend.bat
    pause
    exit /b 1
)

echo ✅ 虚拟环境存在
echo.

REM 测试导入
echo 测试模块导入...
backend\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); from simulation.engine import SimulationEngine; print('✅ simulation模块导入成功')"
if errorlevel 1 (
    echo ❌ simulation模块导入失败
    pause
    exit /b 1
)

backend\venv\Scripts\python.exe -c "import fastapi; import uvicorn; print('✅ FastAPI依赖已安装')"
if errorlevel 1 (
    echo ❌ FastAPI依赖未安装
    echo 正在安装...
    backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
)

echo.
echo ========================================
echo ✅ 所有检查通过！
echo ========================================
echo.
echo 正在启动服务器...
echo 服务器地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

cd backend
..\backend\venv\Scripts\python.exe main.py

pause

