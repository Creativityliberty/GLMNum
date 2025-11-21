# Guide de Déploiement - Aura Model 1

**Projet:** Aura Model 1 GLM  
**Propriétaire:** Nümtema AGENCY  
**Contact:** numtemalionel@gmail.com  
**Version:** 1.0.0  
**Date:** 2025-11-21

---

## 🚀 Démarrage Rapide

### Étape 1: Installation des Dépendances

```bash
cd /app/default_project_1646/Numtema_AGENCY/backend
pip install flask flask-cors
```

### Étape 2: Lancement du Backend

```bash
python server.py
```

Le serveur démarre sur `http://localhost:5000`

### Étape 3: Ouverture de l'Interface

Ouvrez `frontend/index.html` dans votre navigateur ou utilisez:

```bash
cd /app/default_project_1646/Numtema_AGENCY/frontend
python -m http.server 8000
```

Accédez à `http://localhost:8000`

---

## ✅ Vérification de l'Installation

### Test Backend
```bash
curl http://localhost:5000/api/health
```

Réponse attendue:
```json
{
    "status": "healthy",
    "model": "Aura Model 1",
    "owner": "Nümtema AGENCY",
    "contact": "numtemalionel@gmail.com"
}
```

### Test Pipeline RRLA
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Test du système Aura"}'
```

### Exécution des Tests
```bash
cd /app/default_project_1646/Numtema_AGENCY
python tests/test_glm.py
```

Résultat attendu: **13 tests passed** ✅

---

## 📦 Structure de Déploiement