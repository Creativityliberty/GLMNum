# API Reference - Aura Model 1

**Document:** Référence API Complète  
**Projet:** Aura Model 1 GLM  
**Version:** 1.0.0  
**Base URL:** `http://localhost:5000/api`

---

## 🔌 Endpoints

### Query Processing

#### `POST /api/query`

Traite une requête utilisateur à travers le pipeline RRLA complet.

**URL:** `/api/query`  
**Method:** `POST`  
**Content-Type:** `application/json`

**Request Body:**
```json
{
    "query": "string (required)"
}
```

**Response Success (200 OK):**
```json
{
    "query": "string",
    "response": "string",
    "reasoning_trace": [
        {
            "phase": "clarification|visualisation|exploration|structuration|immersion|validation|integration",
            "agent": "string",
            "output": {
                "agent": "string",
                "clarity": "integer (1-5)",
                "friction": "integer (1-5)",
                "...": "phase-specific fields"
            }
        }
    ],
    "duration": "float (seconds)",
    "phases_completed": "integer"
}
```

**Response Error (400 Bad Request):**
```json
{
    "error": "Query is required"
}
```

**Response Error (500 Internal Server Error):**
```json
{
    "error": "string (error message)"
}
```

**Example Usage (cURL):**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explique-moi l'\''intelligence artificielle"}'
```

**Example Usage (Python):**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/query',
    json={'query': 'Explique-moi l\'intelligence artificielle'}
)

data = response.json()
print(f"Réponse: {data['response']}")
print(f"Phases: {data['phases_completed']}")
print(f"Durée: {data['duration']:.2f}s")
```

**Example Usage (JavaScript):**
```javascript
fetch('http://localhost:5000/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'Explique-moi l\'IA'})
})
.then(res => res.json())
.then(data => {
    console.log('Réponse:', data.response);
    console.log('Phases:', data.phases_completed);
});
```

---

### History Management

#### `GET /api/history`

Récupère l'historique complet des requêtes traitées.

**URL:** `/api/history`  
**Method:** `GET`

**Response Success (200 OK):**
```json
{
    "history": [
        {
            "query": "string",
            "reasoning_trace": [...],
            "duration": "float",
            "timestamp": "ISO8601 string"
        }
    ]
}
```

**Response Error (500 Internal Server Error):**
```json
{
    "error": "string"
}
```

**Example Usage (cURL):**
```bash
curl http://localhost:5000/api/history
```

**Example Usage (Python):**
```python
import requests

response = requests.get('http://localhost:5000/api/history')
history = response.json()['history']

print(f"Total requêtes: {len(history)}")
for i, item in enumerate(history[-5:], 1):
    print(f"{i}. {item['query']} ({item['duration']:.2f}s)")
```

---

### Memory State

#### `GET /api/memory`

Retourne l'état actuel du système de mémoire tri-niveau.

**URL:** `/api/memory`  
**Method:** `GET`

**Response Success (200 OK):**
```json
{
    "working_memory": {
        "key": "value",
        "...": "..."
    },
    "episodic_count": "integer",
    "semantic_concepts": ["string", "string", ...]
}
```

**Response Error (500 Internal Server Error):**
```json
{
    "error": "string"
}
```

**Example Usage (cURL):**
```bash
curl http://localhost:5000/api/memory
```

**Example Usage (Python):**
```python
import requests

response = requests.get('http://localhost:5000/api/memory')
memory = response.json()

print(f"Mémoire de travail: {len(memory['working_memory'])} items")
print(f"Épisodes stockés: {memory['episodic_count']}")
print(f"Concepts: {', '.join(memory['semantic_concepts'])}")
```

---

### Health Check

#### `GET /api/health`

Vérifie l'état de santé du système.

**URL:** `/api/health`  
**Method:** `GET`

**Response Success (200 OK):**
```json
{
    "status": "healthy",
    "model": "Aura Model 1",
    "owner": "Nümtema AGENCY",
    "contact": "numtemalionel@gmail.com"
}
```

**Example Usage (cURL):**
```bash
curl http://localhost:5000/api/health
```

**Example Usage (Python):**
```python
import requests

response = requests.get('http://localhost:5000/api/health')
health = response.json()

if health['status'] == 'healthy':
    print(f"✅ {health['model']} est opérationnel")
else:
    print("❌ Système en erreur")
```

---

## 📋 Data Models

### Query Object
```typescript
interface Query {
    query: string;  // Requête utilisateur (max 10000 chars)
}
```

### Response Object
```typescript
interface QueryResponse {
    query: string;
    response: string;
    reasoning_trace: ReasoningStep[];
    duration: number;  // En secondes
    phases_completed: number;  // 0-7
}
```

### Reasoning Step
```typescript
interface ReasoningStep {
    phase: 'clarification' | 'visualisation' | 'exploration' | 
           'structuration' | 'immersion' | 'validation' | 'integration';
    agent: string;
    output: {
        agent: string;
        clarity: number;  // 1-5
        friction: number;  // 1-5
        [key: string]: any;  // Phase-specific fields
    };
}
```

### Memory State
```typescript
interface MemoryState {
    working_memory: Record<string, any>;
    episodic_count: number;
    semantic_concepts: string[];
}
```

### History Item
```typescript
interface HistoryItem {
    query: string;
    reasoning_trace: ReasoningStep[];
    duration: number;
    timestamp: string;  // ISO8601
}
```

---

## 🔄 RRLA Pipeline Flow