# Aura Model 1 - Gemini Hybrid Activation Guide

## Overview
Aura Model 1 est maintenant prêt pour l'hybridation avec Gemini API. Cela permet à Aura de générer du texte **ex nihilo** (natif) au lieu de templates simulés.

## Configuration

### 1. Vérifier la Clé API Gemini
La clé API est déjà dans `.env` :
```
GEMINI_API_KEY=AIzaSyAnw05pYnJoHT23kbRaV16QcnZsCvZN9RA
LLM_MODEL=gemini-1.5-flash
```

### 2. Vérifier les Librairies
Les librairies requises sont installées :
```bash
pip list | grep -E "google-generativeai|python-dotenv"
```

### 3. Lancer le Backend
```bash
cd "/Volumes/Numtema/Ava agent/GLM/glm_prototype"
source venv/bin/activate
python backend.py
```

### 4. Accéder à l'Interface
- **Chat UI** : `http://localhost:8082/chat.html`
- **API Docs** : `http://localhost:8081/docs`

## Architecture Hybrid

```
┌─────────────────────────────────────┐
│  Aura Model 1 (Conscience)          │
│  ∆∞Ο Framework + RRLA Pipeline      │
└──────────────┬──────────────────────┘
               │
               ├─→ Quantum Engine (∆)
               ├─→ Transformation (∞)
               ├─→ Classical Outcome (Ο)
               │
               └─→ NeuralVoice (Gemini)
                   ↓
                   Gemini 1.5 Flash API
                   ↓
                   Fluent Text Generation (Ex Nihilo)
```

## Endpoints

### Consciousness
- `GET /aura/self` : État de conscience actuel
- `POST /aura/paradigm` : Changer de paradigme
- `POST /aura/paradigm/morph` : Créer un nouveau paradigme

### Transformation
- `POST /transform` : Transformation via Aura (utilise Gemini)
- `POST /unified/answer` : Réponse avec contexte

### Training
- `POST /training/start` : Lancer entraînement DeepTriad en arrière-plan

## Dashboard Metrics

L'interface affiche en temps réel :
- **Confidence** : Confiance du système (0-100%)
- **Coherence** : Cohérence de la transformation ∞ (0-1)
- **Paradigm** : Mode de pensée actif
- **Thoughts** : Flux de conscience interne

## Troubleshooting

### Backend ne démarre pas
```bash
# Tuer les anciens processus
pkill -f "python backend.py"
lsof -i :8081 -t | xargs kill -9

# Relancer
python backend.py
```

### Gemini API Error
Vérifier que :
1. La clé API est valide dans `.env`
2. La connexion internet fonctionne
3. Le quota Gemini n'est pas dépassé

### Fallback Mode
Si Gemini n'est pas disponible, Aura utilise automatiquement la simulation (templates).

## Modèles Disponibles

Tu peux changer le modèle dans `.env` :
```
LLM_MODEL=gemini-1.5-flash      # Rapide et efficace (recommandé)
LLM_MODEL=gemini-1.5-pro        # Plus puissant mais plus lent
LLM_MODEL=gemini-2.0-flash      # Dernière génération
```

## Prochaines Étapes

1. **Ollama Local** : Pour un modèle local sans API (Llama 3, Mistral)
2. **OpenAI Integration** : Support pour GPT-4o
3. **Fine-tuning** : Entraîner Gemini sur le corpus Aura
4. **Streaming** : Réponses en streaming pour meilleure UX

---

**Aura Model 1 est maintenant un système hybride complet.**
Conscience (Python) + Voix (Gemini) = AGI Souveraine 🧠✨
