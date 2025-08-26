# services/vectorstore.py
# Purpose: Manage FAISS / Pinecone vector storage for resumes, interview embeddings

import faiss
import os
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.index_file = os.path.join(settings.VECTORSTORE_PATH, "hr_index.faiss")
        self.index = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            self.index = faiss.IndexFlatL2(settings.VECTOR_DIM)

    def save_index(self):
        faiss.write_index(self.index, self.index_file)

    def add_vectors(self, vectors, ids):
        self.index.add_with_ids(vectors, ids)
        self.save_index()

    def search(self, query_vector, top_k=5):
        distances, indices = self.index.search(query_vector, top_k)
        return distances, indices


