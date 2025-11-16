# NumTriad System V4 - Complete Integration

## 🏗️ Architecture Overview

NumTriad V4 integrates **4 pillars** into a unified system:

```
┌─────────────────────────────────────────────────────────────┐
│                  NumTriadSystemV4                           │
│                  (Unified Facade)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Pillar A    │  │  Pillar B    │  │  Pillar C    │     │
│  │ Multimodal   │  │   Vision     │  │  DeepTriad   │     │
│  │    V4        │  │     VTE      │  │ Transformer  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pillar D: NumTriadRAGIndexV4 (Triad-aware RAG)     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧱 The 4 Pillars

### **Pillar A: NumTriadMultimodalV4**

**Purpose**: Multimodal embedding with triad scoring

**Features**:
- Encodes: text, code, images, audio
- Output: `E(x) = [v_semantic | triad_probs(∆,∞,Θ) | T_cross]`
- Learns cross-modal coherence
- Projects to shared space `dim_proj`

**Usage**:
```python
emb, triad = system.encode_sample(
    texts=["Hello world"],
    images=image_tensor,
    codes=["print('hi')"],
    audio_feats=audio_tensor
)
# emb: (B, D_total)
# triad: (B, 3) - ∆, ∞, Θ probabilities
```

---

### **Pillar B: VisionTransformationEngine (VTE)**

**Purpose**: Visual graph with transformation paths

**Features**:
- Visual graph `G_vis` with nodes = images, edges = transforms
- Transformation vector `T_vis = [d_emb, d_triad, d_scale, d_position]`
- Shortest path computation
- Triad-aware morphisms

**Usage**:
```python
# Add images to graph
system.add_image_to_graph("img_A", image_tensor_a)
system.add_image_to_graph("img_B", image_tensor_b)

# Connect with KNN
system.connect_vision_graph_knn(k=5, use_triad_weighting=True)

# Find transformation path
path, T_vis = system.visual_path("img_A", "img_B")
# path: ["img_A", ..., "img_B"]
# T_vis: aggregated transformation vector
```

---

### **Pillar C: DeepTriadTransformer**

**Purpose**: Sequence-level triad analysis

**Features**:
- Transformer encoder (triad-aware)
- Global triad scoring: `(B, 3)`
- Per-step triad scoring: `(B, L, 3)`
- Handles long documents/sequences

**Usage**:
```python
# Analyze sequence of embeddings
embeddings_seq = np.random.randn(10, 256)  # 10 chunks
triad_global, triad_steps = system.triad_sequence_analysis(embeddings_seq)
# triad_global: (3,) - overall document triad
# triad_steps: (10, 3) - per-chunk triads
```

---

### **Pillar D: NumTriadRAGIndexV4**

**Purpose**: Triad-aware document retrieval

**Features**:
- In-memory index with triad scoring
- Query modes: `auto`, `abstract`, `concrete`, `balanced`
- Combined scoring: `score = α_semantic * cos_sim + α_triad * alignment`

**Query Modes**:
- `auto`: Uses query's own triad
- `abstract`: Favors high ∞ (infinity), low Θ (theta)
- `concrete`: Favors high Θ
- `balanced`: Neutral (1/3, 1/3, 1/3)

**Usage**:
```python
# Index documents
system.add_document(
    "doc1",
    texts=["Abstract theory of intelligence"],
    metadata={"type": "theory"}
)
system.add_document(
    "doc2",
    texts=["Concrete tutorial: deploy FastAPI"],
    metadata={"type": "howto"}
)

# Query with different modes
results = system.query_documents(
    "explain general theory",
    mode="abstract",
    k=5
)
# Returns: [(doc, score), ...]
```

---

## 📊 Triad (∆∞Θ) Explanation

The **triad** represents three dimensions of abstraction:

| Symbol | Name | Meaning |
|--------|------|---------|
| **∆** | Delta | Difference/Specificity (concrete details) |
| **∞** | Infinity | Generality/Universality (abstract concepts) |
| **Θ** | Theta | Theta (context/application) |

**Examples**:
- "The cat sat on the mat" → High ∆ (specific), Low ∞
- "All mammals have fur" → High ∞ (general), Medium ∆
- "Deploy on Ubuntu" → High Θ (application), Medium ∆

---

## 🚀 Quick Start

### Installation

```bash
# Ensure dependencies
pip install torch numpy

# Import
from numtriad.core.system_v4 import NumTriadSystemV4, NumTriadSystemConfig
from numtriad.multimodal_v4 import MultimodalV4Config
```

### Basic Example

```python
import torch
from numtriad.core.system_v4 import NumTriadSystemV4, NumTriadSystemConfig
from numtriad.multimodal_v4 import MultimodalV4Config

# Configure
mm_cfg = MultimodalV4Config(
    dim_text_in=256,
    dim_vision_in=256,
    dim_code_in=256,
    dim_audio_in=128,
    dim_proj=192,
    dim_t_cross=32,
    device="cpu"
)

sys_cfg = NumTriadSystemConfig(
    multimodal=mm_cfg,
    device="cpu"
)

# Initialize
system = NumTriadSystemV4(sys_cfg)

# Index documents
system.add_document("doc1", texts=["Abstract theory"])
system.add_document("doc2", texts=["Concrete tutorial"])

# Query
results = system.query_documents("explain theory", mode="abstract", k=2)
for doc, score in results:
    print(f"{doc.doc_id}: {score:.3f}")
```

---

## 🔧 Advanced Usage

### Multi-Modal Encoding

```python
# Encode multiple modalities
emb, triad = system.encode_sample(
    texts=["Hello world"],
    images=torch.randn(1, 3, 224, 224),
    codes=["def hello(): print('hi')"],
    audio_feats=torch.randn(1, 128)
)

print(f"Embedding shape: {emb.shape}")  # (1, D_total)
print(f"Triad: {triad[0]}")  # [∆, ∞, Θ]
```

### Vision Graph Construction

```python
# Create visual graph
imgs = torch.randn(5, 3, 64, 64)
for i, img in enumerate(imgs):
    system.add_image_to_graph(f"img_{i}", img)

# Connect with KNN
system.connect_vision_graph_knn(k=2, use_triad_weighting=True)

# Find paths
for i in range(4):
    path, T_vis = system.visual_path(f"img_{i}", f"img_{i+1}")
    print(f"Path {i}->{i+1}: {path}")
```

### Sequence Analysis

```python
# Analyze document sequence
chunks = [
    "Introduction to AI",
    "Deep learning basics",
    "Neural networks",
    "Transformers"
]

# Encode each chunk
embeddings = []
for chunk in chunks:
    emb, _ = system.encode_sample(texts=[chunk])
    embeddings.append(emb[0])

embeddings_seq = np.array(embeddings)

# Analyze triad progression
triad_global, triad_steps = system.triad_sequence_analysis(embeddings_seq)

print(f"Global triad: {triad_global}")  # Overall document
print(f"Step triads:\n{triad_steps}")   # Per-chunk
```

### Custom Query Modes

```python
# Different query modes
query = "machine learning"

for mode in ["auto", "abstract", "concrete", "balanced"]:
    results = system.query_documents(query, mode=mode, k=3)
    print(f"\n[{mode.upper()}]")
    for doc, score in results:
        print(f"  {doc.doc_id}: {score:.3f}")
```

---

## 📈 Performance Characteristics

| Operation | Time | Memory |
|-----------|------|--------|
| Encode sample | ~50ms | ~100MB |
| Add document | ~60ms | +10MB |
| Query (k=5) | ~10ms | ~50MB |
| Visual path | ~5ms | ~20MB |
| Sequence analysis | ~100ms | ~200MB |

*Estimates for CPU, batch_size=1*

---

## 🔌 Integration with Backend API

The system is exposed via FastAPI:

```python
# In backend.py
from numtriad.core.system_v4 import NumTriadSystemV4, NumTriadSystemConfig

system = NumTriadSystemV4(config)

@app.post("/transform")
async def transform(req: TransformRequest):
    emb, triad = system.encode_sample(texts=[req.content])
    return {
        "embedding": emb[0].tolist(),
        "triad": {"delta": triad[0][0], "infinity": triad[0][1], "theta": triad[0][2]}
    }

@app.post("/unified/search")
async def search(req: SearchRequest):
    results = system.query_documents(req.query, mode=req.triad_target, k=req.k)
    return {
        "results": [
            {"doc_id": doc.doc_id, "score": float(score), "metadata": doc.metadata}
            for doc, score in results
        ]
    }
```

---

## 🧪 Testing

```python
# Test all pillars
def test_system():
    cfg = NumTriadSystemConfig(...)
    system = NumTriadSystemV4(cfg)
    
    # Test Pillar A
    emb, triad = system.encode_sample(texts=["test"])
    assert emb.shape == (1, 192)
    assert triad.shape == (1, 3)
    
    # Test Pillar D
    system.add_document("doc1", texts=["test"])
    results = system.query_documents("test", k=1)
    assert len(results) == 1
    
    # Test Pillar B (if VTE available)
    if system.vte:
        img = torch.randn(3, 64, 64)
        system.add_image_to_graph("img1", img)
        assert "img1" in system.vte.nodes
    
    # Test Pillar C (if DeepTriad available)
    if system.deeptriad:
        seq = np.random.randn(5, 192)
        triad_g, triad_s = system.triad_sequence_analysis(seq)
        assert triad_g.shape == (3,)
        assert triad_s.shape == (5, 3)
    
    print("✅ All tests passed!")

test_system()
```

---

## 📚 File Structure

```
numtriad/
├── core/
│   ├── __init__.py
│   └── system_v4.py          ← Main integration
├── multimodal_v4.py          ← Pillar A
├── vision/
│   ├── __init__.py
│   └── vte.py                ← Pillar B
└── models/
    └── deeptriad_transformer.py  ← Pillar C (optional)
```

---

## 🎯 Use Cases

### 1. **Multi-Level Search**
```python
# Find abstract theory
results = system.query_documents("theory", mode="abstract")

# Find concrete tutorials
results = system.query_documents("tutorial", mode="concrete")
```

### 2. **Document Classification**
```python
# Analyze document triad
emb, triad = system.encode_sample(texts=[document])
if triad[0][1] > 0.6:  # High ∞
    print("Abstract document")
elif triad[0][2] > 0.6:  # High Θ
    print("Practical document")
```

### 3. **Visual Transformation**
```python
# Find visual similarity path
path, T_vis = system.visual_path("img_abstract", "img_concrete")
# Use path for visual reasoning
```

### 4. **Sequence Reasoning**
```python
# Analyze reasoning chain
triads = system.triad_sequence_analysis(reasoning_steps)
# Track abstraction level changes
```

---

## 🐛 Troubleshooting

### ImportError: NumTriadMultimodalV4 not found
- Ensure `numtriad/multimodal_v4.py` exists
- Check imports in `__init__.py`

### CUDA out of memory
- Reduce batch size
- Use `device="cpu"`
- Reduce `dim_proj`

### VTE not initialized
- Ensure `numtriad/vision/vte.py` exists
- Check `VTE_AVAILABLE` flag

### Empty RAG results
- Add documents first with `add_document()`
- Check query mode matches document type

---

## 📖 API Reference

### NumTriadSystemV4

```python
class NumTriadSystemV4:
    def __init__(cfg: NumTriadSystemConfig)
    
    # Pillar A
    def encode_sample(...) -> Tuple[np.ndarray, np.ndarray]
    
    # Pillar D
    def add_document(doc_id, texts, images, codes, audio_feats, metadata)
    def query_documents(query_text, mode, k) -> List[Tuple[IndexedDoc, float]]
    
    # Pillar B
    def add_image_to_graph(node_id, image, metadata) -> VisualNode
    def connect_vision_graph_knn(k, use_triad_weighting, kind)
    def visual_path(source_id, target_id) -> Tuple[List[str], np.ndarray]
    
    # Pillar C
    def triad_sequence_analysis(embeddings_seq) -> Tuple[np.ndarray, np.ndarray]
    
    # Status
    def get_status() -> Dict[str, Any]
```

---

## 🎓 Learning Resources

- **Triad Theory**: See `PILLAR_A_INTEGRATION.txt`
- **Vision VTE**: See `PILLAR_B_INTEGRATION.txt`
- **DeepTriad**: See `PILLAR_C_INTEGRATION.txt`
- **RAG System**: See `SYSTEM_RUNNING_FINAL.txt`

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | 2024-11-16 | Complete integration of 4 pillars |
| 3.0.0 | 2024-11-15 | Initial Pillars A & B |
| 2.0.0 | 2024-11-10 | DeepTriad Transformer |
| 1.0.0 | 2024-11-01 | RAG Index |

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review example usage
3. Check logs with `logging.basicConfig(level=logging.DEBUG)`

---

**NumTriad V4 - Unified Multimodal Triad-Aware System** ✨
