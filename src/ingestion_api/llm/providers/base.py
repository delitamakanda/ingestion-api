from abc import ABC, abstractmethod
from typing import TypeVar

from narwhals import schema
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    @abstractmethod
    async def structured(self, *, system_prompt: str, user_prompt: str, schema: type[T],) -> T:
        ...

    @abstractmethod
    async def generate_text(self, *, system_prompt: str, user_prompt: str,) -> str:
        ...