# Approach Explanation: Persona-Driven Document Intelligence

This document outlines the end-to-end design and implementation of our modular, offline-capable pipeline for extracting, semantically ranking, and summarizing PDF documents based on a user's persona and objective.

---

## 🔍 1. System Overview

* **Goal:** Given a collection of PDFs and a `query.json` describing a user’s role and task, produce a prioritized list of document sections that best address the user’s needs.
* **Key Components:**

  1. **PDF Parsing & Chunking** (`pdf_parser.py`)
  2. **Query Enhancement & Embedding** (`semantic_ranker.py`)
  3. **Semantic Ranking** (`semantic_ranker.py`)
  4. **Output Assembly** (`output_builder.py`)

All modules are written in Python 3.9+ and orchestrated by `main.py`. Docker ensures consistent, offline-capable execution.

---

## 🌐 2. Hierarchical PDF Parsing & Chunking

**Objective:** Convert raw PDF layouts into meaningful text chunks that preserve context and structure.

1. **Font-Based Header Detection**

   * Analyze every text span’s font size relative to the page’s median font.
   * Measure font weight (boldness) and header-line conciseness (short, descriptive).
   * Combine these signals in a heuristic to reliably identify section titles.

2. **Chunk Consolidation**

   * Treat each detected header as the start of a new chunk.
   * Aggregate all intervening text (paragraphs, lists, figures) into that chunk.
   * Result: A list of `(header, full_section_text)` pairs, giving the model complete context for each section.

> *Why it matters*: Consolidated chunks prevent fragmented ranking and ensure topics aren’t split across multiple embeddings.

---

## 🤖 3. Query Enhancement & Embedding

**Objective:** Transform a minimal user query into a rich, context-aware search prompt.

1. **Descriptive Query Formulation**

   * Base input: Persona role + Job-to-Be-Done (JTBD).
   * Expand with **domain keywords** (e.g., *"beaches, nightlife, local cuisine"*) relevant to the JTBD.
   * Generate a natural-language query that guides the embedding model toward the user’s precise interest.

2. **Embedding Generation**

   * Model: `sentence-transformers/msmarco-distilbert-base-v2`.
   * Compute a single vector for the enhanced query.
   * Compute one vector per consolidated PDF chunk.

> *Model choice rationale*: Balances semantic performance with CPU-friendly speed and a compact footprint (< 400 MB).

---

## 📊 4. Semantic Ranking Algorithm

**Objective:** Score and sort each section chunk by relevance to the enhanced query.

1. **Cosine Similarity Calculation**

   * Measure similarity between the query vector and each chunk vector.

2. **Global Ranking**

   * Assign each chunk a relevance score.
   * Sort all chunks in descending order of score.

3. **Relevance Categories**

   * **Section Relevance**: Overall importance of the chunk’s topic.
   * **Sub-Section Relevance**: Finer-grained score when deeper headers exist (handled implicitly through chunk granularity).

> *Outcome*: A fully ordered list of sections, highest-scoring first, ready for extraction to JSON.

---

## 🛠 5. Output Generation

* `output_builder.py` reads the ranked list and formats it into `output.json`:

  ```json
  [
    {"header": "Top Section", "content": "Full text...", "score": 0.92},
    ...
  ]
  ```
* The JSON schema supports downstream integration (dashboards, APIs, or further processing).

---

## 🎯 6. Summary

Our modular pipeline—leveraging robust PDF parsing heuristics and state-of-the-art embeddings—delivers persona-driven insights from large document sets. By preserving full-section context and refining queries with domain keywords, we ensure the semantically most relevant content rises to the top, empowering faster, data-informed decisions.
