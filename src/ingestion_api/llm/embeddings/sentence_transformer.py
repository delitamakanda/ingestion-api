from ingestion_api.llm.embeddings.base import EmbeddingService
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingService(EmbeddingService):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        passages = [
            f"passage: {text}" for text in texts
        ]
        embeddings = self.model.encode(passages, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(f"query: {text}", normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()
