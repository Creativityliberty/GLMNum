# ∆∞Ο Embedding System - Guide d'Implémentation

## 📚 Table des Matières

1. [Architecture du Système](#architecture-du-système)
2. [Module Principal ∆∞Ο](#module-principal-∆∞ο)
3. [Intégration des Domaines](#intégration-des-domaines)
4. [API REST](#api-rest)
5. [Interface Web](#interface-web)
6. [Tests et Validation](#tests-et-validation)
7. [Extensibilité](#extensibilité)

---

## 🏗️ Architecture du Système

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    GLM v3.0 ∆∞Ο System                      │
├─────────────────────────────────────────────────────────────┤
│  SymbolicEngine                                            │
│  ├── Domain Registry                                        │
│  ├── Transformation Pipeline                                │
│  ├── Cache Management                                       │
│  └── Statistics Tracking                                    │
├─────────────────────────────────────────────────────────────┤
│  Domains (Text, Code, Geometry, Image)                     │
│  ├── encode() + ∆∞Ó enhancement                            │
│  ├── decode()                                               │
│  └── metadata with triadic scores                           │
├─────────────────────────────────────────────────────────────┤
│  ∆∞Ó Core Module                                            │
│  ├── DeltaOmegaThetaComputer                                │
│  ├── Heuristic Scoring Functions                            │
│  └── Distance Calculations                                  │
├─────────────────────────────────────────────────────────────┤
│  Interfaces                                                 │
│  ├── REST API (FastAPI)                                     │
│  ├── Web UI (HTML/JS/CSS)                                   │
│  └── Python API                                            │
└─────────────────────────────────────────────────────────────┘
```

### Flux de Données

1. **Input** → Domain.encode() → **SymbolicRepresentation + ∆∞Ó scores**
2. **Transformation** → SymbolicEngine.transform_with_symbolic() → **Result + metadata**
3. **Output** → Web UI/API → **Visualisation + JSON response**

---

## 🧮 Module Principal ∆∞Ó

### Fichier : `delta_infty_omicron.py`

#### Classes Principales

```python
@dataclass
class DeltaOmegaThetaScores:
    """Triadic embedding scores for conceptual analysis."""
    delta: float    # ∆ - complexity/granularity (0-1)
    omega: float    # ∞ - generality/transformability (0-1)
    theta: float    # Ο - concreteness/spatiality (0-1)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for metadata storage."""
        return {
            "delta_score": self.delta,
            "omega_score": self.omega, 
            "theta_score": self.theta
        }
```

#### Computer Class

```python
class DeltaOmegaThetaComputer:
    """Computes ∆∞Ó scores using minimal heuristics."""
    
    # Termes pour scoring
    GENERAL_TERMS = {
        "intelligence", "énergie", "temps", "espace", "valeur", "système",
        "information", "relation", "transformation", "concept", "abstraction"
    }
    
    CONCRETE_TERMS = {
        "machine", "capteur", "bâtiment", "voiture", "ordinateur", "serveur",
        "ville", "robot", "kg", "mètre", "euro", "usd", "donnée", "code"
    }
    
    LOGIC_CONNECTORS = {
        "donc", "tandis", "cependant", "néanmoins", "pourtant",
        "ainsi", "mais", "alors", "parce", "car", "si", "alors"
    }
```

#### Fonctions de Scoring

```python
@staticmethod
def compute_delta(text: str) -> float:
    """
    ∆: Complexity score based on length, sentences, and logic.
    """
    tokens = DeltaOmegaThetaComputer.tokenize(text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    
    # Indicateurs de complexité
    n_tokens = len(tokens)
    n_sentences = len(sentences)
    n_connectors = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.LOGIC_CONNECTORS)
    
    # Normalisation vers [0,1]
    raw = (n_tokens / 50.0) + (n_sentences / 5.0) + (n_connectors / 5.0)
    return float(min(1.0, raw))

@staticmethod  
def compute_omega(text: str) -> float:
    """
    ∞: Generality score based on abstract terms.
    """
    tokens = DeltaOmegaThetaComputer.tokenize(text)
    if not tokens:
        return 0.0
    
    general_hits = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.GENERAL_TERMS)
    ratio = general_hits / len(tokens)
    
    # Étirement: 10% termes généraux = forte généralité
    stretched = ratio * 10.0
    return float(min(1.0, stretched))

@staticmethod
def compute_theta(text: str) -> float:
    """
    Ο: Concreteness score based on numbers and concrete terms.
    """
    tokens = DeltaOmegaThetaComputer.tokenize(text)
    
    # Nombres et termes concrets
    n_numbers = sum(1 for t in tokens if re.match(r"^\d+([.,]\d+)?$", t))
    concrete_hits = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.CONCRETE_TERMS)
    
    raw = (n_numbers / 5.0) + (concrete_hits / 5.0)
    return float(min(1.0, raw))
```

---

## 🔧 Intégration des Domaines

### Pattern d'Intégration

Chaque domaine suit le même pattern d'intégration :

```python
# 1. Import du module ∆∞Ó
from delta_infty_omicron import enhance_symbolic_metadata

# 2. Dans la méthode encode()
def encode(self, obj: Any) -> SymbolicRepresentation:
    # ... calcul existant de delta, infinity, omega ...
    
    # Base metadata avec ∆∞Ó scores
    base_metadata = {
        'domain': self.name,
        # ... autres métadonnées spécifiques au domaine
    }
    
    # Créer représentation textuelle pour scoring
    text_representation = self._extract_text_for_scoring(obj)
    
    # Enhancer avec scores ∆∞Ó
    enhanced_metadata = enhance_symbolic_metadata(base_metadata, text_representation)
    
    return SymbolicRepresentation(
        delta=delta,
        infinity=infinity,
        omega=omega,
        metadata=enhanced_metadata
    )
```

### TextDomain

```python
# Spécificités:
# - Utilise le texte directement pour scoring
# - Ajoute métadonnées: length, words, text_preview

text_representation = text  # Utilisation directe
```

### CodeDomain

```python
# Spécificités:
# - Analyse AST Python pour extraire features
# - Ajoute métadonnées: lines, num_functions, num_classes

text_representation = code  # Code source comme texte
```

### GeometricDomain

```python
# Spécificités:
# - Convertit forme géométrique en description textuelle
# - Ajoute métadonnées: sides, radius, type

geom_text = f"{base_metadata['type']} with {obj.sides} sides and radius {obj.radius}"
```

### ImageDomain

```python
# Spécificités:
# - Génère description depuis features visuelles
# - Ajoute métadonnées: height, width, colors, shapes, objects

image_text = f"Image with {len(objects)} objects, colors: {colors[:3]}, shapes: {shapes[:3]}"
```

---

## 🌐 API REST

### Fichier : `api.py`

#### Endpoints Principaux

```python
@app.post("/transform")
async def transform_content(request: TransformRequest):
    """
    Transformation entre domaines avec scores ∆∞Ó
    """
    result = engine.transform_with_symbolic(
        request.content,
        request.source_domain,
        request.target_domain
    )
    return result

@app.post("/similarity")
async def calculate_similarity(request: SimilarityRequest):
    """
    Calcul de similarité ∆∞Ó
    """
    similarity = engine.similarity(
        request.content1,
        request.content2,
        request.domain
    )
    return {"similarity": similarity}

@app.post("/analyze")
async def analyze_content(request: AnalyzeRequest):
    """
    Analyse symbolique complète avec scores ∆∞Ó
    """
    symbolic = engine.abstract(request.content, request.domain)
    return {
        "symbolic": engine._symbolic_to_dict(symbolic),
        "dio_scores": {
            "delta": symbolic.metadata.get("delta_score", 0),
            "omega": symbolic.metadata.get("omega_score", 0),
            "theta": symbolic.metadata.get("theta_score", 0)
        }
    }
```

#### Models Pydantic

```python
class TransformRequest(BaseModel):
    content: str
    source_domain: str
    target_domain: str

class SimilarityRequest(BaseModel):
    content1: str
    content2: str
    domain: str

class AnalyzeRequest(BaseModel):
    content: str
    domain: str
```

---

## 🎨 Interface Web

### Structure des Fichiers

```
web_ui/
├── index.html          # Structure principale (Transform + Chat modes)
├── style.css          # Styles avec visualisation ∆∞Ó
└── app.js             # Logique JavaScript
```

### Mode Transform

#### HTML Structure
```html
<div class="mode-tabs">
    <button class="tab-button active" onclick="switchMode('transform')">Transform Mode</button>
    <button class="tab-button" onclick="switchMode('chat')">Chat Mode</button>
</div>

<div id="transformMode" class="mode-content">
    <!-- Sélecteurs de domaines, input/output, visualisation ∆∞Ó -->
</div>
```

#### JavaScript Integration
```javascript
function displayTransformResult(data) {
    // Extraire scores ∆∞Ó
    const deltaScore = data.source_symbolic.metadata.delta_score || 0;
    const omegaScore = data.source_symbolic.metadata.omega_score || 0;
    const thetaScore = data.source_symbolic.metadata.theta_score || 0;
    
    // Visualiser avec barres de progression
    symbolicInfo.innerHTML = `
        <div class="dio-scores">
            <div class="dio-score">
                <span class="dio-label">∆ Complexity:</span>
                <div class="dio-bar">
                    <div class="dio-fill" style="width: ${deltaScore * 100}%"></div>
                    <span class="dio-value">${(deltaScore * 100).toFixed(1)}%</span>
                </div>
            </div>
            <!-- ... autres scores ... -->
        </div>
    `;
}
```

### Mode Chat

#### Commandes Supportées
```javascript
// Transform command
transform 'text' from domain1 to domain2

// Similarity command  
similarity 'text1' vs 'text2' in domain

// Analyze command
analyze 'text' in domain

// System commands
help, clear, list domains
```

---

## 🧪 Tests et Validation

### Structure des Tests

```
tests/
├── test_delta_infty_omicron.py    # Tests du module principal
├── test_domains.py                # Tests d'intégration domaines
├── test_api.py                    # Tests API REST
└── test_integration.py            # Tests end-to-end
```

### Tests Unitaires ∆∞Ó

```python
def test_dio_scoring():
    """Test basic ∆∞Ó scoring functionality."""
    from delta_infty_omicron import compute_dio_scores
    
    # Test texte abstrait
    abstract_text = "L'intelligence transforme les concepts théoriques"
    scores = compute_dio_scores(abstract_text)
    
    assert 0 <= scores.delta <= 1
    assert 0 <= scores.omega <= 1  
    assert 0 <= scores.theta <= 1
    assert scores.omega > scores.theta  # Plus abstrait que concret

def test_dio_distance():
    """Test ∆∞Ó distance calculation."""
    from delta_infty_omicron import DeltaOmegaThetaScores
    
    scores1 = DeltaOmegaThetaScores(0.8, 0.9, 0.2)
    scores2 = DeltaOmegaThetaScores(0.3, 0.4, 0.7)
    
    distance = scores1.distance(scores2)
    assert distance > 0
    assert isinstance(distance, float)
```

### Tests d'Intégration Domaines

```python
def test_text_domain_dio_integration():
    """Test TextDomain ∆∞Ó integration."""
    from domains.text import TextDomain
    
    domain = TextDomain()
    result = domain.encode("Test text for scoring")
    
    # Vérifier présence des scores ∆∞Ó
    assert "delta_score" in result.metadata
    assert "omega_score" in result.metadata
    assert "theta_score" in result.metadata
    
    # Vérifier valeurs valides
    assert all(0 <= result.metadata[key] <= 1 for key in ["delta_score", "omega_score", "theta_score"])
```

### Tests API

```python
def test_transform_endpoint_with_dio():
    """Test /transform endpoint includes ∆∞Ó scores."""
    response = client.post("/transform", json={
        "content": "Test transformation",
        "source_domain": "text", 
        "target_domain": "code"
    })
    
    data = response.json()
    assert "source_symbolic" in data
    assert "target_symbolic" in data
    
    # Vérifier scores ∆∞Ó présents
    source_meta = data["source_symbolic"]["metadata"]
    assert "delta_score" in source_meta
    assert "omega_score" in source_meta
    assert "theta_score" in source_meta
```

---

## 🔧 Extensibilité

### Ajouter un Nouveau Domaine

1. **Créer la classe de domaine** :
```python
class NewDomain(Domain):
    @property
    def name(self) -> str:
        return "new_domain"
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        # ... implémentation spécifique ...
        
        # Intégration ∆∞Ó
        base_metadata = {'domain': self.name, ...}
        text_repr = self._extract_text_representation(obj)
        enhanced_metadata = enhance_symbolic_metadata(base_metadata, text_repr)
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=enhanced_metadata
        )
```

2. **Enregistrer le domaine** :
```python
engine.register_domain(NewDomain())
```

3. **Ajouter les tests** :
```python
def test_new_domain_dio_integration():
    domain = NewDomain()
    result = domain.encode(test_input)
    assert "delta_score" in result.metadata
```

### Améliorer les Heuristiques

1. **Ajouter de nouveaux termes** :
```python
GENERAL_TERMS.update({"nouveau_terme_abstrait", "autre_concept"})
CONCRETE_TERMS.update({"nouveau_terme_concret", "objet_spécifique"})
```

2. **Modifier les fonctions de scoring** :
```python
@staticmethod
def compute_delta_enhanced(text: str) -> float:
    # Utiliser NLP avancé, structures syntaxiques, etc.
    pass
```

3. **Ajouter pondération par domaine** :
```python
def compute_dio_scores_domain_aware(text: str, domain: str) -> DeltaOmegaThetaScores:
    # Adapter les heuristiques selon le domaine
    pass
```

### Intégration Apprentissage Automatique

```python
class NeuralDeltaOmegaThetaComputer:
    """Version neuronale du calculateur ∆∞Ó."""
    
    def __init__(self, model_path: str = None):
        self.model = self._load_or_create_model(model_path)
    
    def compute_scores(self, text: str) -> DeltaOmegaThetaScores:
        # Utiliser modèle neuronal entraîné
        embedding = self._encode_text(text)
        scores = self.model.predict(embedding)
        return DeltaOmegaThetaScores(*scores)
```

---

## 📊 Monitoring et Performance

### Métriques à Suivre

1. **Performance des scores** :
   - Distribution des scores par domaine
   - Corrélation avec évaluations humaines
   - Temps de calcul par transformation

2. **Usage du système** :
   - Nombre de transformations par domaine
   - Taux de cache hits
   - Popularité des commandes chat

3. **Qualité des résultats** :
   - Feedback utilisateur
   - Tests A/B avec/sans ∆∞Ó
   - Benchmarks de similarité

### Logging Structuré

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_transformation_with_dio(source_text, target_domain, dio_scores, performance_ms):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "source_length": len(source_text),
        "target_domain": target_domain,
        "dio_scores": dio_scores,
        "performance_ms": performance_ms
    }
    logger.info(json.dumps(log_data))
```

---

## 🚀 Déploiement

### Configuration Production

```python
# config.py
class Config:
    # API
    API_HOST = "0.0.0.0"
    API_PORT = 8001
    
    # ∆∞Ó
    DIO_MODEL_TYPE = "heuristic"  # ou "neural"
    DIO_CACHE_SIZE = 1000
    
    # Performance
    ENABLE_CACHING = True
    MAX_CONTENT_LENGTH = 10000
```

### Dockerisation

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

**Ce guide d'implémentation couvre l'architecture technique complète du système ∆∞Ó dans GLM v3.0.** 🔧
