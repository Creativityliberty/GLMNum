# GLM v4.0 - Complete Repository Structure

## 🌲 Full Directory Tree

```
glm_prototype/
│
├── 📄 README.md                              # Main documentation
├── 📄 GLM_v3.0_GUIDE.md                     # GLM v3.0 core concepts
├── 📄 GLM_NUMTRIAD_INTEGRATION.md           # Integration architecture
├── 📄 REPO_STRUCTURE_V4.md                  # This file
├── 📄 NUMTRIAD_V4_COMPLETE.md               # NumTriad V4 documentation
├── 📄 requirements.txt                       # Python dependencies
├── 📄 pyproject.toml                        # Package configuration
│
├── 🔧 CONFIGURATION & ENTRY POINTS
├── 📄 api.py                                # FastAPI main server
├── 📄 main.py                               # CLI entry point
├── 📄 config.yaml                           # Global configuration
│
├── 📁 core/                                 # ∆∞Ο Symbolic Core
│   ├── __init__.py
│   ├── symbolic.py                          # SymbolicEngine (∆∞Ο)
│   ├── config.py                            # Configuration management
│   ├── utils.py                             # Shared utilities
│   └── logging_utils.py                     # Unified logging
│
├── 📁 domains/                              # Multi-Domain Support
│   ├── __init__.py
│   ├── text_domain.py                       # Text processing
│   ├── code_domain.py                       # Code analysis
│   ├── geometry_domain.py                   # Geometric reasoning
│   ├── image_domain.py                      # Image processing
│   ├── vision_transform_domain.py           # VTE/VTM (NEW)
│   └── audio_domain.py                      # Audio processing (future)
│
├── 📁 encoders/                             # Encoder Registry
│   ├── __init__.py
│   ├── base_text_encoder.py                 # Base text (TF-IDF, hash)
│   ├── hf_text_encoder.py                   # HuggingFace text
│   ├── hf_vision_encoder.py                 # HuggingFace vision
│   ├── hf_code_encoder.py                   # HuggingFace code
│   ├── hf_audio_encoder.py                  # HuggingFace audio
│   ├── nomic_text_encoder.py                # Nomic text
│   ├── nomic_image_encoder.py               # Nomic vision
│   └── encoder_registry.py                  # Dynamic encoder selection
│
├── 📁 numtriad/                             # NumTriad System (NEW)
│   ├── __init__.py
│   │
│   ├── 📁 core/                             # ∆∞Ο Mathematical Core
│   │   ├── __init__.py
│   │   ├── delta_infty_omicron_math.py      # Math definitions & axioms
│   │   ├── triad_features.py                # Triad feature extraction
│   │   ├── triad_distance.py                # Triad distance metrics
│   │   └── system_v4.py                     # NumTriadSystemV4 (unified)
│   │
│   ├── 📁 encoders/                         # Triad Encoders
│   │   ├── __init__.py
│   │   ├── numtriad_v2_text.py              # NumTriad V2 (text only)
│   │   ├── numtriad_v3_multimodal.py        # NumTriad V3/V4 (multimodal)
│   │   ├── hf_deeptriad_core.py             # HF + triad head wrapper
│   │   └── fusion_heads.py                  # Triad fusion heads
│   │
│   ├── 📁 models/                           # Triad Models
│   │   ├── __init__.py
│   │   ├── triad_scorer_mlp_v2.py           # TriadScorerMLP-V2
│   │   ├── deeptriad_transformer.py         # DeepTriadTransformer (Pillar C)
│   │   ├── triad_fusion_model.py            # Fusion models
│   │   └── triad_fusion_head_v3.py          # Fusion head V3
│   │
│   ├── 📁 rag/                              # RAG Systems
│   │   ├── __init__.py
│   │   ├── numtriad_rag_v3.py               # RAG V3 (text)
│   │   ├── deeptriad_rag_v4.py              # NumTriadRAGIndexV4 (Pillar D)
│   │   └── chunking.py                      # Document chunking strategies
│   │
│   ├── 📁 vision/                           # Vision Transformation
│   │   ├── __init__.py
│   │   ├── vte.py                           # VisionTransformationEngine
│   │   ├── vtm.py                           # Visual Transformation Morphisms
│   │   └── visual_utils.py                  # Graph utilities
│   │
│   ├── 📁 data/                             # Data & Schemas
│   │   ├── __init__.py
│   │   ├── schemas.py                       # Data schemas
│   │   ├── dataloader_triad_text.py         # Text dataset loader
│   │   ├── dataloader_triad_multimodal.py   # Multimodal dataset loader
│   │   ├── dataloader_sequences.py          # Sequence dataset loader
│   │   └── 📁 examples/
│   │       ├── numtriad_v2_sample.jsonl
│   │       ├── numtriad_v3_multimodal_sample.jsonl
│   │       └── deeptriad_sequences_sample.jsonl
│   │
│   ├── 📁 training/                         # Training Scripts
│   │   ├── __init__.py
│   │   ├── train_triad_scorer_v2.py         # Train TriadScorerMLP-V2
│   │   ├── train_numtriad_v2_text.py        # Train NumTriad V2
│   │   ├── train_numtriad_v3_multimodal.py  # Train NumTriad V3/V4
│   │   ├── train_deeptriad_transformer.py   # Train DeepTriad Transformer
│   │   └── losses.py                        # Custom loss functions
│   │
│   └── 📁 eval/                             # Evaluation
│       ├── __init__.py
│       ├── eval_triad_classification.py     # Triad classification eval
│       ├── eval_rag_triad.py                # RAG evaluation
│       └── eval_multimodal_alignment.py     # Multimodal alignment eval
│
├── 📁 benchmarks/                           # Benchmark Suite
│   ├── __init__.py
│   ├── 📁 numtbench/                        # NumTBench (main benchmark)
│   │   ├── __init__.py
│   │   ├── tasks_text.py                    # Text tasks
│   │   ├── tasks_multimodal.py              # Multimodal tasks
│   │   ├── tasks_rag.py                     # RAG scenarios
│   │   ├── metrics.py                       # Evaluation metrics
│   │   └── numtbench_runner.py              # Benchmark runner
│   └── 📄 NUMTBENCH.md                      # Benchmark documentation
│
├── 📁 web_ui/                               # Web Interface
│   ├── index.html                           # Main page
│   ├── app.js                               # Application logic
│   ├── style.css                            # Styling
│   ├── 📁 components/
│   │   ├── triad_panel.js                   # Triad visualization
│   │   ├── vision_vte_view.js               # VTE graph view
│   │   ├── rag_console.js                   # RAG search console
│   │   └── settings_panel.js                # Settings & mode selection
│   └── 📁 assets/
│       ├── logo_glm.svg
│       ├── logo_numtriad.svg
│       └── 📁 diagrams/
│           ├── delta_infty_omicron.png
│           ├── triad_space.png
│           └── integration_flow.png
│
├── 📁 examples/                             # Usage Examples
│   ├── __init__.py
│   ├── demo_cli.py                          # CLI demo
│   ├── demo_numtriad_text.py                # Text triad demo
│   ├── demo_numtriad_multimodal.py          # Multimodal demo
│   ├── demo_deeptriad_sequence.py           # Sequence analysis demo
│   ├── demo_vte_graph.py                    # Vision graph demo
│   └── demo_rag_triad_v4.py                 # RAG demo
│
├── 📁 scripts/                              # Utility Scripts
│   ├── __init__.py
│   ├── run_api.sh                           # Start API server
│   ├── run_web.sh                           # Start web UI
│   ├── index_corpus_numtriad_v2.py          # Index corpus (V2)
│   ├── index_corpus_numtriad_v3.py          # Index corpus (V3)
│   └── export_checkpoints.py                # Export models
│
├── 📁 tests/                                # Test Suite
│   ├── __init__.py
│   ├── test_core_symbolic.py                # Symbolic engine tests
│   ├── test_domains_text.py                 # Text domain tests
│   ├── test_numtriad_v2.py                  # NumTriad V2 tests
│   ├── test_numtriad_v3_multimodal.py       # NumTriad V3 tests
│   ├── test_deeptriad_transformer.py        # DeepTriad tests
│   ├── test_vte_vtm.py                      # Vision tests
│   └── test_rag_triad_v4.py                 # RAG tests
│
└── 📁 docs/                                 # Documentation
    ├── __init__.py
    ├── 📄 NUMTRIAD_V2_SPEC.md               # NumTriad V2 specification
    ├── 📄 NUMTRIAD_V3_V4_SPEC.md            # NumTriad V3/V4 specification
    ├── 📄 GLM_NUMTRIAD_INTEGRATION.md       # Integration guide
    ├── 📄 VTE_VTM_SPEC.md                   # Vision engine spec
    ├── 📄 API_REFERENCE.md                  # API documentation
    ├── 📄 ROADMAP_2030.md                   # Future roadmap
    └── 📁 archived/                         # Old documentation
        ├── BACKEND_COMPLETE.txt
        ├── SYSTEM_RUNNING_FINAL.txt
        └── ...
```

---

## 📊 Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (api.py)                       │
│  /transform, /analyze, /similarity, /embed/numtriad, etc.  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              SymbolicEngine (core/symbolic.py)              │
│  ∆∞Ο Core + Embedding Mode Routing                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐   ┌──────────┐   ┌──────────────┐
   │ Domains│   │ Encoders │   │   NumTriad   │
   │        │   │          │   │              │
   │ Text   │   │ Base     │   │ V2/V3/V4     │
   │ Code   │   │ HF       │   │ DeepTriad    │
   │ Image  │   │ Nomic    │   │ VTE/VTM      │
   │ Geo    │   │ Registry │   │ RAG V4       │
   └────────┘   └──────────┘   └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │    Output (Embedding +      │
        │    Triad + Metadata)        │
        └─────────────────────────────┘
```

---

## 🔄 Data Flow Example

```
User Query: "Explain quantum mechanics"
    ↓
api.py: POST /unified/search
    ↓
SymbolicEngine.encode(text, embedding_mode="numtriad_v3")
    ├─ Domain routing: text_domain
    ├─ Encoder selection: NumTriadEmbeddingV3
    ├─ Encode: text → (embedding, triad)
    └─ Output: {emb: [...], triad: [0.3, 0.6, 0.1]}
    ↓
NumTriadRAGIndexV4.query(embedding, triad, mode="auto")
    ├─ Analyze triad: high ∞ → abstract mode
    ├─ Semantic ranking: cosine_sim
    ├─ Triad ranking: alignment
    └─ Combined score: α*semantic + (1-α)*triad
    ↓
web_ui: Display results with triad visualization
```

---

## 📋 File Categories

### Core System
- `api.py` - FastAPI server
- `core/symbolic.py` - ∆∞Ο engine
- `main.py` - CLI entry

### Domain Support
- `domains/*.py` - Domain implementations
- `encoders/*.py` - Encoder registry

### NumTriad Integration
- `numtriad/core/` - Mathematical foundations
- `numtriad/encoders/` - Triad encoders
- `numtriad/models/` - Neural models
- `numtriad/rag/` - RAG systems
- `numtriad/vision/` - Vision engines

### Training & Evaluation
- `numtriad/training/` - Training scripts
- `numtriad/eval/` - Evaluation scripts
- `benchmarks/numtbench/` - Benchmark suite

### Interface
- `web_ui/` - Web interface
- `examples/` - Usage examples
- `scripts/` - Utility scripts

### Testing & Documentation
- `tests/` - Test suite
- `docs/` - Documentation

---

## 🎯 Integration Checklist

- [ ] SymbolicEngine supports embedding_mode
- [ ] NumTriadEmbeddingV3 multimodal working
- [ ] DeepTriadTransformer sequence analysis
- [ ] VisionTransformationEngine visual graphs
- [ ] NumTriadRAGIndexV4 triad-aware search
- [ ] API endpoints all modes
- [ ] Web UI mode selector
- [ ] Tests passing
- [ ] Documentation complete

---

## 📈 Scalability Path

```
Phase 1: Core Integration (Current)
  ├─ SymbolicEngine + NumTriad V2/V3
  ├─ Basic RAG V4
  └─ Web UI with mode selector

Phase 2: Advanced Features (Next)
  ├─ DeepTriad Transformer production
  ├─ VTE/VTM full implementation
  ├─ Multimodal fusion optimization
  └─ Performance benchmarking

Phase 3: Production Ready (2030)
  ├─ Distributed RAG
  ├─ Model serving (ONNX/TorchServe)
  ├─ Advanced monitoring
  └─ Enterprise features
```

---

**Version**: 4.0.0  
**Last Updated**: 2024-11-16  
**Status**: Architecture Complete
