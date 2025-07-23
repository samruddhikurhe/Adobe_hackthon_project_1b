**Persona-Driven Document Intelligence**
A semantic analysis pipeline that extracts and ranks the most relevant information from a collection of PDF documents based on a user’s persona and objective.

---

## 🚀 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)

   * [Query Setup](#query-setup)
   * [Local Run](#local-run)
   * [Docker Run](#docker-run)
7. [Project Structure](#project-structure)
8. [Configuration & Tuning](#configuration--tuning)
9. [Contributing](#contributing)
10. [License](#license)
11. [Contact](#contact)

---

## 📖 Overview

Persona-Driven Document Intelligence was developed for the Adobe Hackathon (Round 1B). It processes multiple PDF documents, tailors the analysis to a user’s persona and objective, and generates a prioritized, context-aware summary for faster decision-making.

---

## ✨ Features

* **Hierarchical PDF Parsing**: Detects headers by font size/weight and groups content into logical sections.
* **Query Enhancement**: Combines persona, objective, and task-specific keywords for richer search queries.
* **Semantic Ranking**: Uses `msmarco-distilbert-base-v2` to compute embeddings and rank sections by cosine similarity.
* **Structured Output**: Generates a clear `output.json` with the highest-relevance sections first.
* **Containerized**: One-time setup; runs consistently across environments via Docker.

---

## 🛠 Tech Stack

* **Language**: Python 3.9+
* **PDF Parsing**: PyMuPDF (`fitz`)
* **Embeddings**: `sentence-transformers`
* **Numerics**: NumPy
* **Containerization**: Docker

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

```python
# Default threshold
HEADER_FONT_SIZE_THRESHOLD = 1.1
# More sensitive: lower value (e.g., 1.05)
# Less sensitive: higher value (e.g., 1.2)
```

---
