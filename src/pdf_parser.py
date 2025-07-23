# src/pdf_parser.py

import fitz  # PyMuPDF
import statistics
import re
import unicodedata
from . import config

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text by handling ligatures, removing common PDF artifacts,
    and standardizing whitespace.
    """
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'•\s*|·\s*|’\s*|–\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_header(span: dict, median_font_size: float) -> bool:
    """
    Determines if a text span is a header using flexible rules.
    """
    if not span or not span.get('text', '').strip():
        return False

    font_size = span.get('size', 0)
    font_name = span.get('font', '').lower()
    text = span.get('text', '')

    if len(text.split()) > 12:
        return False

    is_bold = 'bold' in font_name
    is_larger = font_size > (median_font_size * config.HEADER_FONT_SIZE_THRESHOLD)

    if is_bold or is_larger:
        return True
        
    return False

def parse_pdf_hierarchically(pdf_path: str) -> list:
    """
    Parses a PDF by identifying headers and consolidating all text between them.
    This version ignores any text before the first detected header on a page.
    """
    doc = fitz.open(pdf_path)
    all_sections = []

    for page_num, page in enumerate(doc, start=1):
        font_sizes = [
            span['size']
            for block in page.get_text("dict").get("blocks", [])
            if "lines" in block
            for line in block.get("lines", [])
            for span in line.get("spans", [])
            if span.get('text', '').strip()
        ]
        median_font_size = statistics.median(font_sizes) if font_sizes else 12.0

        blocks = page.get_text("dict").get("blocks", [])
        page_sections = []
        
        # Start with no current section. A section will only be created
        # after the first header on the page is found.
        current_section = None

        for block in blocks:
            if block.get("type") != 0 or "lines" not in block:
                continue

            first_span = block["lines"][0]["spans"][0]
            block_is_header = is_header(first_span, median_font_size)

            block_text = " ".join(
                span['text'] for line in block["lines"] for span in line["spans"]
            )
            cleaned_block_text = clean_text(block_text)

            if not cleaned_block_text:
                continue

            if block_is_header:
                # If a section was already being built, save it.
                if current_section:
                    page_sections.append(current_section)
                
                # Start a new section.
                current_section = {
                    "title": cleaned_block_text,
                    "page": page_num,
                    "content": ""
                }
            elif current_section:
                # Only add content if we are inside a section (i.e., after the first header).
                current_section["content"] += cleaned_block_text + " "
        
        # Add the last section of the page if it exists
        if current_section:
            page_sections.append(current_section)
        
        all_sections.extend(page_sections)

    doc.close()

    # Final processing step: Convert the consolidated 'content' into 'sub_chunks'
    for section in all_sections:
        section_content = section["content"].strip()
        section["sub_chunks"] = []
        if len(section_content) > config.MIN_CHUNK_LENGTH:
            section["sub_chunks"].append({
                "text": section_content,
                "page": section["page"]
            })
        if "content" in section:
             del section["content"]

    return all_sections