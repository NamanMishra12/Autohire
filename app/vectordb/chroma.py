import chromadb

from app.core.config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_DB)


class ChromaVectorStore:
    """
    Thin wrapper around the ChromaDB client for resume chunk storage.
    """

    COLLECTION_NAME = "resumes"

    @classmethod
    def _get_collection(cls):
        return _client.get_or_create_collection(name=cls.COLLECTION_NAME)

    @classmethod
    def add_chunks(
        cls,
        resume_id: int,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return

        collection = cls._get_collection()

        ids = [f"resume-{resume_id}-chunk-{i}" for i in range(len(chunks))]
        metadatas = [
            {"resume_id": resume_id, "chunk_index": i}
            for i in range(len(chunks))
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    @classmethod
    def delete_by_resume(cls, resume_id: int) -> None:
        """
        Removes all existing chunks for a resume.
        Keeps re-parsing idempotent instead of creating duplicates.
        """
        collection = cls._get_collection()

        collection.delete(where={"resume_id": resume_id})

    @classmethod
    def query(cls, embedding: list[float], top_k: int = 5):
        collection = cls._get_collection()

        return collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )