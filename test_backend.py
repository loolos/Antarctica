"""
测试后端服务器启动
"""
import sys
import os
import io
import subprocess
import time
import urllib.request
import json

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_backend():
    """测试后端服务器"""
    print("="*60)
    print("测试后端服务器")
    print("="*60)
    
    # 检查backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ backend目录不存在")
        return False
    
    # 检查main.py
    main_py = os.path.join(backend_dir, 'main.py')
    if not os.path.exists(main_py):
        print("❌ main.py不存在")
        return False
    
    print("✅ 文件检查通过")
    
    # 检查依赖
    print("\n检查Python模块...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from simulation.engine import SimulationEngine
        print("✅ simulation模块导入成功")
    except Exception as e:
        print(f"❌ simulation模块导入失败: {e}")
        return False
    
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI和Uvicorn已安装")
    except ImportError as e:
        print(f"❌ 依赖未安装: {e}")
        print("   请运行: cd backend && py -m pip install -r requirements.txt")
        return False
    
    # 尝试导入main
    print("\n测试导入main.py...")
    try:
        sys.path.insert(0, backend_dir)
        import main
        print("✅ main.py导入成功")
        print(f"   FastAPI应用: {main.app.title}")
    except Exception as e:
        print(f"❌ main.py导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ 后端服务器配置检查通过！")
    print("="*60)
    print("\n启动说明:")
    print("1. 打开终端，进入backend目录")
    print("2. 运行: py main.py")
    print("3. 或双击运行: start_backend.bat")
    print("\n服务器将在 http://localhost:8000 启动")
    print("API文档: http://localhost:8000/docs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)

