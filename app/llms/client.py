from openai import AsyncOpenAI

from app.core.config import settings


def get_llm_client() -> AsyncOpenAI:
    """
    Returns an async LLM client configured for the active provider.
    Grok uses an OpenAI-compatible API so we reuse the openai library.
    """
    return AsyncOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )