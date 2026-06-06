# Free Embedding Models for Local Setup

## Overview
This document provides a comprehensive list of free embedding models that can be set up locally for the government/financial data analysis project.

## 🏆 Top Free Embedding Models (Local/Self-Hosted)

### Lightweight & Fast (Best for Development/Prototyping)

| Model | Dimensions | Size | Speed | Best For |
|-------|------------|------|-------|----------|
| **all-MiniLM-L6-v2** | 384 | 80MB | ⚡⚡⚡ | General purpose, fast prototyping |
| **all-MiniLM-L12-v2** | 384 | 130MB | ⚡⚡⚡ | Better accuracy than L6, still fast |
| **paraphrase-MiniLM-L3-v2** | 384 | 60MB | ⚡⚡⚡ | Very small, good for edge devices |

### High Accuracy (Best for Production)

| Model | Dimensions | Size | Speed | Best For |
|-------|------------|------|-------|----------|
| **BAAI/bge-large-en-v1.5** | 1024 | 1.3GB | ⚡⚡ | State-of-the-art retrieval |
| **BAAI/bge-m3** | 1024 | 560MB | ⚡⚡ | Multilingual + dense + sparse |
| **intfloat/e5-large-v2** | 1024 | 1.3GB | ⚡⚡ | Instruction-tuned, good for RAG |
| **intfloat/multilingual-e5-large** | 1024 | 1.3GB | ⚡⚡ | 99 languages, good for multilingual |

### Multilingual Options

| Model | Languages | Dimensions | Size |
|-------|-----------|------------|------|
| **paraphrase-multilingual-MiniLM-L12-v2** | 50+ | 384 | 460MB |
| **sentence-transformers/LaBSE** | 109 | 768 | 1.3GB |
| **intfloat/multilingual-e5-base** | 99 | 768 | 1.1GB |

## 🛠️ Setup Options

### Option 1: Sentence Transformers (Easiest)
```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

# Quick start - any model from HuggingFace
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(['Hello world', 'Another sentence'])
```

### Option 2: Ollama (Best for Local GPU/CPU)
```bash
# Install Ollama, then pull embedding models
ollama pull nomic-embed-text
ollama pull mxbai-embed-large
```

```python
import ollama

response = ollama.embeddings(
    model='nomic-embed-text',
    prompt='Hello world'
)
embedding = response['embedding']
```

### Option 3: HuggingFace Transformers (Most Control)
```bash
pip install transformers torch
```

```python
from transformers import AutoTokenizer, AutoModel
import torch

model_name = 'BAAI/bge-large-en-v1.5'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Get embeddings
inputs = tokenizer('Hello world', return_tensors='pt')
with torch.no_grad():
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
```

## 📊 Model Comparison for Your Use Case

Based on the project structure (government/financial data), I recommend:

### For Financial/Political Text Analysis:
- **Primary**: `BAAI/bge-large-en-v1.5` - Best retrieval accuracy
- **Alternative**: `intfloat/e5-large-v2` - Instruction-tuned, good for RAG

### For Development/Testing:
- **Primary**: `all-MiniLM-L6-v2` - Fast, small, good enough
- **Alternative**: `all-MiniLM-L12-v2` - Better accuracy, still fast

### For Multilingual Content:
- **Primary**: `intfloat/multilingual-e5-large` - 99 languages
- **Alternative**: `paraphrase-multilingual-MiniLM-L12-v2` - Smaller, 50+ languages

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install sentence-transformers

# 2. Test with smallest model
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print(model.encode(['test']).shape)
"

# 3. For production, use BGE
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-large-en-v1.5')
print(model.encode(['test']).shape)
"
```

## 💡 Free Tier API Options (No Local Setup)

| Provider | Free Tier | Model |
|----------|-----------|-------|
| **HuggingFace** | 1000 requests/day | All open-source models |
| **Ollama** | Unlimited (local) | nomic-embed-text, mxbai-embed-large |
| **Google** | $300 free credit | text-embedding-004 |
| **OpenAI** | $5 free credit | text-embedding-3-small |

## 🔧 Hardware Requirements

| Model Size | RAM Needed | GPU Recommended |
|------------|------------|-----------------|
| <100MB | 1GB+ | No |
| 100MB-500MB | 2-4GB | No (but helps) |
| 500MB-1GB | 4-8GB | Yes |
| >1GB | 8GB+ | Strongly recommended |

## 📝 Notes

- All models listed are open-source and free to use
- Sentence Transformers provides the easiest setup with good performance
- BGE models are currently state-of-the-art for retrieval tasks
- E5 models are instruction-tuned and work well for RAG applications
- For the government/financial data project, BGE-large or E5-large are recommended for production use