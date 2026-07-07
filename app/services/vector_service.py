from app.tools.embeddings import EmbeddingGenerator
from app.vectordb.chroma import ChromaVectorStore


class VectorService:
    """
    Orchestrates embedding generation and vector storage.
    Used by DocumentService during resume parsing, and later
    by the Matcher Agent during job matching.
    """

    def store_resume_chunks(self, resume_id: int, chunks: list[str]) -> int:
        """
        Embeds and stores resume text chunks in ChromaDB.
        Replaces any previously stored chunks for this resume.
        Returns the number of chunks stored.
        """
        ChromaVectorStore.delete_by_resume(resume_id)

        if not chunks:
            return 0

        embeddings = EmbeddingGenerator.generate(chunks)

        ChromaVectorStore.add_chunks(
            resume_id=resume_id,
            chunks=chunks,
            embeddings=embeddings,
        )

        return len(chunks)