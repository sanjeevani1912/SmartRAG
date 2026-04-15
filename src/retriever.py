import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class SmartRetriever:
    def __init__(self, index_path):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = FAISS.load_local(
            index_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

    def retrieve(self, query, k=5):
        """
        Retrieves chunks and their relevance scores.
        FAISS with relevance scores returns a reciprocal distance [0, 1] 
        where 1 is most similar.
        """
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)
        
        chunks = [res[0] for res in results]
        scores = [res[1] for res in results]
        
        return chunks, scores
