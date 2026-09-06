import json
from ingestion_api.llm.schemas import GeneratedAnswer

SYSTEM_PROMPT = """
Your are a regulatory knowledge assistant.

Answer only from the provided sources.

Rules:

1. Do not use outside knwledge.
2. Every factual claim must be supported by one or more source identifiers.
3. Never invent a source identifier.
4. If the provided sources are insufficient, set insufficient_information=true.
5. Distinguish clearly between countries.
6. Distinguish publication date from effective date when the sourcce allows it.
7. When sourcs conflict, mention the conflict.
8. Do not treat a commentary document as equivalent to primary legislation.
"""

class SynthesisAgent:
    def __init__(self, llm):
        self.llm = llm

    async def synthesize(self, *, question: str, sources) -> GeneratedAnswer:
        source_payload = [
            source.model_dump() for source in sources
        ]

        user_prompt = f"""
        QUESTION: {question}
        
        SOURCES: {json.dumps(source_payload, ensure_ascii=False, indent=2)}
        """

        return await self.llm.structured(user_prompt=user_prompt, system_prompt=SYSTEM_PROMPT, schema=GeneratedAnswer)