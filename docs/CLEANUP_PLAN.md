# Cleanup Plan - GLM v4.0

## Objectif
Nettoyer les anciens fichiers et garder seulement ce qui est nécessaire pour GLM v4.0

## Fichiers à SUPPRIMER (anciens/obsolètes)

### API Anciennes
- `api.py` - Remplacé par `backend.py`
- `api_deeptriad.py` - Intégré dans `backend.py`
- `api_working.py` - Backup ancien

### Fichiers de Test Anciens
- `test_api.py` - Ancien test
- `test_deeptriad_complete.py` - Ancien test
- `test_full_integration.py` - Ancien test
- `test_gemini_triad_wrapper.py` - Ancien test
- `test_multimodal_v4.py` - Ancien test
- `test_numtriad_complete.py` - Ancien test
- `test_numtriad_integration.py` - Ancien test
- `test_numtriad_v3_pillar3.py` - Ancien test
- `test_numtriad_v3_rag.py` - Ancien test
- `test_pillar_b_vte.py` - Ancien test
- `test_v3_complete.py` - Ancien test

### Fichiers de Configuration Anciens
- `chat_demo.py` - Ancien démo
- `demo.py` - Ancien démo
- `delta_infty_omicron.py` - Ancien code

### Fichiers Backup
- `web_ui/app.js.backup` - Backup
- `web_ui/app_simple.js.backup` - Backup
- `web_ui/index.html.backup` - Backup
- `web_ui/index_simple.html.backup` - Backup

### Fichiers de Documentation Anciens (Garder seulement les essentiels)
À ARCHIVER dans `docs/archived/`:
- `BACKEND_COMPLETE.txt`
- `COMPLETE_SYSTEM_SUMMARY.md`
- `EXECUTIVE_SUMMARY.txt`
- `FINAL_STATUS.txt`
- `GEMINI_TRIAD_GUIDE.md`
- `GEMINI_TRIAD_SUMMARY.txt`
- `NUMTRIAD_INTEGRATION.md`
- `NUMTRIAD_V3_RAG_GUIDE.md`
- `NUMTRIAD_V3_SUMMARY.md`
- `PILLAR_A_MULTIMODAL_V4.md`
- `PILLAR_A_SUMMARY.txt`
- `PILLAR_B_INTEGRATION.txt`
- `PROJECT_COMPLETION_SUMMARY.md`
- `PROJECT_FINAL_STATUS.md`
- `STARTUP_INSTRUCTIONS.txt`
- `SYSTEM_RUNNING.txt`
- `SYSTEM_RUNNING_FINAL.txt`
- `SYSTEM_RUNNING_PORT_8080.txt`

### Scripts Anciens
- `cleanup.py` - Ancien script
- `cleanup.sh` - Ancien script

## Fichiers à GARDER

### Core System (Essentiels)
- `core/symbolic.py` - GLM symbolic engine
- `core/unified_system.py` - **NOUVEAU** - Système unifié
- `core/unified_encoding.py` - **NOUVEAU** - API encoding
- `core/smart_search.py` - **NOUVEAU** - Recherche intelligente

### NumTriad (Essentiels)
- `numtriad/core/system_v4.py` - Système unifié NumTriad
- `numtriad/multimodal_v4.py` - Pillar A
- `numtriad/vision/vte.py` - Pillar B
- `numtriad/rag/` - Pillar D
- `numtriad/llm/gemini_triad_wrapper.py` - Gemini integration

### Backend
- `backend.py` - FastAPI backend (17 endpoints)

### Web UI
- `web_ui/index.html` - Interface principale
- `web_ui/app.js` - Logique application
- `web_ui/style.css` - Styling
- `web_ui/test_api.html` - Test API

### Tests (Essentiels)
- `test_numtriad_v4.py` - Tests NumTriad V4

### Documentation (Essentiels)
- `README.md` - Main documentation
- `NUMTRIAD_V4_COMPLETE.md` - NumTriad documentation
- `NUMTRIAD_V4_INTEGRATION_SUMMARY.txt` - Integration guide
- `docs/` - Documentation folder

### Configuration
- `requirements.txt` - Dependencies
- `.gitignore` - Git ignore
- `LICENSE` - MIT License

### Examples
- `examples/one_line_demo.py` - **NOUVEAU** - One-line examples
- `examples/deeptriad_rag_example.py` - RAG example
- `examples/gemini_triad_example.py` - Gemini example

## Structure Finale

```
GLMNum/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── core/
│   ├── symbolic.py
│   ├── unified_system.py          ← NEW
│   ├── unified_encoding.py        ← NEW
│   └── smart_search.py            ← NEW
│
├── numtriad/
│   ├── core/
│   │   ├── __init__.py
│   │   └── system_v4.py
│   ├── multimodal_v4.py
│   ├── vision/
│   │   ├── __init__.py
│   │   └── vte.py
│   ├── rag/
│   ├── llm/
│   │   └── gemini_triad_wrapper.py
│   └── ...
│
├── backend.py
│
├── web_ui/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── test_api.html
│
├── docs/
│   ├── README.md
│   ├── THEORY.md
│   ├── API.md
│   ├── IMPLEMENTATION.md
│   └── archived/              ← Old docs
│
├── examples/
│   ├── one_line_demo.py       ← NEW
│   ├── deeptriad_rag_example.py
│   └── gemini_triad_example.py
│
└── test_numtriad_v4.py
```

## Commandes de Nettoyage

```bash
# 1. Créer dossier archived
mkdir -p docs/archived

# 2. Déplacer anciens fichiers
mv BACKEND_COMPLETE.txt docs/archived/
mv COMPLETE_SYSTEM_SUMMARY.md docs/archived/
# ... etc

# 3. Supprimer anciens fichiers
rm api.py
rm api_deeptriad.py
rm api_working.py
rm test_api.py
rm test_deeptriad_complete.py
# ... etc

# 4. Supprimer backups
rm web_ui/*.backup

# 5. Commit
git add -A
git commit -m "🧹 Cleanup: Remove old files, keep only GLM v4.0 essentials"
git push
```

## Bénéfices

✅ Repository plus propre et léger
✅ Moins de confusion avec les anciens fichiers
✅ Focus sur GLM v4.0
✅ Meilleure maintenabilité
✅ Facilite les contributions

## Timeline

- **Jour 1**: Créer système unifié (DONE)
- **Jour 2**: Nettoyer repository
- **Jour 3-4**: Web UI moderne
- **Jour 5**: Dashboard
- **Jour 6**: Documentation
- **Jour 7**: Tests & Polish
