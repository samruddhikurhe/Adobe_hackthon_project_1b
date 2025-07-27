# 📄 Persona-Driven Document Intelligence

This document outlines the architecture, evolution, and technical decisions behind our intelligent document analysis pipeline. The system is designed to be a robust, **offline-capable solution** that processes large collections of PDF documents, extracting and ranking the most relevant information based on a user's specific *persona* and *objective*.

---

## 🚀 The Journey: From a Simple Model to a Sophisticated Pipeline

Our development process was an **iterative journey** focused on solving increasingly complex semantic challenges.

---

### 🧪 Initial Approach: The Fast Bi-Encoder

Our first implementation used a standard **bi-encoder model** (`msmarco-distilbert-base-v2`). This architecture is incredibly fast and efficient.

#### ✅ How It Worked:
- Encoded the user’s query into a vector.
- Encoded all text chunks from documents into vectors.
- Used **cosine similarity** to find the chunks closest to the query.

#### ✅ Initial Success:
Worked well for **simple, keyword-based queries** (e.g., finding "nightlife" for a "trip planner").

#### The Challenge: Limits of Keyword-Based Relevance
In a nuanced scenario, such as an *HR professional* needing "fillable forms for onboarding and compliance", the model failed.

- It returned sections about **PDF/A Compliance** and **License Deployment**.
- These matched keywords like "compliance" but **missed the intent**.

#### 🧩 Root Cause:
Bi-encoders are good at surface-level matching but **struggle with deeper contextual understanding**, especially when the same word has different meanings in different contexts.

---

## 🧠 Final Architecture: Two-Stage Retrieval & Re-ranking

To address the limitations, we adopted a **state-of-the-art two-stage architecture** that balances **speed** and **semantic precision**.

### 🥇 Stage 1: Retrieval (Broad Search)

**Model:** `msmarco-distilbert-base-v2` (Bi-Encoder)

**Process:**
1. Generate a descriptive query (e.g., “How to use Acrobat to create, fill, and sign forms…”).
2. Embed query and chunks using bi-encoder.
3. Retrieve top **75 most relevant** candidates via cosine similarity.

**Goal:** Fast, approximate narrowing of candidates from thousands to 75.

---

### 🥈 Stage 2: Re-ranking (Expert Review)

**Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (Cross-Encoder)

**Process:**
1. For each of the 75 candidates, feed the chunk and query together to the cross-encoder.
2. Get a more **accurate relevance score** using deep semantic understanding.
3. Final sorting is done based on this refined score.

**Goal:** Apply deep reasoning to select the most relevant chunks based on intent.

---

### ✅ Summary: Why Two Stages?

| Bi-Encoder              | Cross-Encoder             |
|------------------------|---------------------------|
| Fast & scalable         | Accurate but slow         |
| Good for broad filtering| Good for fine-grained ranking |

The two-stage system **combines speed with precision**, mirroring how modern search engines operate.

---

## 🛠️ Supporting Components

### 📘 Hierarchical PDF Parsing (`pdf_parser.py`)
- Detects headings using **font size and weight heuristics**.
- Consolidates all text under each heading into **logical chunks**.
- Preserves context for relevance scoring.

### 🧠 Dynamic Query Formulation (`semantic_ranker.py`)
- Automatically generates **descriptive queries** based on:
  - The persona (e.g., HR, Lawyer)
  - The job-to-be-done (e.g., “fill forms”, “extract compliance data”)

### 📦 Containerization (`Dockerfile`)
- Fully containerized and **offline-capable**.
- Guarantees reproducibility and platform independence after initial setup.

---

## 🔮 Future Work & Potential Improvements

### 🧩 1. Centralized Configuration
Move model names and thresholds into `config.py` for easier experimentation and tuning.

### 🛡️ 2. Advanced Error Handling
Add detailed `try...except` blocks for:
- Corrupted PDFs
- Encrypted/password-protected files

### 🤖 3. Extractive Question Answering (Stage 3)
Add a third stage using a QA model like `deepset/roberta-base-squad2`:
- Extract **short, direct answers** from top-ranked chunks.
- Example: Instead of giving a paragraph, return the exact form field name.

---

