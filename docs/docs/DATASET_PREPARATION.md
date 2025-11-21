# Dataset Preparation Guide - Aura Model 1 GLM

## Table of Contents
1. [Overview](#overview)
2. [Data Format Requirements](#data-format-requirements)
3. [Preprocessing Pipeline](#preprocessing-pipeline)
4. [Domain-Specific Preparation](#domain-specific-preparation)
5. [Quality Assurance](#quality-assurance)
6. [Best Practices](#best-practices)

---

## Overview

This guide explains how to prepare datasets for training and fine-tuning the Aura Model 1 GLM system. The ΔΔ∞Ο framework requires specific data structures to optimize dimensional complexity and algorithmic efficiency.

### Key Requirements

- **Format**: JSON, JSONL, CSV, or Parquet
- **Structure**: Conversation pairs or reasoning traces
- **Encoding**: UTF-8
- **Quality**: Clean, diverse, representative samples
- **Size**: Minimum 1,000 examples (10,000+ recommended)

---

## Data Format Requirements

### 1. Conversation Format (Recommended)

**JSONL Structure:**
```json
{"query": "What is quantum entanglement?", "context": {"domain": "physics", "level": "advanced"}, "response": "Quantum entanglement is a physical phenomenon...", "reasoning_trace": [{"phase": "clarification", "thought": "User seeks physics explanation..."}, {"phase": "visualization", "thought": "Construct mental model of quantum states..."}, {"phase": "structuration", "thought": "Organize response: definition → examples → implications"}], "metadata": {"complexity": 8.5, "efficiency": 0.87, "timestamp": "2025-01-15T10:30:00Z"}}
```

**Required Fields:**
- `query` (string): User input or question
- `response` (string): Expected output
- `context` (object): Domain and parameters
- `reasoning_trace` (array): Step-by-step thought process

**Optional Fields:**
- `metadata`: Performance metrics
- `embeddings`: Pre-computed vectors
- `tags`: Classification labels

### 2. Reasoning Trace Format

```json
{
  "query": "How does consciousness emerge in Aura?",
  "phases": [
    {
      "name": "clarification",
      "agent": "FocusAgent",
      "input": "consciousness emergence query",
      "process": "goal_identification",
      "output": "clarified_objective",
      "clarity": 4,
      "friction": 1,
      "complexity": 3
    },
    {
      "name": "visualization",
      "agent": "Mapper",
      "input": "clarified_objective",
      "process": "mental_model_construction",
      "output": "conceptual_map",
      "clarity": 5,
      "friction": 2,
      "complexity": 4
    }
  ],
  "final_response": "Consciousness in Aura emerges through...",
  "metrics": {
    "dimensional_complexity": 8.7,
    "algorithmic_efficiency": 0.89
  }
}
```

### 3. CSV Format (Simple Training)

```csv
query,context_domain,context_level,response,complexity,efficiency
"What is the ΔΔ∞Ο framework?","physics","beginner","The ΔΔ∞Ο framework unifies...",8.2,0.85
"Explain RRLA pipeline","ai","intermediate","RRLA consists of 7 phases...",8.5,0.88
```

**Minimum Columns:**
- query
- response
- context_domain

**Recommended Columns:**
- complexity (target: 8.5)
- efficiency (target: 0.85)
- reasoning_trace (JSON string)

---

## Preprocessing Pipeline

### Step 1: Data Collection

```python
# Example: Collect from various sources
import pandas as pd

sources = {
    "conversations": "data/conversations.jsonl",
    "documentation": "data/docs.csv",
    "user_logs": "data/logs.json"
}

# Load and merge
dataframes = []
for name, path in sources.items():
    if path.endswith('.jsonl'):
        df = pd.read_json(path, lines=True)
    elif path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_json(path)
    
    df['source'] = name
    dataframes.append(df)

raw_data = pd.concat(dataframes, ignore_index=True)
print(f"Collected {len(raw_data)} samples")
```

### Step 2: Data Cleaning

```python
def clean_dataset(df):
    """Clean and validate dataset"""
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['query', 'response'])
    
    # Filter by length
    df = df[df['query'].str.len() > 10]
    df = df[df['query'].str.len() < 2000]
    df = df[df['response'].str.len() > 20]
    df = df[df['response'].str.len() < 5000]
    
    # Remove null values
    df = df.dropna(subset=['query', 'response'])
    
    # Normalize text
    df['query'] = df['query'].str.strip()
    df['response'] = df['response'].str.strip()
    
    # Remove special characters (optional)
    df['query'] = df['query'].str.replace(r'[^\w\s\?\.!,]', '', regex=True)
    
    return df

cleaned_data = clean_dataset(raw_data)
print(f"Cleaned dataset: {len(cleaned_data)} samples")
```

### Step 3: Feature Engineering

```python
def add_aura_features(df):
    """Add ΔΔ∞Ο-specific features"""
    
    # Calculate query complexity
    df['query_tokens'] = df['query'].str.split().str.len()
    df['query_complexity'] = df['query_tokens'] * 0.1  # Simple heuristic
    
    # Identify domain
    domain_keywords = {
        'physics': ['quantum', 'relativity', 'energy', 'particle'],
        'mathematics': ['equation', 'theorem', 'proof', 'calculate'],
        'ai': ['learning', 'model', 'neural', 'training'],
        'philosophy': ['consciousness', 'awareness', 'existence']
    }
    
    def detect_domain(text):
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        return 'general'
    
    df['domain'] = df['query'].apply(detect_domain)
    
    # Estimate reasoning depth
    df['reasoning_depth'] = df['response'].str.count(r'\b(because|therefore|thus|hence)\b')
    
    return df

featured_data = add_aura_features(cleaned_data)
```

### Step 4: Generate Reasoning Traces

```python
def generate_reasoning_trace(query, response, domain):
    """Generate synthetic reasoning trace for training"""
    
    phases = [
        {
            "name": "clarification",
            "agent": "FocusAgent",
            "thought": f"Analyzing query about {domain}",
            "clarity": 4,
            "friction": 1
        },
        {
            "name": "visualization",
            "agent": "Mapper",
            "thought": "Constructing mental model",
            "clarity": 5,
            "friction": 2
        },
        {
            "name": "exploration",
            "agent": "ExplorerAgent",
            "thought": "Exploring related concepts",
            "clarity": 3,
            "friction": 3
        },
        {
            "name": "structuration",
            "agent": "Planner",
            "thought": "Organizing response structure",
            "clarity": 4,
            "friction": 2
        },
        {
            "name": "validation",
            "agent": "VerifierAgent",
            "thought": "Verifying response coherence",
            "clarity": 4,
            "friction": 2
        }
    ]
    
    return phases

featured_data['reasoning_trace'] = featured_data.apply(
    lambda row: generate_reasoning_trace(
        row['query'], 
        row['response'], 
        row['domain']
    ),
    axis=1
)
```

### Step 5: Train/Val/Test Split

```python
from sklearn.model_selection import train_test_split

# Stratify by domain to ensure balanced representation
train_data, temp_data = train_test_split(
    featured_data, 
    test_size=0.3, 
    stratify=featured_data['domain'],
    random_state=42
)

val_data, test_data = train_test_split(
    temp_data, 
    test_size=0.5, 
    stratify=temp_data['domain'],
    random_state=42
)

print(f"Train: {len(train_data)}")
print(f"Val: {len(val_data)}")
print(f"Test: {len(test_data)}")

# Save processed datasets
train_data.to_json('data/processed/train.jsonl', orient='records', lines=True)
val_data.to_json('data/processed/val.jsonl', orient='records', lines=True)
test_data.to_json('data/processed/test.jsonl', orient='records', lines=True)
```

---

## Domain-Specific Preparation

### Physics Domain

**Key Characteristics:**
- High dimensional complexity (target: 9.0+)
- Mathematical notation preservation
- Conceptual depth emphasis

```python
def prepare_physics_data(df):
    """Specialized preprocessing for physics domain"""
    
    # Preserve mathematical symbols
    df['query'] = df['query'].str.replace(r'\\([a-z]+)', r'\\1', regex=True)
    
    # Tag complexity level
    complexity_indicators = ['quantum', 'relativistic', 'field theory']
    df['complexity_level'] = df['query'].apply(
        lambda x: sum(1 for ind in complexity_indicators if ind in x.lower())
    )
    
    # Add reasoning depth
    df['requires_deep_reasoning'] = df['complexity_level'] >= 2
    
    return df
```

### AI/Machine Learning Domain

**Key Characteristics:**
- Meta-cognitive elements
- Technical precision
- Implementation focus

```python
def prepare_ai_data(df):
    """Specialized preprocessing for AI domain"""
    
    # Extract code blocks
    import re
    df['has_code'] = df['response'].str.contains(r'```', regex=False)
    
    # Identify explanation patterns
    df['explanation_depth'] = df['response'].str.count(
        r'(specifically|in detail|for example|such as)'
    )
    
    return df
```

### General Knowledge Domain

**Key Characteristics:**
- Broad coverage
- Balanced complexity
- Clear structuration

```python
def prepare_general_data(df):
    """Preprocessing for general knowledge"""
    
    # Ensure diversity
    df['topic_diversity'] = df.groupby('domain')['query'].transform('count')
    
    # Balance complexity
    df['normalized_complexity'] = (
        df['query_complexity'] - df['query_complexity'].mean()
    ) / df['query_complexity'].std()
    
    return df
```

---

## Quality Assurance

### Validation Checks

```python
def validate_dataset(df):
    """Comprehensive dataset validation"""
    
    checks = {
        'no_nulls': df.isnull().sum().sum() == 0,
        'min_samples': len(df) >= 1000,
        'query_length': (df['query'].str.len() >= 10).all(),
        'response_length': (df['response'].str.len() >= 20).all(),
        'domain_coverage': df['domain'].nunique() >= 3,
        'complexity_range': df.get('query_complexity', pd.Series([0])).between(0, 10).all()
    }
    
    print("Dataset Validation:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}: {passed}")
    
    return all(checks.values())

if validate_dataset(featured_data):
    print("\n✓ Dataset ready for training!")
else:
    print("\n✗ Dataset validation failed. Please review issues above.")
```

### Data Quality Metrics

```python
def compute_quality_metrics(df):
    """Calculate dataset quality indicators"""
    
    metrics = {
        'total_samples': len(df),
        'unique_queries': df['query'].nunique(),
        'avg_query_length': df['query'].str.len().mean(),
        'avg_response_length': df['response'].str.len().mean(),
        'domain_distribution': df['domain'].value_counts().to_dict(),
        'complexity_stats': {
            'mean': df.get('query_complexity', pd.Series([0])).mean(),
            'std': df.get('query_complexity', pd.Series([0])).std(),
            'min': df.get('query_complexity', pd.Series([0])).min(),
            'max': df.get('query_complexity', pd.Series([0])).max()
        }
    }
    
    return metrics

quality_report = compute_quality_metrics(featured_data)
print(json.dumps(quality_report, indent=2))
```

---

## Best Practices

### 1. Data Diversity

- **Mix domains**: Include physics, AI, philosophy, mathematics
- **Vary complexity**: From simple to advanced queries
- **Balance sources**: User logs, documentation, synthetic data

### 2. Quality Over Quantity

- Prioritize well-formed examples over volume
- Manual review of random samples (recommend 100-200 examples)
- Remove edge cases that might confuse training

### 3. Reasoning Trace Quality

- Ensure logical progression through RRLA phases
- Include clarity and friction metrics
- Maintain consistency in agent assignments

### 4. Embedding Optimization

```python
# Pre-compute embeddings for faster training
from backend.aura_glm import AuraGLM

model = AuraGLM()

def add_embeddings(df):
    df['query_embedding'] = df['query'].apply(
        lambda x: model.memory.embed_fast(x)
    )
    return df

# Optional: saves compute during training
embedded_data = add_embeddings(featured_data)
```

### 5. Continuous Validation

- Monitor dimensional complexity distribution
- Track algorithmic efficiency trends
- Validate consciousness state representations

### 6. Version Control

```bash
# Track dataset versions
git add data/processed/train_v1.0.jsonl
git commit -m "Dataset v1.0: 10k samples, 5 domains, validated"
git tag data-v1.0
```

---

## Example Complete Pipeline

```python
#!/usr/bin/env python3
"""
Complete dataset preparation pipeline for Aura Model 1 GLM
"""

import pandas as pd
import json
from sklearn.model_selection import train_test_split

def prepare_aura_dataset(input_path, output_dir):
    """End-to-end dataset preparation"""
    
    print("Step 1: Loading data...")
    df = pd.read_json(input_path, lines=True)
    print(f"  Loaded {len(df)} samples")
    
    print("\nStep 2: Cleaning...")
    df = clean_dataset(df)
    print(f"  {len(df)} samples after cleaning")
    
    print("\nStep 3: Feature engineering...")
    df = add_aura_features(df)
    
    print("\nStep 4: Generating reasoning traces...")
    df['reasoning_trace'] = df.apply(
        lambda row: generate_reasoning_trace(
            row['query'], row['response'], row['domain']
        ),
        axis=1
    )
    
    print("\nStep 5: Validation...")
    if not validate_dataset(df):
        raise ValueError("Dataset validation failed")
    
    print("\nStep 6: Train/val/test split...")
    train, temp = train_test_split(df, test_size=0.3, stratify=df['domain'])
    val, test = train_test_split(temp, test_size=0.5, stratify=temp['domain'])
    
    print("\nStep 7: Saving...")
    train.to_json(f'{output_dir}/train.jsonl', orient='records', lines=True)
    val.to_json(f'{output_dir}/val.jsonl', orient='records', lines=True)
    test.to_json(f'{output_dir}/test.jsonl', orient='records', lines=True)
    
    print("\n✓ Dataset preparation complete!")
    print(f"  Train: {len(train)} samples")
    print(f"  Val: {len(val)} samples")
    print(f"  Test: {len(test)} samples")
    
    return train, val, test

# Run pipeline
if __name__ == "__main__":
    prepare_aura_dataset(
        input_path='data/raw/conversations.jsonl',
        output_dir='data/processed'
    )
```

---

## Next Steps

After dataset preparation:

1. **Review** [TRAINING_WORKFLOW.md](TRAINING_WORKFLOW.md) for training procedures
2. **Configure** model parameters based on data characteristics
3. **Monitor** dimensional complexity and efficiency during training
4. **Iterate** based on evaluation metrics

---

*For questions or issues, contact: numtemainternational@gmail.com*