# Troubleshooting Guide

## Frontend Startup Issues

### Issue: Script exits immediately without showing errors

**Solution**: Use the debug script:
```bash
start_frontend_debug.bat
```

This script will:
- Check all prerequisites step by step
- Show detailed error messages
- Pause on errors so you can read them

### Issue: TypeScript compilation errors

**Fixed**: Updated `tsconfig.json` to:
- Set `target` to `es2015` (was `es5`)
- Added `downlevelIteration: true`

### Issue: npm install fails with dependency conflicts

**Solution**: Use `--legacy-peer-deps` flag:
```bash
cd frontend
npm install --legacy-peer-deps
```

### Issue: Port 3000 already in use

**Solution**: 
1. Find the process:
```bash
netstat -ano | findstr ":3000"
```

2. Kill the process (replace PID):
```bash
taskkill /F /PID <PID>
```

Or the frontend will automatically try the next port (3001, 3002, etc.)

### Issue: Module not found errors

**Solution**: Reinstall dependencies:
```bash
cd frontend
rmdir /s /q node_modules
npm install --legacy-peer-deps
```

## Backend Startup Issues

### Issue: Port 8000 already in use

**Solution**: Use `fix_port.bat`:
```bash
fix_port.bat
```

Or manually:
```bash
netstat -ano | findstr ":8000"
taskkill /F /PID <PID>
```

### Issue: ModuleNotFoundError

**Solution**: Install dependencies:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

## Common Commands

### Check if ports are in use
```bash
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"
```

### Kill all Node processes
```bash
taskkill /F /IM node.exe
```

### Kill all Python processes
```bash
taskkill /F /IM python.exe
```

### Check TypeScript compilation
```bash
cd frontend
npx tsc --noEmit
```

### Reinstall frontend dependencies
```bash
cd frontend
rmdir /s /q node_modules
npm install --legacy-peer-deps
```

## Debug Scripts

- `start_frontend_debug.bat` - Detailed frontend startup with error checking
- `start_frontend_simple.bat` - Simplified frontend startup
- `fix_port.bat` - Fix port 8000 conflicts

