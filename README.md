## Persona‑Driven Document Intelligence

A semantic analysis pipeline that extracts and ranks the most relevant information from a collection of PDF documents based on a user’s persona and objective. Combines a fast bi‑encoder retrieval stage with a precise cross‑encoder re‑ranking stage, all running fully offline in Docker.

## 🚀 Table of Contents

Overview

Features

Tech Stack

Prerequisites

Installation

Usage

Query Setup

Local Run

Docker Run

Project Structure

Configuration & Tuning

## 📖 Overview

Persona‑Driven Document Intelligence processes multiple PDFs, tailors semantic analysis to a user’s persona and objective, and produces a context‑aware, prioritized summary to speed decision‑making.

## ✨ Features

Hierarchical PDF ParsingDetects headings via font‑size heuristics and groups content into logical chunks.

Persona‑Driven Query EnhancementMerges persona + objective + task keywords into rich natural‑language queries.

Two‑Stage Semantic Retrieval

Bi‑Encoder Retrieval (msmarco-distilbert-base-v2): Fast embedding lookup; retrieves top 75 candidates.

Cross‑Encoder Re‑ranking (cross-encoder/ms-marco-MiniLM-L-6-v2): Deep semantic scoring to refine ranking.

Structured OutputProduces output.json listing highest‑relevance sections first.

Containerized & OfflineFully reproducible via Docker; no internet required at runtime.

## 🛠 Tech Stack

Python 3.9+

PDF Parsing: PyMuPDF (fitz)

Embeddings: sentence-transformers

Similarity & Re‑ranking: sentence-transformers cross‑encoder

Numerics: NumPy

Containerization: Docker

---

## 📋 Prerequisites

* Python 3.9 or higher
* Docker Engine (for containerized execution)

> *Note*: Git is assumed to be available on your system.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/persona-doc-intel.git
cd persona-doc-intel
```

### 2. Create a Virtual Environment (Optional)

```bash
python3 -m venv venv
source venv/bin/activate    # on Linux/macOS
venv\\Scripts\\activate   # on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Query Setup

Edit `input/query.json` to define your persona and objective. Example:

```json
{
  "persona": {"role": "Travel Planner"},
  "job_to_be_done": {"description": "Plan a 4-day trip for 10 college friends."}
}
```

### Local Run

Ensure PDFs are in `input/` alongside `query.json`, then:

```bash
python src/main.py --input input/ --output output/
```

### Docker Run

1. **Build the image**

   ```bash
   docker build -t document-intelligence .
   ```
2. **Run the container**

   ```bash
   docker run --rm \
     -v "$(pwd)/input:/app/input" \
     -v "$(pwd)/output:/app/output" \
     document-intelligence
   ```

---

## 📂 Project Structure

```
.
├── Dockerfile
├── README.md
├── requirements.txt
├── input/               # PDFs + query.json
├── output/              # Generated output.json
└── src/
    ├── config.py        # Parsing thresholds
    ├── main.py          # Entry point
    ├── pdf_parser.py    # Header-based PDF parsing
    ├── semantic_ranker.py # Query enhancement & ranking
    └── output_builder.py  # JSON output formatting
```

---

## 🎛 Configuration & Tuning

Adjust header detection sensitivity in `src/config.py`:

Number of bi-encoder candidates to retrieve
TOP_K = 75

Header detection sensitivity
HEADER_FONT_SIZE_THRESHOLD = 1.1

Model identifiers
BIO_ENCODER = "msmarco-distilbert-base-v2"
CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

---
