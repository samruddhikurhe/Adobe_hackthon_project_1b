from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = 'sentence-transformers/msmarco-distilbert-base-v2'
MODEL_SAVE_PATH = 'models/msmarco-distilbert-base-v2'

def download_and_save_model():
    """
    Downloads a sentence-transformer model from Hugging Face and saves it locally.
    """
    print(f"Downloading model: {MODEL_NAME}")

    if not os.path.exists(MODEL_SAVE_PATH):
        os.makedirs(MODEL_SAVE_PATH)

    model = SentenceTransformer(MODEL_NAME)

    model.save(MODEL_SAVE_PATH)

    print(f"Model saved successfully to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    download_and_save_model()