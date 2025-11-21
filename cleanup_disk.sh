#!/bin/bash

# GLM v4.0 - Disk Cleanup Script
# Frees up space for PyTorch installation

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         GLM v4.0 - Disk Cleanup & Space Recovery              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check current disk usage
echo "Step 1: Checking disk usage..."
echo "Before cleanup:"
df -h / | tail -1
BEFORE=$(df / | tail -1 | awk '{print $4}')
echo "Available: ${BEFORE}K"
echo ""

# Step 2: Clean pip cache
echo "Step 2: Cleaning pip cache..."
pip cache purge
echo "✅ pip cache cleaned"
echo ""

# Step 3: Clean npm cache (if npm installed)
echo "Step 3: Cleaning npm cache (if available)..."
if command -v npm &> /dev/null; then
    npm cache clean --force
    echo "✅ npm cache cleaned"
else
    echo "⚠️  npm not found, skipping"
fi
echo ""

# Step 4: Clean brew cache (if brew installed)
echo "Step 4: Cleaning brew cache (if available)..."
if command -v brew &> /dev/null; then
    brew cleanup -s
    echo "✅ brew cache cleaned"
else
    echo "⚠️  brew not found, skipping"
fi
echo ""

# Step 5: Clean Xcode cache (if present)
echo "Step 5: Cleaning Xcode cache (if present)..."
if [ -d ~/Library/Developer/Xcode/DerivedData ]; then
    rm -rf ~/Library/Developer/Xcode/DerivedData/*
    echo "✅ Xcode cache cleaned"
else
    echo "⚠️  Xcode cache not found"
fi
echo ""

# Step 6: Clean system cache
echo "Step 6: Cleaning system cache..."
if [ -d ~/.cache ]; then
    rm -rf ~/.cache/*
    echo "✅ System cache cleaned"
fi
echo ""

# Step 7: Check freed space
echo "Step 7: Checking freed space..."
echo "After cleanup:"
df -h / | tail -1
AFTER=$(df / | tail -1 | awk '{print $4}')
FREED=$((AFTER - BEFORE))
echo "Available: ${AFTER}K (freed ~${FREED}K)"
echo ""

# Step 8: Verify space for PyTorch
NEEDED=200000  # 200 MB in KB
if [ $AFTER -gt $NEEDED ]; then
    echo "✅ Enough space for PyTorch installation"
else
    echo "⚠️  Still low on space. Freed: ${FREED}K, Need: ${NEEDED}K"
    echo ""
    echo "Additional cleanup options:"
    echo "  - Remove ~/Downloads/*"
    echo "  - Remove old backups"
    echo "  - Check for large files: find ~ -type f -size +100M"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Cleanup Complete!                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Install torch: pip install torch --index-url https://download.pytorch.org/whl/cpu"
echo "3. Verify: python -c \"import torch; print(torch.__version__)\""
echo ""
