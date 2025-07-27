# src/semantic_ranker.py

import threading
from typing import Any, Dict, List, Optional, Tuple

from sentence_transformers import SentenceTransformer, CrossEncoder
from sentence_transformers.util import cos_sim

from . import config

class SemanticRanker:
    """
    A thread-safe Singleton class for performing a two-stage semantic ranking.
    Stage 1: Fast retrieval with a bi-encoder.
    Stage 2: Accurate re-ranking with a cross-encoder.
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
        
        # --- Load BOTH models ---
        bi_encoder_path = config.MODEL_PATH
        # A lightweight, powerful cross-encoder perfect for re-ranking
        cross_encoder_path = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
        device = config.DEVICE
        
        try:
            print(f"Initializing SemanticRanker...")
            # Stage 1 Model (fast retrieval)
            print(f"Loading bi-encoder: {bi_encoder_path} on {device}...")
            self.bi_encoder = SentenceTransformer(bi_encoder_path, device=device)
            
            # Stage 2 Model (accurate re-ranking)
            print(f"Loading cross-encoder: {cross_encoder_path} on {device}...")
            self.cross_encoder = CrossEncoder(cross_encoder_path, device=device)
            
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Failed to load models: {e}")
            raise
            
        self._initialized = True

    def rank_documents(
        self,
        persona: Dict[str, Any],
        jtd: Dict[str, Any],
        documents_data: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Ranks sections using a two-stage retrieval and re-ranking process.
        """
        # --- Create a more descriptive, action-oriented query ---
        jtd_text = jtd.get('description') or jtd.get('task', 'a task')
        # This query guides the model to focus on the HR workflow actions.
        query = f"How to use Acrobat to create, convert, fill, sign, and send fillable forms for HR tasks like '{jtd_text}'"
        print(f"Using dynamic query: {query}")

        # --- Flatten all document chunks ---
        all_chunks = []
        for doc_idx, doc in enumerate(documents_data):
            for section in doc.get('sections', []):
                section_title = section.get('title', '')
                for sub_chunk in section.get('sub_chunks', []):
                    sub_chunk['doc_idx'] = doc_idx
                    sub_chunk['section_title'] = section_title
                    all_chunks.append(sub_chunk)

        if not all_chunks:
            return [], []

        # --- STAGE 1: Fast Retrieval with Bi-Encoder ---
        print(f"Stage 1: Retrieving top candidates with bi-encoder...")
        query_emb = self.bi_encoder.encode(query, convert_to_tensor=True)
        chunk_texts = [f"{chunk.get('section_title', '')}: {chunk.get('text', '')}" for chunk in all_chunks]
        corpus_emb = self.bi_encoder.encode(chunk_texts, convert_to_tensor=True, show_progress_bar=True)
        
        scores = cos_sim(query_emb, corpus_emb)[0]
        for i, chunk in enumerate(all_chunks):
            chunk['bi_score'] = float(scores[i].item())

        all_chunks.sort(key=lambda x: x.get('bi_score', 0.0), reverse=True)
        top_candidates = all_chunks[:75] 

        # --- STAGE 2: Accurate Re-ranking with Cross-Encoder ---
        print(f"Stage 2: Re-ranking top {len(top_candidates)} candidates with cross-encoder...")
        cross_inp = [[query, f"{chunk.get('section_title', '')}: {chunk.get('text', '')}"] for chunk in top_candidates]
        cross_scores = self.cross_encoder.predict(cross_inp, show_progress_bar=True)

        for i, chunk in enumerate(top_candidates):
            chunk['score'] = float(cross_scores[i])

        # --- Final Ranking and Output Generation ---
        top_candidates.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        
        ranked_sub_sections = []
        for chunk in top_candidates:
            doc_name = documents_data[chunk['doc_idx']].get('doc_name', 'Unknown Document')
            ranked_sub_sections.append({
                'doc_name': doc_name,
                'page': chunk.get('page', 1),
                'text': chunk.get('text', ''),
                'title': chunk.get('section_title'),
                'score': chunk.get('score', 0.0)
            })
            
        section_scores = {}
        for sub in ranked_sub_sections:
            title = sub['title']
            score = sub['score']
            if title and (title not in section_scores or score > section_scores[title]['score']):
                section_scores[title] = {
                    'doc_name': sub['doc_name'],
                    'page': sub['page'],
                    'score': score,
                    'title': title
                }

        ranked_sections = sorted(section_scores.values(), key=lambda x: x['score'], reverse=True)

        return ranked_sections, ranked_sub_sections
