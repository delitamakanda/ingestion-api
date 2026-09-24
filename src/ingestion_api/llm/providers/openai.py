import time
from typing import Any

from openai import AsyncOpenAI
from ingestion_api.core.logging import get_logger
from ingestion_api.llm.providers.base import LLMProvider, T
from ingestion_api.core.metrics import LLM_REQUESTS_TOTAL, LLM_DURATION_SECONDS

logger = get_logger(__name__)

class OpenAILLMProvider(LLMProvider):

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def structured(
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            schema: type[T]
    ) -> T:
        start_time = time.perf_counter()
        try:
            response = (await self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                text_format=schema,
            ))
        except Exception:
            logger.exception("openai_llm_provider.structured.failed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
            LLM_REQUESTS_TOTAL.labels('failed').inc()
            LLM_DURATION_SECONDS.observe((time.perf_counter() - start_time) * 1000)
            return None
        logger.info("openai_llm_provider.structured.completed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
        LLM_REQUESTS_TOTAL.labels('completed').inc()
        LLM_DURATION_SECONDS.observe((time.perf_counter() - start_time) * 1000)
        return response.output_parsed

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        start_time = time.perf_counter()
        try:
            response = (await self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
            ))
        except Exception:
            logger.exception("openai_llm_provider.generate_text.failed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
            LLM_REQUESTS_TOTAL.labels('failed').inc()
            LLM_DURATION_SECONDS.observe((time.perf_counter() - start_time) * 1000)
            return ''
        logger.info("openai_llm_provider.generate_text.completed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
        LLM_REQUESTS_TOTAL.labels('completed').inc()
        LLM_DURATION_SECONDS.observe((time.perf_counter() - start_time) * 1000)
        return response.output_text