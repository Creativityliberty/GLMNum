#!/bin/bash

# ============================================================================
# GLM v4.0 Cleanup Script
# ============================================================================
# Removes old files and archives documentation
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    GLM v4.0 Cleanup Script                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
DELETED=0
ARCHIVED=0

# ============================================================================
# STEP 1: Create archived directory
# ============================================================================

echo -e "\n${YELLOW}Step 1: Creating archived directory...${NC}"
mkdir -p docs/archived
echo -e "${GREEN}✅ Created docs/archived${NC}"

# ============================================================================
# STEP 2: Archive old documentation
# ============================================================================

echo -e "\n${YELLOW}Step 2: Archiving old documentation...${NC}"

OLD_DOCS=(
    "BACKEND_COMPLETE.txt"
    "COMPLETE_SYSTEM_SUMMARY.md"
    "EXECUTIVE_SUMMARY.txt"
    "FINAL_STATUS.txt"
    "GEMINI_TRIAD_GUIDE.md"
    "GEMINI_TRIAD_SUMMARY.txt"
    "NUMTRIAD_INTEGRATION.md"
    "NUMTRIAD_V3_RAG_GUIDE.md"
    "NUMTRIAD_V3_SUMMARY.md"
    "PILLAR_A_MULTIMODAL_V4.md"
    "PILLAR_A_SUMMARY.txt"
    "PILLAR_B_INTEGRATION.txt"
    "PROJECT_COMPLETION_SUMMARY.md"
    "PROJECT_FINAL_STATUS.md"
    "STARTUP_INSTRUCTIONS.txt"
    "SYSTEM_RUNNING.txt"
    "SYSTEM_RUNNING_FINAL.txt"
    "SYSTEM_RUNNING_PORT_8080.txt"
)

for doc in "${OLD_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" "docs/archived/$doc"
        echo -e "${GREEN}✅ Archived $doc${NC}"
        ((ARCHIVED++))
    fi
done

# ============================================================================
# STEP 3: Delete old API files
# ============================================================================

echo -e "\n${YELLOW}Step 3: Deleting old API files...${NC}"

OLD_API=(
    "api.py"
    "api_deeptriad.py"
    "api_working.py"
)

for file in "${OLD_API[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✅ Deleted $file${NC}"
        ((DELETED++))
    fi
done

# ============================================================================
# STEP 4: Delete old test files
# ============================================================================

echo -e "\n${YELLOW}Step 4: Deleting old test files...${NC}"

OLD_TESTS=(
    "test_api.py"
    "test_deeptriad_complete.py"
    "test_full_integration.py"
    "test_gemini_triad_wrapper.py"
    "test_multimodal_v4.py"
    "test_numtriad_complete.py"
    "test_numtriad_integration.py"
    "test_numtriad_v3_pillar3.py"
    "test_numtriad_v3_rag.py"
    "test_pillar_b_vte.py"
    "test_v3_complete.py"
)

for file in "${OLD_TESTS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✅ Deleted $file${NC}"
        ((DELETED++))
    fi
done

# ============================================================================
# STEP 5: Delete old demo files
# ============================================================================

echo -e "\n${YELLOW}Step 5: Deleting old demo files...${NC}"

OLD_DEMOS=(
    "chat_demo.py"
    "demo.py"
    "delta_infty_omicron.py"
)

for file in "${OLD_DEMOS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✅ Deleted $file${NC}"
        ((DELETED++))
    fi
done

# ============================================================================
# STEP 6: Delete old cleanup scripts
# ============================================================================

echo -e "\n${YELLOW}Step 6: Deleting old cleanup scripts...${NC}"

OLD_SCRIPTS=(
    "cleanup.py"
    "cleanup.sh"
)

for file in "${OLD_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✅ Deleted $file${NC}"
        ((DELETED++))
    fi
done

# ============================================================================
# STEP 7: Delete backup files
# ============================================================================

echo -e "\n${YELLOW}Step 7: Deleting backup files...${NC}"

if [ -f "web_ui/app.js.backup" ]; then
    rm "web_ui/app.js.backup"
    echo -e "${GREEN}✅ Deleted web_ui/app.js.backup${NC}"
    ((DELETED++))
fi

if [ -f "web_ui/app_simple.js.backup" ]; then
    rm "web_ui/app_simple.js.backup"
    echo -e "${GREEN}✅ Deleted web_ui/app_simple.js.backup${NC}"
    ((DELETED++))
fi

if [ -f "web_ui/index.html.backup" ]; then
    rm "web_ui/index.html.backup"
    echo -e "${GREEN}✅ Deleted web_ui/index.html.backup${NC}"
    ((DELETED++))
fi

if [ -f "web_ui/index_simple.html.backup" ]; then
    rm "web_ui/index_simple.html.backup"
    echo -e "${GREEN}✅ Deleted web_ui/index_simple.html.backup${NC}"
    ((DELETED++))
fi

# ============================================================================
# STEP 8: Summary
# ============================================================================

echo -e "\n${YELLOW}Step 8: Summary${NC}"
echo -e "${GREEN}✅ Archived: $ARCHIVED files${NC}"
echo -e "${GREEN}✅ Deleted: $DELETED files${NC}"

# ============================================================================
# STEP 9: Git commit
# ============================================================================

echo -e "\n${YELLOW}Step 9: Git commit...${NC}"

git add -A
git commit -m "🧹 Cleanup: Remove old files, keep only GLM v4.0 essentials

- Archived old documentation to docs/archived/
- Deleted old API files (api.py, api_deeptriad.py, api_working.py)
- Deleted old test files (11 files)
- Deleted old demo files
- Deleted backup files
- Repository now focused on GLM v4.0

Files archived: $ARCHIVED
Files deleted: $DELETED"

echo -e "${GREEN}✅ Committed to git${NC}"

# ============================================================================
# FINAL MESSAGE
# ============================================================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ Cleanup Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}Summary:${NC}"
echo -e "  📁 Archived: $ARCHIVED files to docs/archived/"
echo -e "  🗑️  Deleted: $DELETED files"
echo -e "  📦 Repository size: $(du -sh . | cut -f1)"
echo -e "  🎯 Focus: GLM v4.0 only"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. git push (to push cleanup to GitHub)"
echo -e "  2. Start building GLM v4.0 features"
echo -e "  3. Update documentation"

echo -e "\n"
