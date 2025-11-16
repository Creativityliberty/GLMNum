# NumTriad V3 + DeepTriad RAG Guide
## Advanced Triad-Aware Retrieval System

---

## 📋 Overview

**NumTriadEmbeddingV3** combines:
- **BaseTextEncoder**: Semantic embeddings via SentenceTransformer
- **DeepTriadTransformer**: Sequence-level triad prediction
- **Triad Target Modes**: Control abstraction level (auto/abstract/concrete/balanced)
- **Enriched Embeddings**: `[semantic_vector | α * triad_scores]`

**DeepTriadRAGIndex** provides:
- **Triad-Aware Retrieval**: Semantic similarity + triad distance
- **Multiple Retrieval Modes**: cosine, triad_weighted
- **Batch Operations**: Process multiple queries efficiently
- **Document Metadata**: Store and retrieve custom metadata

---

## 🚀 Quick Start

### 1. Configuration

```python
from numtriad.config import NumTriadConfig
from numtriad.encoders.numtriad_v3 import NumTriadV3Config
from numtriad.rag.deeptriad_rag import DeepTriadRAGIndex

# Base configuration
cfg = NumTriadConfig(
    base_text_model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu",
)

# V3 configuration
v3_cfg = NumTriadV3Config(
    deeptriad_ckpt="checkpoints/deeptriad_transformer_v1.pt",
    max_len=16,
    triad_target_mode="auto",
    triad_alpha=1.0,
)
```

### 2. Create Index

```python
index = DeepTriadRAGIndex(
    base_config=cfg,
    v3_config=v3_cfg,
    retrieval_mode="triad_weighted",
    triad_weight=0.3,
)
```

### 3. Add Documents

```python
docs = [
    "Théorie générale de l'intelligence basée sur ∆∞Ο",
    "Tutoriel pratique : déployer FastAPI avec Docker",
    "Analyse économique concrète d'un marché local",
]

metas = [
    {"type": "theory", "domain": "AI"},
    {"type": "tutorial", "domain": "DevOps"},
    {"type": "case-study", "domain": "Economics"},
]

index.add_documents(docs, metadatas=metas)
```

### 4. Search with Triad Control

```python
# Concrete search
results = index.search(
    query="Comment déployer en production ?",
    k=3,
    triad_target="concrete",
)

# Abstract search
results = index.search(
    query="Qu'est-ce que l'intelligence ?",
    k=3,
    triad_target="abstract",
)

# Balanced search
results = index.search(
    query="Qu'est-ce qu'un système complexe ?",
    k=3,
    triad_target="balanced",
)
```

---

## 🎯 Triad Target Modes

### `auto`
- **Behavior**: Use natural triad prediction from DeepTriad
- **Use Case**: General-purpose search
- **Triad Adjustment**: None

### `abstract`
- **Behavior**: Boost Δ (complexity) and ∞ (generality), reduce Θ (concreteness)
- **Use Case**: Theoretical, conceptual queries
- **Adjustment**: Δ+0.15, ∞+0.15, Θ-0.15

### `concrete`
- **Behavior**: Boost Θ (concreteness), reduce Δ and ∞
- **Use Case**: Practical, implementation-focused queries
- **Adjustment**: Δ-0.15, ∞-0.15, Θ+0.30

### `balanced`
- **Behavior**: Equilibrate to (1/3, 1/3, 1/3)
- **Use Case**: Mixed-level queries
- **Adjustment**: 50% original + 50% balanced

---

## 🔎 Retrieval Modes

### `cosine`
- **Metric**: Pure cosine similarity on enriched embeddings
- **Formula**: `score = cosine_sim(query_emb, doc_emb)`
- **Use Case**: Fast, semantic-only retrieval

### `triad_weighted`
- **Metric**: Cosine similarity minus triad distance
- **Formula**: `score = cosine_sim - triad_weight * L1_distance(query_triad, doc_triad)`
- **Use Case**: Semantic + abstraction-level alignment
- **Default**: Yes

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  User Query                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. NumTriadEmbeddingV3.encode()                            │
│     ├─ Chunk text into segments                             │
│     ├─ Encode with BaseTextEncoder                          │
│     ├─ Predict triad with DeepTriadTransformer              │
│     ├─ Apply triad_target mode                              │
│     └─ Return enriched embedding [v | α*triad]              │
│                                                             │
│  2. DeepTriadRAGIndex.search()                              │
│     ├─ Compute cosine similarity                            │
│     ├─ (Optional) Compute triad distance                    │
│     ├─ Combine scores (retrieval_mode)                      │
│     └─ Return top-k documents                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓
    Ranked Results with Metadata
```

---

## 💡 Usage Examples

### Example 1: Theory vs Practice

```python
# Theoretical question
theory_results = index.search(
    "What is a general theory of intelligence?",
    k=3,
    triad_target="abstract",
)

# Practical question
practice_results = index.search(
    "How do I set up a development environment?",
    k=3,
    triad_target="concrete",
)
```

### Example 2: Batch Processing

```python
queries = [
    "What is machine learning?",
    "How to train a model?",
    "What are neural networks?",
]

batch_results = index.search_batch(
    queries,
    k=5,
    triad_target="balanced",
)

for query, results in zip(queries, batch_results):
    print(f"Query: {query}")
    for doc, score in results:
        print(f"  - {doc.doc_id}: {score:.4f}")
```

### Example 3: Retrieval Mode Comparison

```python
query = "What is complexity?"

# Pure semantic
cosine_results = index.search(
    query,
    k=3,
    retrieval_mode="cosine",
)

# Semantic + triad alignment
triad_results = index.search(
    query,
    k=3,
    retrieval_mode="triad_weighted",
)
```

### Example 4: Custom Metadata

```python
docs = [
    "Deep learning paper",
    "ML tutorial",
    "Neural network guide",
]

metas = [
    {"year": 2023, "type": "research", "level": "advanced"},
    {"year": 2024, "type": "tutorial", "level": "beginner"},
    {"year": 2023, "type": "guide", "level": "intermediate"},
]

index.add_documents(docs, metadatas=metas)

# Search and filter by metadata
results = index.search("How to learn ML?", k=5, triad_target="concrete")
beginner_results = [
    (doc, score) for doc, score in results
    if doc.meta.get("level") == "beginner"
]
```

---

## 🔧 Advanced Configuration

### Custom Triad Weight

```python
index = DeepTriadRAGIndex(
    base_config=cfg,
    v3_config=v3_cfg,
    retrieval_mode="triad_weighted",
    triad_weight=0.5,  # Higher = more triad distance matters
)
```

### Custom Embedding Alpha

```python
v3_cfg = NumTriadV3Config(
    deeptriad_ckpt="...",
    triad_alpha=2.0,  # Amplify triad scores in embedding
)
```

### Custom Chunk Length

```python
v3_cfg = NumTriadV3Config(
    deeptriad_ckpt="...",
    max_len=32,  # Longer sequences
)
```

---

## 📈 Performance Considerations

| Aspect | Impact | Recommendation |
|--------|--------|-----------------|
| `max_len` | Longer = more context but slower | 16-32 for most cases |
| `triad_weight` | Higher = more triad influence | 0.2-0.5 for balanced |
| `triad_alpha` | Higher = more triad in embedding | 1.0 for standard |
| Retrieval mode | `cosine` faster, `triad_weighted` more accurate | Use `triad_weighted` |

---

## 🧪 Testing

Run the example:
```bash
python examples/deeptriad_rag_example.py
```

Run tests:
```bash
python test_numtriad_v3_rag.py
```

---

## 📚 API Reference

### NumTriadEmbeddingV3

```python
class NumTriadEmbeddingV3:
    def __init__(config, v3_config, device=None)
    def encode(texts, triad_mode="auto", return_raw=False)
        # Returns: (enriched_emb, triads) or (base_emb, enriched_emb, triads)
```

### DeepTriadRAGIndex

```python
class DeepTriadRAGIndex:
    def __init__(base_config, v3_config, retrieval_mode="triad_weighted", triad_weight=0.3)
    def add_documents(texts, metadatas=None, ids=None, triad_mode="auto")
    def search(query, k=5, triad_target="auto", retrieval_mode=None)
        # Returns: List[(DeepTriadDocument, score)]
    def search_batch(queries, k=5, triad_target="auto")
        # Returns: List[List[(DeepTriadDocument, score)]]
    def get_stats()
        # Returns: Dict with index statistics
```

### DeepTriadDocument

```python
@dataclass
class DeepTriadDocument:
    doc_id: str
    text: str
    meta: Dict[str, Any]
    embedding: np.ndarray  # (dim+3,)
    triad: Triad
```

---

## 🎓 Learning Path

1. **Start**: Run `examples/deeptriad_rag_example.py`
2. **Understand**: Read this guide
3. **Experiment**: Try different `triad_target` modes
4. **Optimize**: Tune `triad_weight` and `triad_alpha`
5. **Deploy**: Integrate into your application

---

## 🚀 Production Deployment

```python
# Load pre-trained checkpoint
index = DeepTriadRAGIndex(cfg, v3_cfg)

# Bulk index documents
with open("documents.jsonl") as f:
    docs = [json.loads(line) for line in f]
    texts = [d["text"] for d in docs]
    metas = [d.get("meta", {}) for d in docs]
    index.add_documents(texts, metadatas=metas)

# Serve via API
@app.post("/search")
def search_endpoint(query: str, k: int = 5, mode: str = "auto"):
    results = index.search(query, k=k, triad_target=mode)
    return [
        {
            "id": doc.doc_id,
            "text": doc.text,
            "score": score,
            "triad": {
                "delta": doc.triad.delta,
                "infinity": doc.triad.infinity,
                "theta": doc.triad.theta,
            }
        }
        for doc, score in results
    ]
```

---

## 📞 Support

For issues or questions:
1. Check the examples
2. Review the test cases
3. Consult the API reference
4. Check the architecture diagram

---

**Version**: 1.0  
**Last Updated**: 2024-11-16  
**Status**: Production Ready ✅
