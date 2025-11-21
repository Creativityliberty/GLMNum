#!/bin/bash

# GLM v4.0 - PyTorch Setup Script
# Downgrade Python to 3.11 and install PyTorch

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         GLM v4.0 - PyTorch Setup & Environment                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check current Python
echo "Step 1: Checking Python versions..."
echo "Current Python: $(python3 --version)"
echo "Available Python 3.11: $(python3.11 --version 2>/dev/null || echo 'Not found')"
echo ""

# Step 2: Create virtual environment with Python 3.11
echo "Step 2: Creating virtual environment with Python 3.11..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3.11 -m venv venv
source venv/bin/activate

echo "✅ Virtual environment created with Python $(python --version)"
echo ""

# Step 3: Upgrade pip
echo "Step 3: Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✅ pip upgraded"
echo ""

# Step 4: Install PyTorch (CPU version)
echo "Step 4: Installing PyTorch..."
echo "Installing CPU version (recommended for testing)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo "✅ PyTorch installed"
echo ""

# Step 5: Install other dependencies
echo "Step 5: Installing other dependencies..."
pip install fastapi uvicorn numpy networkx requests beautifulsoup4 lxml

echo "✅ Dependencies installed"
echo ""

# Step 6: Verify installation
echo "Step 6: Verifying installation..."
echo ""
echo "Python version:"
python --version
echo ""
echo "PyTorch version:"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
echo ""
echo "NumPy version:"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
echo ""
echo "FastAPI version:"
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
echo ""

# Step 7: Check GPU (if available)
echo "Step 7: Checking GPU support..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run tests: python tests/test_system.py"
echo "3. Start backend: python api.py"
echo "4. Open UI: http://localhost:3000"
echo ""
