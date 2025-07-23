Approach Explanation: Persona-Driven Document Intelligence
Our solution is architected as a modular, multi-stage Python pipeline designed for offline execution. The system intelligently extracts and ranks document content by semantically matching it against a user's profile and objective.

1. Hierarchical PDF Parsing & Chunking
We use the PyMuPDF library for its robust and fast text extraction capabilities. Instead of treating a PDF as flat text, our pdf_parser.py module implements a sophisticated hierarchical chunking strategy.

It first identifies major section headers using a multi-factor heuristic that analyzes font weight (boldness), font size (relative to the page's median), and conciseness. This is far more reliable than using font size alone.

Crucially, all text content appearing between two consecutive headers is consolidated into a single, cohesive chunk. This ensures that the full context of a section is preserved for ranking, which proved vital for achieving relevant results. This structure of a title with its complete body of text directly maps to the hackathon's required output format.

2. Model Selection & Semantic Ranking
The core of our system's intelligence comes from the sentence-transformers/msmarco-distilbert-base-v2 model. This model was specifically chosen for its excellent performance in semantic search tasks, combined with a fast CPU inference speed and a manageable size, making it ideal for the hackathon's constraints.

Our ranking algorithm in semantic_ranker.py is powered by cosine similarity:

Enhanced Query Formulation: A simple combination of the Persona and Job-to-be-Done proved insufficient. Our final approach creates a descriptive, natural language query that is explicitly expanded with keywords relevant to the persona's goal (e.g., "nightlife," "coastal adventures," "food"). This query rewriting step is essential for guiding the model to the most relevant content.

Vector Encoding: This enhanced query and the consolidated content chunk for each section are encoded into semantic vector embeddings.

Ranking: We calculate the cosine similarity between the query vector and each section's content vector. Since each section now has one consolidated chunk of text, its relevance score is determined by the similarity of its entire content to the query. Sections are then ranked globally based on these scores.

This refined approach allows us to precisely address the "Section Relevance" and "Sub-Section Relevance" scoring categories. The entire process is orchestrated by main.py, which handles I/O and uses output_builder.py to generate the final output in the specified JSON format.