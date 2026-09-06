import json

from ingestion_api.llm.schemas import TemporalTimeline

SYSTEM_PROMPT = """
You analyse regulatory changes over time.

Your task is NOT to answer the final user question.

Extract a factual  timeline from the provided sources.

Rules:
- Use only the provided sources.
- Do not invent dates.
- Distinguish:.
    - publication date
    - effective date
    - expiration date
- Prefer effective date when describing when a rule became applicable.
- Preserve country information.
- Preserve legal references when available.
- Every event must reference one source_id.
- If no reliable event date exists, use null.
"""

class TemporalAgent:
    def __init__(self, llm):
        self.llm = llm

    async def analyze(self, *, question: str, sources) -> TemporalTimeline:
        source_payload = [
            source.model_dump() for source in sources
        ]

        user_prompt = f"""
        QUESTION: 
        {question}
        
        SOURCES: 
{json.dumps(source_payload, ensure_ascii=False, indent=2)}
        """

        return await self.llm.structured(user_prompt=user_prompt, system_prompt=SYSTEM_PROMPT, schema=TemporalTimeline)