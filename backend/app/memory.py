# Placeholder for FAISS vector store integration
import faiss
import numpy as np

class MemoryStore:
    def __init__(self, dim=1536):
        self.index = faiss.IndexFlatL2(dim)
        self.vectors = []
        self.texts = []

    def add(self, vector, text):
        self.index.add(np.array([vector]).astype('float32'))
        self.vectors.append(vector)
        self.texts.append(text)

    def search(self, vector, k=5):
        D, I = self.index.search(np.array([vector]).astype('float32'), k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)] 