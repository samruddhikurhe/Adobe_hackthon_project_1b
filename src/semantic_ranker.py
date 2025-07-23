import threading
from typing import Any, Dict, List, Optional, Tuple

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# Import configuration
from . import config


class SemanticRanker:
    """
    A thread-safe Singleton class for performing semantic ranking of PDF sections.
    """
    _instance: Optional['SemanticRanker'] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> 'SemanticRanker':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        model_path = config.MODEL_PATH
        device = config.DEVICE
        try:
            print(f"Initializing SemanticRanker: loading {model_path} on {device}...")
            self.model = SentenceTransformer(model_path, device=device)
            print("Model loaded.")
        except Exception as e:
            print(f"Failed to load model {model_path}: {e}")
            raise
        self._initialized = True

    # In src/semantic_ranker.py

    def rank_documents(
        self,
        persona: str,
        jtd: str,
        documents_data: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Ranks sections and sub-sections based on semantic similarity to a DYNAMIC persona and JTD.
        """
        # --- Step 1: Create a dynamic query from the input ---
        # This is the key change. The query is now built from the function arguments.
        persona_text = persona.get('role', 'a user')
        jtd_text = jtd.get('description') or jtd.get('task', 'a task')
        query = f"{persona_text}: {jtd_text}"

        print(f"Using dynamic query: {query}") # For debugging

        # --- Step 2: Flatten all document chunks ---
        all_chunks: List[Dict[str, Any]] = []
        for doc_idx, doc in enumerate(documents_data):
            for section in doc.get('sections', []):
                # We now associate the section title with the chunk for better context
                section_title = section.get('title', '')
                for sub_chunk in section.get('sub_chunks', []):
                    sub_chunk['doc_idx'] = doc_idx
                    sub_chunk['section_title'] = section_title
                    all_chunks.append(sub_chunk)

        if not all_chunks:
            return [], []

        # --- Step 3: Perform a single, batched encoding operation ---
        query_emb = self.model.encode(query, convert_to_tensor=True)
        # Give the model both the title and the text for better ranking
        chunk_texts = [f"{chunk.get('section_title', '')}: {chunk.get('text', '')}" for chunk in all_chunks]
        corpus_emb = self.model.encode(
            chunk_texts,
            convert_to_tensor=True,
            show_progress_bar=False,
            batch_size=32
        )

        # --- Step 4: Calculate scores and assign to chunks ---
        score_matrix = cos_sim(query_emb, corpus_emb)
        scores = score_matrix[0]

        for i, chunk in enumerate(all_chunks):
            chunk['score'] = float(scores[i].item())

        # --- Step 5: Rank sections by the maximum score of their child chunks ---
        ranked_sections: List[Dict[str, Any]] = []
        for doc in documents_data:
            for section in doc.get('sections', []):
                sec_scores = [c.get('score', 0.0) for c in section.get('sub_chunks', []) if c.get('section_title') == section.get('title')]
                section_score = max(sec_scores) if sec_scores else 0.0
                section['score'] = section_score
                ranked_sections.append({
                    'doc_name': doc.get('doc_name', 'Unknown Document'),
                    'page': section.get('page', 1),
                    'title': section.get('title', 'Untitled Section'),
                    'score': section_score
                })
        ranked_sections.sort(key=lambda x: x['score'], reverse=True)

        # --- Step 6: Prepare and sort the sub-section output ---
        ranked_sub_sections: List[Dict[str, Any]] = []
        all_chunks.sort(key=lambda x: x.get('score', 0.0), reverse=True)

        for chunk in all_chunks:
            doc_name = documents_data[chunk['doc_idx']].get('doc_name', 'Unknown Document')
            ranked_sub_sections.append({
                'doc_name': doc_name,
                'page': chunk.get('page', 1),
                'text': chunk.get('text', ''),
                'score': chunk.get('score', 0.0)
            })

        return ranked_sections, ranked_sub_sections
