from sentence_transformers import SentenceTransformer
import numpy as np

# Load once when imported
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_text_embedding(text: str) -> np.ndarray:
    embedding = model.encode(text)
    return embedding

