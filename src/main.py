# src/main.py

import os
import json
from pathlib import Path
from datetime import datetime

# Import project modules
from . import config
from .pdf_parser import parse_pdf_hierarchically
from .semantic_ranker import SemanticRanker
from .output_builder import build_output_json

def process_collection(collection_path: Path, ranker: SemanticRanker):
    """
    Processes a single collection of PDFs against its specific query.
    A collection is a directory containing a 'query.json' file and PDF documents.
    """
    collection_name = collection_path.name
    print(f"\n--- Processing Collection: {collection_name} ---")

    # --- Load Input Data for this specific collection ---
    query_file_path = collection_path / config.QUERY_FILE

    try:
        with open(query_file_path, 'r', encoding='utf-8') as f:
            query_data = json.load(f)
        
        persona = query_data.get("persona", {})
        jtd = query_data.get("job_to_be_done", {})

        print(f"Loaded Persona: {persona}")
        print(f"Loaded Job-to-be-Done: {jtd}")

    except FileNotFoundError:
        print(f"Error: Query file not found in {collection_path}. Skipping.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {query_file_path}. Skipping.")
        return

    # --- Find and Parse PDF Documents within this collection ---
    pdf_paths = list(collection_path.rglob('*.pdf'))
    pdf_filenames = [p.name for p in pdf_paths]

    if not pdf_paths:
        print(f"No PDF files found in {collection_path}. Skipping.")
        return

    print(f"Found {len(pdf_paths)} PDF(s) to process: {', '.join(pdf_filenames)}")

    documents_data = []
    for pdf_path in pdf_paths:
        print(f"Parsing {pdf_path.name}...")
        try:
            sections = parse_pdf_hierarchically(str(pdf_path))
            documents_data.append({
                "doc_name": pdf_path.name,
                "sections": sections
            })
        except Exception as e:
            print(f"Could not parse {pdf_path.name}. Error: {e}")

    # --- Rank Documents ---
    print(f"Ranking documents for {collection_name}...")
    ranked_sections, ranked_sub_sections = ranker.rank_documents(
        persona, jtd, documents_data
    )

    # --- Build and Save Final Output for this collection ---
    print(f"Building output for {collection_name}...")
    final_output = build_output_json(
        persona,
        jtd,
        pdf_filenames,
        ranked_sections[:config.TOP_SECTIONS],
        ranked_sub_sections[:config.TOP_SUB_SECTIONS]
    )

    output_path = Path(config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    # Create a unique output filename for each collection
    output_file_path = output_path / f"output_{collection_name}.json"

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print(f"Process for {collection_name} complete. Output saved to {output_file_path}")


def main():
    """
    Main function to find and orchestrate the processing of all collections.
    """
    print("Starting Persona-Driven Document Intelligence process...")

    # Initialize the semantic ranker once to avoid reloading the model
    ranker = SemanticRanker()
    input_dir = Path(config.INPUT_DIR)

    if not input_dir.is_dir():
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    # Find all subdirectories in the input folder that contain a query.json
    collection_paths = [d for d in input_dir.iterdir() if d.is_dir() and (d / config.QUERY_FILE).exists()]

    if not collection_paths:
        print(f"No collections with a '{config.QUERY_FILE}' found in '{input_dir}'.")
        # As a fallback, check if the root input directory itself is a collection
        if (input_dir / config.QUERY_FILE).exists():
             print("Processing the root input directory as a single collection.")
             process_collection(input_dir, ranker)
        return

    for collection_path in collection_paths:
        process_collection(collection_path, ranker)

if __name__ == "__main__":
    main()
