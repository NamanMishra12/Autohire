from pathlib import Path

import pdfplumber
from docx import Document

from app.exceptions.custome_exceptions import UnsupportedFileTypeException


class ResumeParserTool:
    """
    Extracts and prepares raw resume text for the embedding pipeline.

    Pure utility — no DB access, no business logic, no LLM calls.
    """

    CHUNK_SIZE = 1000     # characters per chunk
    CHUNK_OVERLAP = 150   # characters of overlap between chunks

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        Extracts raw text from a resume file.
        Supports .pdf and .docx. (.doc is not supported by
        python-docx — only the modern Word format.)
        """
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return cls._extract_from_pdf(file_path)

        if extension == ".docx":
            return cls._extract_from_docx(file_path)

        raise UnsupportedFileTypeException(
            message=f"Cannot extract text from '{extension}' files.",
        )

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text_parts = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts)

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        document = Document(file_path)

        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

        return "\n".join(paragraphs)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalizes whitespace in extracted text.
        """
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]

        return "\n".join(lines)

    @classmethod
    def chunk_text(cls, text: str) -> list[str]:
        """
        Splits cleaned text into overlapping chunks suitable
        for embedding generation.
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + cls.CHUNK_SIZE
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += cls.CHUNK_SIZE - cls.CHUNK_OVERLAP

        return chunks