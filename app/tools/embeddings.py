from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _get_model() -> SentenceTransformer:
    """
    Loads the embedding model once per process.
    First call downloads the model if not already cached locally
    (requires internet access the very first time).
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


class EmbeddingGenerator:
    """
    Pure utility wrapper around the sentence-transformers model.
    """

    @staticmethod
    def generate(texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = _get_model()

        embeddings = model.encode(
            texts,
            show_progress_bar=False,
        )

        return embeddings.tolist()