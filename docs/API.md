# GLM v3.0 ∆∞Ο System - Référence API

## 📚 Table des Matières

1. [API REST](#api-rest)
2. [API Python](#api-python)
3. [Web UI](#web-ui)
4. [Exemples d'Utilisation](#exemples-dutilisation)
5. [Codes d'Erreur](#codes-derreur)
6. [Performance et Limites](#performance-et-limites)

---

## 🌐 API REST

### Démarrage du Serveur

```bash
cd /Volumes/Numtema/Ava\ agent/GLM/glm_prototype
source .venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

### Documentation Interactive

Accédez à `http://localhost:8001/docs` pour l'interface Swagger interactive.

### Endpoints Principaux

#### `/transform` - Transformation entre Domaines

**POST** `/transform`

Transforme du contenu d'un domaine source vers un domaine cible avec scores ∆∞Ó.

```json
{
  "content": "L'intelligence artificielle transforme les données",
  "source_domain": "text",
  "target_domain": "code"
}
```

**Réponse** :
```json
{
  "result": "# Code reconstructed from symbolic representation\ndef hello_world():\n    return \"Hello, World!\"",
  "source_symbolic": {
    "delta_norm": 0.1234,
    "infinity_nodes": 5,
    "infinity_edges": 4,
    "omega_norm": 0.5678,
    "metadata": {
      "delta_score": 0.48,
      "omega_score": 1.0,
      "theta_score": 0.2,
      "domain": "text",
      "length": 8,
      "words": 8
    }
  },
  "target_symbolic": {
    "delta_norm": 0.2345,
    "infinity_nodes": 3,
    "infinity_edges": 2,
    "omega_norm": 0.3456,
    "metadata": {
      "delta_score": 1.0,
      "omega_score": 0.6,
      "theta_score": 0.8,
      "domain": "code",
      "lines": 6,
      "num_functions": 2
    }
  }
}
```

#### `/similarity` - Calcul de Similarité ∆∞Ó

**POST** `/similarity`

Calcule la similarité entre deux contenus dans un domaine spécifique.

```json
{
  "content1": "intelligence artificielle",
  "content2": "machine learning", 
  "domain": "text"
}
```

**Réponse** :
```json
{
  "similarity": 0.75,
  "content1_symbolic": {
    "delta_norm": 0.1234,
    "infinity_nodes": 3,
    "infinity_edges": 2,
    "omega_norm": 0.5678,
    "metadata": {
      "delta_score": 0.6,
      "omega_score": 0.9,
      "theta_score": 0.1
    }
  },
  "content2_symbolic": {
    "delta_norm": 0.2345,
    "infinity_nodes": 4,
    "infinity_edges": 3,
    "omega_norm": 0.6789,
    "metadata": {
      "delta_score": 0.7,
      "omega_score": 0.8,
      "theta_score": 0.3
    }
  }
}
```

#### `/analyze` - Analyse Symbolique Complète

**POST** `/analyze`

Analyse un contenu et retourne la représentation symbolique complète avec scores ∆∞Ó.

```json
{
  "content": "Le robot utilise des capteurs pour naviguer",
  "domain": "text"
}
```

**Réponse** :
```json
{
  "symbolic": {
    "delta_norm": 0.1234,
    "infinity_nodes": 6,
    "infinity_edges": 5,
    "omega_norm": 0.5678,
    "metadata": {
      "delta_score": 0.65,
      "omega_score": 0.3,
      "theta_score": 0.8,
      "domain": "text",
      "length": 9,
      "words": 9
    }
  },
  "dio_scores": {
    "delta": 0.65,
    "omega": 0.3,
    "theta": 0.8
  },
  "interpretation": {
    "complexity": "Élevée",
    "generality": "Faible", 
    "concreteness": "Élevée",
    "type": "Concept concret complexe"
  }
}
```

#### `/domains` - Liste des Domaines

**GET** `/domains`

Retourne la liste des domaines disponibles et leurs caractéristiques.

**Réponse** :
```json
{
  "domains": [
    {
      "name": "text",
      "description": "Domaine textuel avec analyse sémantique",
      "supported_inputs": ["string"],
      "dio_features": ["complexity_analysis", "generality_scoring", "concreteness_detection"]
    },
    {
      "name": "code",
      "description": "Domaine code Python avec analyse AST",
      "supported_inputs": ["python_code_string"],
      "dio_features": ["ast_complexity", "function_analysis", "structure_scoring"]
    },
    {
      "name": "geometry", 
      "description": "Domaine géométrique (formes 2D)",
      "supported_inputs": ["string", "Polygon", "Circle"],
      "dio_features": ["shape_complexity", "geometric_abstraction"]
    },
    {
      "name": "image",
      "description": "Domaine image avec features visuelles",
      "supported_inputs": ["image_path", "numpy_array", "PIL_Image"],
      "dio_features": ["visual_complexity", "object_detection", "spatial_analysis"]
    }
  ],
  "total_domains": 4
}
```

#### `/stats` - Statistiques du Système

**GET** `/stats`

Retourne les statistiques d'utilisation et de performance du système.

**Réponse** :
```json
{
  "stats": {
    "total_transformations": 1250,
    "cache_hits": 890,
    "cache_hit_rate": 0.712,
    "domain_count": 4,
    "cache_size": 450,
    "avg_transformation_time_ms": 45.2,
    "domains_usage": {
      "text": 520,
      "code": 380,
      "geometry": 200,
      "image": 150
    },
    "dio_score_distribution": {
      "delta_mean": 0.52,
      "omega_mean": 0.48,
      "theta_mean": 0.45,
      "delta_std": 0.23,
      "omega_std": 0.31,
      "theta_std": 0.28
    }
  }
}
```

---

## 🐍 API Python

### Import et Initialisation

```python
from core.symbolic import SymbolicEngine
from domains.text import TextDomain
from domains.code import CodeDomain
from domains.geometric import GeometricDomain
from domains.image import ImageDomain
from delta_infty_omicron import compute_dio_scores, DeltaOmegaThetaScores

# Initialisation du moteur
engine = SymbolicEngine()

# Enregistrement des domaines
engine.register_domain(TextDomain())
engine.register_domain(CodeDomain())
engine.register_domain(GeometricDomain())
engine.register_domain(ImageDomain())
```

### Méthodes Principales

#### `transform()` - Transformation Standard

```python
result = engine.transform(
    obj="L'intelligence transforme les données",
    source_domain="text",
    target_domain="code"
)

print(result)
# Output: Code Python généré
```

#### `transform_with_symbolic()` - Transformation avec Métadonnées ∆∞Ó

```python
result = engine.transform_with_symbolic(
    obj="L'intelligence transforme les données",
    source_domain="text", 
    target_domain="code"
)

# Accès aux résultats
print(f"Résultat: {result['result']}")
print(f"∆∞Ó source: {result['source_symbolic']['metadata']['delta_score']:.3f}")
print(f"∆∞Ó cible: {result['target_symbolic']['metadata']['delta_score']:.3f}")
```

#### `abstract()` - Abstraction Symbolique

```python
symbolic = engine.abstract("concept abstrait", "text")
print(f"Métadonnées ∆∞Ó: {symbolic.metadata}")
```

#### `concretize()` - Concrétisation

```python
concrete = engine.concretize(symbolic, "code")
print(f"Résultat concret: {concrete}")
```

#### `similarity()` - Similarité ∆∞Ó

```python
similarity = engine.similarity(
    obj1="intelligence artificielle",
    obj2="machine learning",
    domain="text"
)

print(f"Similarité: {similarity:.3f}")
```

### Module ∆∞Ó Direct

```python
# Calcul direct des scores ∆∞Ó
scores = compute_dio_scores("Texte à analyser")
print(f"∆: {scores.delta:.3f}, ∞: {scores.omega:.3f}, Ο: {scores.theta:.3f}")

# Distance entre deux ensembles de scores
scores1 = DeltaOmegaThetaScores(0.8, 0.9, 0.2)
scores2 = DeltaOmegaThetaScores(0.3, 0.4, 0.7)
distance = scores1.distance(scores2)
print(f"Distance ∆∞Ó: {distance:.3f}")
```

---

## 🌐 Web UI

### Démarrage

```bash
cd web_ui
python3 -m http.server 8081
```

Accédez à `http://localhost:8081`

### Modes d'Interface

#### Transform Mode
- **Sélecteurs de domaines** : Choisissez source et cible
- **Zone de saisie** : Entrez votre contenu
- **Visualisation ∆∞Ó** : Barres de progression animées
- **Métadonnées complètes** : Représentation symbolique détaillée

#### Chat Mode
- **Interface conversationnelle** : Dialogue avec le système
- **Commandes supportées** :
  ```
  transform 'texte' from domain1 to domain2
  similarity 'texte1' vs 'texte2' in domain
  analyze 'texte' in domain
  list domains
  help
  clear
  ```

### Visualisation ∆∞Ó

Les scores ∆∞Ó sont affichés avec :

- **Barres de progression** colorées et animées
- **Pourcentages** précis pour chaque dimension
- **Interprétation textuelle** (Élevé/Moyen/Faible)
- **Métadonnées JSON** complètes pour développeurs

---

## 💡 Exemples d'Utilisation

### Exemple 1 : Analyse de Concept

```python
# Analyse d'un concept abstrait
abstract_concept = "L'intelligence artificielle révolutionne la technologie"
symbolic = engine.abstract(abstract_concept, "text")

print("=== Analyse ∆∞Ó ===")
print(f"Concept: {abstract_concept}")
print(f"Complexité (∆): {symbolic.metadata['delta_score']:.3f}")
print(f"Généralité (∞): {symbolic.metadata['omega_score']:.3f}")  
print(f"Concrétude (Ο): {symbolic.metadata['theta_score']:.3f}")

# Interprétation
if symbolic.metadata['omega_score'] > 0.7:
    print("Type: Concept très abstrait")
elif symbolic.metadata['theta_score'] > 0.7:
    print("Type: Concept très concret")
else:
    print("Type: Concept intermédiaire")
```

### Exemple 2 : Transformation avec Suivi ∆∞Ó

```python
# Transformation texte → code avec suivi des scores
text = "Une fonction qui calcule la factorielle"
result = engine.transform_with_symbolic(text, "text", "code")

print("=== Transformation ∆∞Ó ===")
print(f"Texte original: {text}")
print(f"Code généré:\n{result['result']}")

print("\nÉvolution des scores ∆∞Ó:")
source = result['source_symbolic']['metadata']
target = result['target_symbolic']['metadata']

print(f"Complexité: {source['delta_score']:.3f} → {target['delta_score']:.3f}")
print(f"Généralité: {source['omega_score']:.3f} → {target['omega_score']:.3f}")
print(f"Concrétude: {source['theta_score']:.3f} → {target['theta_score']:.3f}")
```

### Exemple 3 : Clustering Conceptuel

```python
# Clustering de concepts par similarité ∆∞Ó
concepts = [
    "intelligence artificielle",
    "robot industriel", 
    "algorithme de tri",
    "capteur de température",
    "théorie de l'information",
    "base de données SQL"
]

# Analyse ∆∞Ó pour chaque concept
concept_scores = []
for concept in concepts:
    symbolic = engine.abstract(concept, "text")
    scores = symbolic.metadata
    concept_scores.append({
        'concept': concept,
        'delta': scores['delta_score'],
        'omega': scores['omega_score'],
        'theta': scores['theta_score']
    })

# Clustering simple par généralité
abstract_concepts = [c for c in concept_scores if c['omega'] > 0.7]
concrete_concepts = [c for c in concept_scores if c['theta'] > 0.7]

print("Concepts abstraits:")
for c in abstract_concepts:
    print(f"  - {c['concept']} (∞={c['omega']:.3f})")

print("\nConcepts concrets:")
for c in concrete_concepts:
    print(f"  - {c['concept']} (Ο={c['theta']:.3f})")
```

### Exemple 4 : Requête API cURL

```bash
# Transformation via API REST
curl -X POST "http://localhost:8001/transform" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Calculer la somme de deux nombres",
       "source_domain": "text",
       "target_domain": "code"
     }'

# Analyse ∆∞Ó
curl -X POST "http://localhost:8001/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Le système utilise des réseaux de neurones",
       "domain": "text"
     }'

# Similarité ∆∞Ó
curl -X POST "http://localhost:8001/similarity" \
     -H "Content-Type: application/json" \
     -d '{
       "content1": "apprentissage automatique",
       "content2": "machine learning",
       "domain": "text"
     }'
```

---

## ⚠️ Codes d'Erreur

### Erreurs Client (4xx)

#### `400 Bad Request`
```json
{
  "error": "Invalid request format",
  "details": "Missing required field: content"
}
```

#### `422 Unprocessable Entity`
```json
{
  "error": "Validation error", 
  "details": "Invalid domain: invalid_domain. Available: text, code, geometry, image"
}
```

### Erreurs Serveur (5xx)

#### `500 Internal Server Error`
```json
{
  "error": "Transformation failed",
  "details": "Unable to encode content in domain: text"
}
```

#### `503 Service Unavailable`
```json
{
  "error": "Service temporarily unavailable",
  "details": "System overload, please try again later"
}
```

### Gestion des Erreurs Python

```python
try:
    result = engine.transform_with_symbolic(content, "text", "code")
except ValueError as e:
    print(f"Erreur de validation: {e}")
except RuntimeError as e:
    print(f"Erreur de transformation: {e}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

---

## ⚡ Performance et Limites

### Limites Actuelles

#### Taille du Contenu
- **Texte**: Maximum 10,000 caractères
- **Code**: Maximum 1,000 lignes
- **Image**: Maximum 10MB (formats: PNG, JPG, WebP)

#### Performance
- **Transformation**: ~50ms (texte→code)
- **Analyse ∆∞Ó**: ~20ms (texte court)
- **Similarité**: ~15ms (deux textes)

#### Taux de Requêtes
- **API REST**: 100 requêtes/minute (par défaut)
- **Python API**: Limité par ressources locales
- **Web UI**: 1 utilisateur simultané maximum

### Recommandations

#### Pour Meilleure Performance
1. **Utiliser le cache** pour les transformations répétées
2. **Batch processing** pour analyses multiples
3. **Domain approprié** pour chaque type de contenu
4. **Contenu optimal** (ni trop court, ni trop long)

#### Monitoring
```python
# Surveillance des performances
import time

start_time = time.time()
result = engine.transform_with_symbolic(content, "text", "code")
end_time = time.time()

print(f"Transformation time: {(end_time - start_time) * 1000:.2f}ms")

# Accès aux statistiques
stats = engine.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.3f}")
print(f"Total transformations: {stats['total_transformations']}")
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Configuration API
export GLM_API_HOST=0.0.0.0
export GLM_API_PORT=8001
export GLM_API_WORKERS=4

# Configuration ∆∞Ó
export GLM_DIO_CACHE_SIZE=1000
export GLM_DIO_MODEL_TYPE=heuristic
export GLM_DIO_TIMEOUT=30

# Logging
export GLM_LOG_LEVEL=INFO
export GLM_LOG_FILE=glm.log
```

### Configuration Python

```python
# Configuration personnalisée
config = {
    'dio_weights': {
        'alpha': 0.7,  # Poids pour delta
        'beta': 0.2,   # Poids pour omega  
        'gamma': 0.1   # Poids pour theta
    },
    'cache_enabled': True,
    'cache_size': 1000,
    'timeout_seconds': 30
}

# Application de la configuration
engine.configure(config)
```

---

**Cette référence API complète couvre toutes les interfaces disponibles pour le système ∆∞Ó GLM v3.0.** 📚
