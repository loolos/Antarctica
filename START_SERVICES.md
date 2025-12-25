# 启动前后端服务

## 快速启动

### Windows 用户（最简单）

1. **启动后端**：
   - 双击运行 `scripts\start_backend.bat`
   - 等待看到 "Uvicorn running on http://0.0.0.0:8000"

2. **启动前端**（打开新窗口）：
   - 双击运行 `scripts\start_frontend.bat`
   - 等待看到 "Compiled successfully!"

3. **访问应用**：
   - 浏览器自动打开，或手动访问 `http://localhost:3000`

### Linux/Mac 用户

1. **启动后端**：
   ```bash
   chmod +x scripts/start_backend.sh
   ./scripts/start_backend.sh
   ```

2. **启动前端**（新终端）：
   ```bash
   chmod +x scripts/start_frontend.sh
   ./scripts/start_frontend.sh
   ```

3. **访问应用**：
   - 浏览器访问 `http://localhost:3000`

## 手动启动

### 后端

```bash
cd backend
# 首次运行需要创建虚拟环境
py -m venv venv
venv\Scripts\activate  # Windows
# 或 source venv/bin/activate  # Linux/Mac

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动服务
python main.py
```

后端将在 `http://localhost:8000` 启动
- API 文档：`http://localhost:8000/docs`

### 前端

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm start
```

前端将在 `http://localhost:3000` 启动

## 验证服务运行

### 检查后端
- 访问 `http://localhost:8000/state` 应该返回 JSON 数据
- 访问 `http://localhost:8000/docs` 查看 API 文档

### 检查前端
- 访问 `http://localhost:3000` 应该看到可视化界面
- 控制台应该显示 WebSocket 连接成功

## 停止服务

- 在运行服务的终端窗口按 `Ctrl+C`

## 故障排除

如果遇到问题，请查看：
- `docs/RUN_GUIDE.md` - 详细运行指南
- `docs/TROUBLESHOOTING.md` - 故障排除指南

