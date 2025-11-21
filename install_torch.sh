#!/bin/bash

# GLM v4.0 - PyTorch Installation Script (CORRECTED)
# Installs torch (NOT pytorch) with proper error handling

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         GLM v4.0 - PyTorch Installation (CORRECTED)            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python: $PYTHON_VERSION"

# Verify Python 3.11
if [[ ! $PYTHON_VERSION =~ ^3\.11 ]]; then
    echo "❌ Error: Python 3.11 required, found $PYTHON_VERSION"
    echo "Please activate venv: source venv/bin/activate"
    exit 1
fi
echo "✅ Python 3.11 confirmed"
echo ""

# Step 2: Check disk space
echo "Step 2: Checking disk space..."
AVAILABLE=$(df / | tail -1 | awk '{print $4}')
AVAILABLE_MB=$((AVAILABLE / 1024))
echo "Available: ${AVAILABLE_MB}MB"

if [ $AVAILABLE_MB -lt 200 ]; then
    echo "❌ Error: Need 200MB, have ${AVAILABLE_MB}MB"
    echo "Run: bash cleanup_disk.sh"
    exit 1
fi
echo "✅ Sufficient space"
echo ""

# Step 3: Upgrade pip
echo "Step 3: Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Step 4: Install torch (CORRECT NAME!)
echo "Step 4: Installing torch (CPU version)..."
echo "Package: torch (NOT pytorch!)"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

if [ $? -ne 0 ]; then
    echo "❌ PyTorch installation failed"
    exit 1
fi
echo "✅ PyTorch installed"
echo ""

# Step 5: Verify installation
echo "Step 5: Verifying installation..."
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>&1)
echo "PyTorch version: $TORCH_VERSION"

# Check CUDA
CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>&1)
echo "CUDA available: $CUDA_AVAILABLE"

echo "✅ PyTorch verified"
echo ""

# Step 6: Install other dependencies
echo "Step 6: Installing other dependencies..."
pip install fastapi uvicorn numpy networkx requests beautifulsoup4 lxml psutil

echo "✅ Dependencies installed"
echo ""

# Step 7: Final verification
echo "Step 7: Final verification..."
echo ""
echo "Installed packages:"
pip list | grep -E "torch|numpy|fastapi|networkx" || echo "Packages installed"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Installation Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Run tests: python tests/test_system.py"
echo "2. Start backend: python api.py"
echo "3. Open UI: http://localhost:3000"
echo ""
