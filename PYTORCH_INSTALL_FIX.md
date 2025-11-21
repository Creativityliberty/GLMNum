# PyTorch Installation - Fix Guide

## Problems Identified

### 1. ❌ Disk Space Issue
- **Error**: "No space left on device"
- **Current**: 585 MB available / 466 GB total
- **Needed**: ~200 MB for PyTorch
- **Status**: CRITICAL

### 2. ❌ Wrong Package Name
- **Error**: "pytorch" vs "torch"
- **Fix**: Use `torch` not `pytorch`
- **Status**: EASY FIX

### 3. ⚠️ Python Version Mismatch
- **Issue**: Using Python 3.13 in some places, 3.11 in venv
- **Fix**: Ensure consistent Python 3.11 usage
- **Status**: NEEDS ATTENTION

---

## Solution

### Step 1: Free Up Disk Space (PRIORITY 1)

```bash
# Check what's taking space
du -sh ~/* | sort -rh | head -20

# Clean Xcode cache (if present)
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Clean pip cache
pip cache purge

# Clean npm cache (if present)
npm cache clean --force

# Clean brew cache (if present)
brew cleanup -s

# Target: Free up at least 500 MB
```

### Step 2: Use Correct Virtual Environment

```bash
# Activate the venv with Python 3.11
source /Volumes/Numtema/Ava\ agent/GLM/glm_prototype/venv/bin/activate

# Verify Python version
python --version
# Should show: Python 3.11.12

# Verify pip
pip --version
```

### Step 3: Install torch (NOT pytorch)

```bash
# Install torch with CPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__}')"
```

### Step 4: Install Other Dependencies

```bash
# Install remaining dependencies
pip install fastapi uvicorn numpy networkx requests beautifulsoup4 lxml psutil

# Verify all
pip list | grep -E "torch|numpy|fastapi|networkx"
```

---

## Quick Commands

### Free Space Immediately
```bash
# Remove large directories
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf ~/.cache/*
pip cache purge

# Check freed space
df -h /
```

### Correct Installation
```bash
# 1. Activate correct venv
source /Volumes/Numtema/Ava\ agent/GLM/glm_prototype/venv/bin/activate

# 2. Verify Python 3.11
python --version

# 3. Install torch (correct name!)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. Verify
python -c "import torch; print(torch.__version__)"
```

---

## Troubleshooting

### If still "No space left on device"
```bash
# Check disk usage
df -h /

# Find large files
find ~ -type f -size +100M 2>/dev/null | head -20

# Remove large old files
rm -rf ~/Downloads/*
rm -rf ~/Library/Caches/*
```

### If "pytorch" error appears
```bash
# Use correct package name
pip install torch  # NOT pytorch!
```

### If Python not found
```bash
# Ensure venv is activated
source /Volumes/Numtema/Ava\ agent/GLM/glm_prototype/venv/bin/activate

# Check Python
which python
python --version
```

---

## Expected Output

After successful installation:

```
$ python -c "import torch; print(torch.__version__)"
2.2.2

$ pip list | grep torch
torch                    2.2.2
torchvision              0.17.2
torchaudio               2.2.2
```

---

## Next Steps

1. Free disk space (500 MB minimum)
2. Activate venv with Python 3.11
3. Install torch (correct name)
4. Run tests: `python tests/test_system.py`
5. Expected: 7/7 PASSED

---

**Status**: Ready to execute  
**Time**: ~15 minutes  
**Priority**: CRITICAL
