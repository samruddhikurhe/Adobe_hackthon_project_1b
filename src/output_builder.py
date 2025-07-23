# src/output_builder.py

import json
from datetime import datetime
from typing import List, Dict, Any
from . import config

def build_output_json(
    persona: Dict[str, Any],
    jtd: Dict[str, Any],
    input_documents: List[str],
    ranked_sections: List[Dict[str, Any]],
    ranked_sub_sections: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Constructs the final JSON output object from the processed data.
    This function returns a Python dictionary, not a JSON string.
    """
    # Extract the text descriptions from the persona and jtd dictionaries
    # This handles different possible keys like 'description' or 'task'.
    persona_text = persona.get('role', 'Unknown Persona')
    jtd_text = jtd.get('description') or jtd.get('task', 'Unknown Job')

    # Prepare the main structure of the output
    output = {
        "metadata": {
            "input_documents": input_documents,
            "persona": persona_text,
            "job_to_be_done": jtd_text,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    # Populate extracted_sections, limited by the value in config.py
    for i, section in enumerate(ranked_sections, start=1):
        output["extracted_sections"].append({
            "document": section.get("doc_name", "Unknown Document"),
            "section_title": section.get("title", "Untitled Section"),
            "importance_rank": i,
            "page_number": section.get("page", 0)
        })

    # Populate subsection_analysis, limited by the value in config.py
    for sub in ranked_sub_sections:
        output["subsection_analysis"].append({
            "document": sub.get("doc_name", "Unknown Document"),
            "refined_text": sub.get("text", ""),
            "page_number": sub.get("page", 0)
        })

    # Return the complete dictionary
    return output
