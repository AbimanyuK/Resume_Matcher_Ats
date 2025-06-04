import faiss
import numpy as np

def build_faiss_index(embedding_list: list[np.ndarray]) -> faiss.IndexFlatIP:
    dim = embedding_list[0].shape[0]
    index = faiss.IndexFlatIP(dim)  
    index.add(np.vstack(embedding_list))
    return index

def search_index(index, query_vector: np.ndarray, top_k=5):
    query_vector = np.expand_dims(query_vector, axis=0)
    D, I = index.search(query_vector, top_k)
    return D[0], I[0]
