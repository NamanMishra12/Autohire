from app.llms.client import get_llm_client
from app.core.config import settings
from app.utils.logger import logger


async def llm_call(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 1000,
) -> str:
    """
    Makes a single LLM call and returns the response text.
    All agents go through here — one place to add logging,
    retries, and cost tracking later.
    """
    client = get_llm_client()

    logger.debug(f"LLM call | provider={settings.LLM_PROVIDER} model={settings.LLM_MODEL}")

    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    result = response.choices[0].message.content.strip()

    logger.debug(f"LLM response tokens: {response.usage.total_tokens}")

    return result