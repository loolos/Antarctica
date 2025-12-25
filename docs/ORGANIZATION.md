# 项目文件整理说明

本文档说明项目的文件组织结构整理情况。

## 📁 新的目录结构

项目已按照功能分类整理，新的目录结构如下：

```
Antarctica/
├── docs/                    # 📚 文档目录
│   ├── README.md            # 文档索引
│   ├── QUICK_START.md       # 快速启动指南
│   ├── RUN_GUIDE.md         # 运行指南
│   ├── ARCHITECTURE.md      # 架构设计文档
│   ├── TESTING.md           # 测试文档
│   ├── TROUBLESHOOTING.md   # 故障排除
│   └── ...                  # 其他文档
│
├── scripts/                 # 🔧 脚本目录
│   ├── start_backend.bat/sh # 启动后端
│   ├── start_frontend.bat/sh # 启动前端
│   ├── run_tests.bat/sh     # 运行测试
│   └── ...                  # 其他脚本
│
├── tools/                   # 🛠️ 工具目录
│   ├── find_chinese_in_bats.*
│   ├── fix_deprecation.*
│   └── ...                  # 开发工具脚本
│
├── tests/                   # 🧪 测试目录
│   ├── test_*.py            # 所有测试文件
│   ├── run_tests.py         # 测试运行器
│   └── README.md            # 测试说明
│
├── simulation/              # 🎮 模拟核心
├── backend/                 # 🔌 后端服务
├── frontend/                # 🎨 前端界面
└── README.md                # 主文档
```

## 🔄 文件移动记录

### 文档文件 → `docs/`
- `QUICK_START.md`
- `RUN_GUIDE.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `TROUBLESHOOTING.md`
- `TRANSLATION_COMPLETE.md`
- `TRANSLATION_SUMMARY.md`
- `START_TEST_RESULTS.md`
- `TEST_RESULTS.md`

### 脚本文件 → `scripts/`
- `start_backend.bat` / `start_backend.sh`
- `start_frontend.bat` / `start_frontend.sh`
- `start_frontend_debug.bat`
- `start_frontend_simple.bat`
- `run_tests.bat` / `run_tests.sh`
- `test_frontend.bat`
- `test_server_start.bat`
- `fix_port.bat`

### 工具文件 → `tools/`
- `find_chinese_in_bats.js` / `find_chinese_in_bats.py`
- `find_deprecated.js`
- `fix_deprecation.js` / `fix_deprecation.py`

### 测试文件 → `tests/`
- `test_quick.py`
- `test_simulation.py`
- `test_backend.py`
- `reproduce_bug.py`

## ✅ 已完成的更新

### 1. 脚本路径更新
所有脚本文件已更新，现在可以从 `scripts/` 目录正确访问项目根目录：
- Windows 批处理文件：使用 `cd /d %~dp0..` 返回项目根目录
- Linux/Mac Shell 脚本：使用 `cd "$(dirname "$0")/.."` 返回项目根目录

### 2. 文档路径更新
- `README.md` - 更新了项目结构和脚本路径引用
- `docs/QUICK_START.md` - 更新了脚本路径
- `docs/RUN_GUIDE.md` - 更新了脚本路径和文档链接
- `docs/TESTING.md` - 更新了测试文件路径

### 3. 新增文档
- `docs/README.md` - 文档索引，帮助快速找到所需文档

## 📝 使用说明

### 运行脚本
现在所有脚本都在 `scripts/` 目录下，使用方法：

**Windows**:
```bash
# 双击运行，或在命令行执行
scripts\start_backend.bat
scripts\start_frontend.bat
scripts\run_tests.bat
```

**Linux/Mac**:
```bash
chmod +x scripts/*.sh
./scripts/start_backend.sh
./scripts/start_frontend.sh
./scripts/run_tests.sh
```

### 查看文档
所有文档都在 `docs/` 目录下：
- 查看文档索引：`docs/README.md`
- 快速启动：`docs/QUICK_START.md`
- 详细指南：`docs/RUN_GUIDE.md`

### 运行测试
所有测试文件都在 `tests/` 目录下：
```bash
# 快速测试
python tests/test_quick.py

# 完整测试套件
python tests/run_tests.py

# 或使用脚本
scripts/run_tests.bat  # Windows
./scripts/run_tests.sh  # Linux/Mac
```

## 🎯 整理优势

1. **结构清晰** - 按功能分类，易于查找
2. **易于维护** - 相关文件集中管理
3. **路径统一** - 所有脚本和文档路径已更新
4. **文档完善** - 新增文档索引，方便导航

## 📌 注意事项

- 所有脚本已更新路径，可以直接从 `scripts/` 目录运行
- 文档中的路径引用已更新，但建议从项目根目录查看文档
- 工具脚本在 `tools/` 目录，通常从项目根目录运行

---

**整理完成日期**: 2025-12-25

