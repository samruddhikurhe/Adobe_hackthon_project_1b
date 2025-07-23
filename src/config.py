import os

# --- Path Configurations ---
# Note: These paths are relative to the container's /app directory
INPUT_DIR = "input"
OUTPUT_DIR = "output"
MODEL_PATH = "sentence-transformers/msmarco-distilbert-base-v2" 

# --- Input File Configuration ---
# We assume the persona and JTD are in a file named query.json in the input directory
QUERY_FILE = "query.json"

# --- Model & Ranking Configurations ---
# The device to run the model on ('cpu' is required by the hackathon)
DEVICE = "cpu"
# Number of top sections to include in the output
TOP_SECTIONS = 10
# Number of top sub-sections to include in the output
TOP_SUB_SECTIONS = 10

# --- PDF Parsing Configurations ---
# Heuristic for identifying headers: font size must be this much larger than the median
HEADER_FONT_SIZE_THRESHOLD = 1.15
# Minimum number of characters for a text chunk to be considered valid
MIN_CHUNK_LENGTH = 5