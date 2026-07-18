from __future__ import annotations

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

MODELS: tuple[str, ...] = (
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "stepfun/step-3.5-flash:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "qwen/qwen3-coder:free",
)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def build_headers(api_key: str) -> dict[str, str]:
    """Builds request headers for local OpenRouter smoke tests."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kagandms",
        "X-Title": "TarihBot",
    }


def get_api_key() -> str:
    """Reads the OpenRouter API key from the environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required for local AI smoke tests.")
    return api_key


async def run_ai_models_smoke_test() -> None:
    """Runs local smoke tests against a small set of OpenRouter models."""
    headers = build_headers(get_api_key())

    async with httpx.AsyncClient() as client:
        for model in MODELS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Tarihte bugün 25.1.1996 test et."}
                ],
            }
            logger.info("Testing %s", model)
            try:
                response = await client.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=5.0,
                )
                logger.info("Status: %s", response.status_code)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"][:50]
                    logger.info("Preview: %s...", content)
                else:
                    error_message = response.json().get("error", {}).get("message", "")
                    logger.error("API error: %s", error_message)
            except Exception:
                logger.exception("Model test failed for %s", model)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    asyncio.run(run_ai_models_smoke_test())
