from sentence_transformers import SentenceTransformer
import os

# --- THIS IS THE CHANGE ---
# Switch to a model optimized for asymmetric semantic search (query vs. document)
MODEL_NAME = 'sentence-transformers/msmarco-distilbert-base-v2'
MODEL_SAVE_PATH = 'models/msmarco-distilbert-base-v2'

def download_and_save_model():
    """
    Downloads a sentence-transformer model from Hugging Face and saves it locally.
    """
    print(f"Downloading model: {MODEL_NAME}")

    if not os.path.exists(MODEL_SAVE_PATH):
        os.makedirs(MODEL_SAVE_PATH)

        # Load the model from Hugging Face (this will download it)
    model = SentenceTransformer(MODEL_NAME)

        # Save the model to the specified path for offline use
    model.save(MODEL_SAVE_PATH)

    print(f"Model saved successfully to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    download_and_save_model()