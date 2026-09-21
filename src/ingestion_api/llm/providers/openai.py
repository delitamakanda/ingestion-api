import time

from openai import AsyncOpenAI
from ingestion_api.core.logging import get_logger
from ingestion_api.llm.providers.base import LLMProvider, T

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
        response = (await self.client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text_format=schema,
        ))
        logger.info("openai_llm_provider.structured.completed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
        return response.output_parsed

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        start_time = time.perf_counter()
        response = (await self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        ))
        logger.info("openai_llm_provider.generate_text.completed", system_prompt=system_prompt, user_prompt=user_prompt, elapsed=(time.perf_counter() - start_time) * 1000)
        return response.output_text