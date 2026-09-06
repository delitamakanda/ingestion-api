from openai import AsyncOpenAI
from pydantic import BaseModel

from ingestion_api.llm.providers.base import LLMProvider, T


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
        response = (await self.client.responses.parse(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text_format=schema,
        ))
        return response.output_parsed

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        response = (await self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        ))
        return response.output_text