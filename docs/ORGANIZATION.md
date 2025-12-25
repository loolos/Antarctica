# Project File Organization

This document describes the project file organization structure.

## 📁 New Directory Structure

The project has been organized by functionality. The new directory structure is as follows:

```
Antarctica/
├── docs/                    # 📚 Documentation directory
│   ├── README.md            # Documentation index
│   ├── QUICK_START.md       # Quick start guide
│   ├── RUN_GUIDE.md         # Run guide
│   ├── ARCHITECTURE.md      # Architecture design document
│   ├── TESTING.md           # Testing documentation
│   ├── TROUBLESHOOTING.md   # Troubleshooting
│   └── ...                  # Other documents
│
├── scripts/                 # 🔧 Scripts directory
│   ├── start_backend.bat/sh # Start backend
│   ├── start_frontend.bat/sh # Start frontend
│   ├── run_tests.bat/sh     # Run tests
│   └── ...                  # Other scripts
│
├── tools/                   # 🛠️ Tools directory
│   ├── find_chinese_in_bats.*
│   ├── fix_deprecation.*
│   └── ...                  # Development tool scripts
│
├── tests/                   # 🧪 Tests directory
│   ├── test_*.py            # All test files
│   ├── run_tests.py         # Test runner
│   └── README.md            # Test documentation
│
├── simulation/              # 🎮 Simulation core
├── backend/                 # 🔌 Backend service
├── frontend/                # 🎨 Frontend interface
└── README.md                # Main documentation
```

## 🔄 File Movement Record

### Documentation Files → `docs/`
- `QUICK_START.md`
- `RUN_GUIDE.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `TROUBLESHOOTING.md`
- `TRANSLATION_COMPLETE.md`
- `TRANSLATION_SUMMARY.md`
- `START_TEST_RESULTS.md`
- `TEST_RESULTS.md`

### Script Files → `scripts/`
- `start_backend.bat` / `start_backend.sh`
- `start_frontend.bat` / `start_frontend.sh`
- `start_frontend_debug.bat`
- `start_frontend_simple.bat`
- `run_tests.bat` / `run_tests.sh`
- `test_frontend.bat`
- `test_server_start.bat`
- `fix_port.bat`

### Tool Files → `tools/`
- `find_chinese_in_bats.js` / `find_chinese_in_bats.py`
- `find_deprecated.js`
- `fix_deprecation.js` / `fix_deprecation.py`

### Test Files → `tests/`
- `test_quick.py`
- `test_simulation.py`
- `test_backend.py`
- `reproduce_bug.py`

## ✅ Completed Updates

### 1. Script Path Updates
All script files have been updated to correctly access the project root directory from the `scripts/` directory:
- Windows batch files: Use `cd /d %~dp0..` to return to project root
- Linux/Mac shell scripts: Use `cd "$(dirname "$0")/.."` to return to project root

### 2. Documentation Path Updates
- `README.md` - Updated project structure and script path references
- `docs/QUICK_START.md` - Updated script paths
- `docs/RUN_GUIDE.md` - Updated script paths and document links
- `docs/TESTING.md` - Updated test file paths

### 3. New Documents
- `docs/README.md` - Documentation index to help quickly find needed documents

## 📝 Usage Instructions

### Running Scripts
All scripts are now in the `scripts/` directory. Usage:

**Windows**:
```bash
# Double-click to run, or execute in command line
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

### Viewing Documentation
All documentation is in the `docs/` directory:
- View documentation index: `docs/README.md`
- Quick start: `docs/QUICK_START.md`
- Detailed guide: `docs/RUN_GUIDE.md`

### Running Tests
All test files are in the `tests/` directory:
```bash
# Quick test
python tests/test_quick.py

# Full test suite
python tests/run_tests.py

# Or use scripts
scripts/run_tests.bat  # Windows
./scripts/run_tests.sh  # Linux/Mac
```

## 🎯 Organization Benefits

1. **Clear Structure** - Organized by functionality, easy to find
2. **Easy Maintenance** - Related files are centrally managed
3. **Unified Paths** - All script and documentation paths have been updated
4. **Complete Documentation** - New documentation index for easy navigation

## 📌 Notes

- All scripts have been updated with paths and can be run directly from the `scripts/` directory
- Path references in documentation have been updated, but it's recommended to view documents from the project root
- Tool scripts are in the `tools/` directory and are usually run from the project root

---

**Organization Completed Date**: 2025-12-25
