# Gemini Triad-Aware QA System Guide
## Complete LLM Orchestration Pipeline

---

## 📋 Overview

The **GeminiTriadWrapper** orchestrates a complete QA pipeline:

1. **NumTriadEmbeddingV3**: Encodes questions with semantic embeddings + triad scores
2. **DeepTriadRAGIndex**: Retrieves documents with triad-aware ranking
3. **GeminiTriadWrapper**: Builds triad-guided prompts for Gemini 2.0 Flash
4. **Gemini 2.0 Flash**: Generates calibrated responses

---

## 🏗️ Architecture

```
User Question
    ↓
NumTriadEmbeddingV3
├─ Chunk text
├─ Encode chunks
├─ Predict triad
└─ Return enriched embedding + triad
    ↓
DeepTriadRAGIndex.search()
├─ Compute cosine similarity
├─ Compute triad distance
├─ Combine scores
└─ Return top-k documents
    ↓
GeminiTriadWrapper
├─ Build system prompt (triad rules)
├─ Build user prompt (question + docs + triad)
├─ Map triad to style
└─ Return structured result
    ↓
Gemini 2.0 Flash
├─ Receive triad-aware prompts
├─ Generate calibrated response
└─ Return answer text
    ↓
Structured Result
├─ answer: Generated response
├─ triad_question: Question triad
├─ style: Detected style
├─ documents: Retrieved docs
└─ metadata: Additional info
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install google-generative-ai (optional, for real Gemini)
pip install google-generative-ai
```

### 2. Configuration

```python
from numtriad.config import NumTriadConfig
from numtriad.encoders.numtriad_v3 import NumTriadV3Config
from numtriad.llm.gemini_triad_wrapper import GeminiTriadWrapper, GeminiConfig

# Base config
cfg = NumTriadConfig(device="cpu")

# V3 config
v3_cfg = NumTriadV3Config(
    deeptriad_ckpt="checkpoints/deeptriad_transformer_v1.pt",
    max_len=16,
)

# Gemini config
gemini_cfg = GeminiConfig(
    model_name="gemini-2.0-flash",
    max_output_tokens=1024,
    temperature=0.3,
)
```

### 3. Create Index & Wrapper

```python
from numtriad.rag.deeptriad_rag import DeepTriadRAGIndex

# Create RAG index
index = DeepTriadRAGIndex(cfg, v3_cfg)

# Add documents
documents = [
    "Document 1 text...",
    "Document 2 text...",
    "Document 3 text...",
]
index.add_documents(documents)

# Create wrapper
wrapper = GeminiTriadWrapper(
    rag_index=index,
    gemini_client=None,  # Set to real client if available
    gemini_cfg=gemini_cfg,
)
```

### 4. Query

```python
# Concrete query
result = wrapper.answer(
    query="How to deploy in production?",
    k=5,
    triad_target_mode="concrete",
)

print(result["answer"])
print(result["style"])
print(result["triad_question"])
```

---

## 🎯 Triad Target Modes

| Mode | Effect | Use Case |
|------|--------|----------|
| `auto` | Natural triad prediction | General queries |
| `abstract` | Boost ∞, reduce Θ | Theoretical questions |
| `concrete` | Boost Θ, reduce ∞ | Practical questions |
| `balanced` | Equilibrate to (1/3, 1/3, 1/3) | Mixed queries |

---

## 🎨 Style Detection

The wrapper automatically maps triads to response styles:

### Concrete (Θ dominant)
- **Characteristics**: Practical, operational, with examples
- **Use Case**: "How to deploy?", "What are the steps?"
- **Example**: Step-by-step instructions, code examples, case studies

### Abstract (∞ dominant)
- **Characteristics**: Theoretical, conceptual, linking to principles
- **Use Case**: "What is AGI?", "Define intelligence"
- **Example**: Theoretical frameworks, philosophical discussion, general concepts

### Structural (Δ dominant)
- **Characteristics**: Analytical, structured, logical breakdown
- **Use Case**: "How does algorithm X work?", "Explain the architecture"
- **Example**: Algorithmic steps, system architecture, logical decomposition

---

## 📊 System Prompt

The wrapper builds a system prompt that encodes triad rules:

```
Tu es un assistant de raisonnement transformationnel basé sur ∆∞Θ.

Règles de style :
- Si Θ est dominant : sois concret, opérationnel, donne des exemples, des étapes, du code
- Si ∞ est dominante : sois plutôt conceptuel, relie aux théories ou principes généraux
- Si Δ est dominante : structure la réponse en étapes logiques, algorithmiques ou méthodologiques

Directives :
- Ne répète pas la triade, utilise-la pour calibrer ton ton, ta profondeur et tes exemples
- Appuie-toi sur les documents fournis, mais synthétise et reformule
- Sois concis mais complet
```

---

## 📝 User Prompt Format

The wrapper builds a structured user prompt:

```
### QUESTION
[User question]

### TRIADE QUESTION
Δ=0.21, ∞=0.55, Θ=0.24
Style recommandé (interne): abstract
Description: Theoretical, conceptual, linking to general principles

### DOCUMENTS DE CONTEXTE
[DOC 1] score=0.89, triade=Δ=0.18, ∞=0.62, Θ=0.20
[Texte du document...]

[DOC 2] score=0.85, triade=Δ=0.30, ∞=0.40, Θ=0.30
[Texte du document...]

### TÂCHE
Réponds à la question en t'appuyant sur les documents ci-dessus,
en respectant le niveau d'abstraction implicite de la triade.
```

---

## 🔧 API Reference

### GeminiTriadWrapper

```python
class GeminiTriadWrapper:
    def __init__(
        rag_index: DeepTriadRAGIndex,
        gemini_client: Optional[Any] = None,
        gemini_cfg: Optional[GeminiConfig] = None,
    )
    
    def answer(
        query: str,
        k: int = 5,
        triad_target_mode: str = "auto",
    ) -> Dict[str, Any]
        # Returns: {
        #     "answer": str,
        #     "triad_question": Dict,
        #     "style": str,
        #     "documents": List[Dict],
        #     "metadata": Dict,
        # }
    
    def get_stats() -> Dict[str, Any]
```

### GeminiConfig

```python
@dataclass
class GeminiConfig:
    model_name: str = "gemini-2.0-flash"
    max_output_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.95
    top_k: int = 40
```

### Utility Functions

```python
def triad_to_style(triad: Triad) -> str
    # Returns: "concrete", "abstract", or "structural"

def format_triad(triad: Triad) -> str
    # Returns: "Δ=0.21, ∞=0.55, Θ=0.24"

def style_to_description(style: str) -> str
    # Returns: Human-readable description
```

---

## 💡 Usage Examples

### Example 1: Concrete Query

```python
result = wrapper.answer(
    query="How to deploy a FastAPI application in production?",
    k=5,
    triad_target_mode="concrete",
)

# Result will emphasize:
# - Step-by-step instructions
# - Code examples
# - Configuration details
# - Practical considerations
```

### Example 2: Abstract Query

```python
result = wrapper.answer(
    query="What is artificial general intelligence?",
    k=5,
    triad_target_mode="abstract",
)

# Result will emphasize:
# - Theoretical frameworks
# - Conceptual definitions
# - Philosophical implications
# - General principles
```

### Example 3: Structural Query

```python
result = wrapper.answer(
    query="How does a transformer neural network work?",
    k=5,
    triad_target_mode="balanced",
)

# Result will emphasize:
# - Logical breakdown
# - Algorithmic steps
# - Component relationships
# - System architecture
```

### Example 4: Batch Processing

```python
queries = [
    "How to use Docker?",
    "What is machine learning?",
    "Explain neural networks",
]

results = [
    wrapper.answer(q, k=5, triad_target_mode="auto")
    for q in queries
]

for q, r in zip(queries, results):
    print(f"Q: {q}")
    print(f"Style: {r['style']}")
    print(f"Answer: {r['answer']}\n")
```

---

## 🔌 Gemini Integration

### With Real Gemini API

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key="YOUR_API_KEY")

# Create client
gemini_client = genai.GenerativeModel("gemini-2.0-flash")

# Create wrapper
wrapper = GeminiTriadWrapper(
    rag_index=index,
    gemini_client=gemini_client,
    gemini_cfg=GeminiConfig(),
)

# Query
result = wrapper.answer("Your question here")
```

### Fallback Mode (No Gemini)

```python
# Create wrapper without Gemini
wrapper = GeminiTriadWrapper(
    rag_index=index,
    gemini_client=None,  # No Gemini
    gemini_cfg=GeminiConfig(),
)

# Query - will use fallback generation
result = wrapper.answer("Your question here")
```

---

## 📊 Output Structure

```python
{
    "answer": "Generated response text...",
    
    "triad_question": {
        "delta": 0.21,
        "infinity": 0.55,
        "theta": 0.24,
    },
    
    "style": "abstract",
    
    "documents": [
        {
            "id": "doc_1",
            "text": "Document excerpt...",
            "score": 0.89,
            "triad": {
                "delta": 0.18,
                "infinity": 0.62,
                "theta": 0.20,
            },
            "meta": {"type": "theory", "domain": "AI"},
        },
        # ... more documents
    ],
    
    "metadata": {
        "num_documents": 5,
        "retrieval_mode": "triad_weighted",
        "triad_target_mode": "auto",
    },
}
```

---

## 🧪 Testing

Run the example:
```bash
python examples/gemini_triad_example.py
```

Run tests:
```bash
python test_gemini_triad_wrapper.py
```

---

## ⚙️ Configuration Options

### Adjust Retrieval

```python
index = DeepTriadRAGIndex(
    base_config=cfg,
    v3_config=v3_cfg,
    retrieval_mode="triad_weighted",  # or "cosine"
    triad_weight=0.3,  # Adjust triad influence
)
```

### Adjust Generation

```python
gemini_cfg = GeminiConfig(
    model_name="gemini-2.0-flash",
    max_output_tokens=2048,  # Longer responses
    temperature=0.5,  # More creative
    top_p=0.9,
    top_k=40,
)
```

### Adjust Encoding

```python
v3_cfg = NumTriadV3Config(
    deeptriad_ckpt="...",
    max_len=32,  # Longer sequences
    triad_alpha=1.5,  # Amplify triad in embedding
)
```

---

## 🎓 Learning Path

1. **Start**: Run `examples/gemini_triad_example.py`
2. **Understand**: Read this guide
3. **Experiment**: Try different `triad_target_mode` values
4. **Optimize**: Tune configuration parameters
5. **Deploy**: Integrate into your application

---

## 🚀 Production Deployment

```python
# 1. Pre-index documents
index = DeepTriadRAGIndex(cfg, v3_cfg)
with open("documents.jsonl") as f:
    for line in f:
        doc = json.loads(line)
        index.add_documents([doc["text"]], metadatas=[doc.get("meta", {})])

# 2. Create wrapper
wrapper = GeminiTriadWrapper(
    rag_index=index,
    gemini_client=gemini_client,
    gemini_cfg=GeminiConfig(),
)

# 3. Expose via API
@app.post("/ask")
def ask(query: str, mode: str = "auto"):
    result = wrapper.answer(query, triad_target_mode=mode)
    return result
```

---

## 📞 Support

For questions or issues:
1. Check the examples
2. Review the test cases
3. Consult the API reference
4. Check the architecture diagram

---

**Version**: 1.0  
**Status**: Production Ready ✅  
**Last Updated**: 2024-11-16
