from ingestion_api.domain.search.schemas import SearchRequest
from ingestion_api.llm.schemas import SearchPlan

SYSTEM_PROMPT = """
You are a search planner for a search engine. based on the following search request.

Your role is NOT to answer the user's question.

Your only task is to generate a retrieval plan.

Rules:
- Never invent countries that were not mentioned in the search request.
- Respect explicit date filters.
- Detect regulatory and legal references
- Generate  several concise retrieval queries when this improves recall.
- Queries may use the language of relevant countries when useful.
- Mark requires_temporal_analysis=true when the question asks about evolution, changes, history, before/after, or a period.
- Do not provide an answer to the question.
"""

class QueryPlannerAgent:

    def __init__(self, llm):
        self.llm = llm

    async def plan(self, request: SearchRequest) -> SearchPlan:
        user_prompt = f"""
        Question: {request.query}
        
        Explicit countries: {request.countries}
        
        Explicit start date: {request.start_date}
        
        Explicit end date: {request.end_date}
        """

        plan = await self.llm.structured(user_prompt=user_prompt, system_prompt=SYSTEM_PROMPT,schema=SearchPlan)

        return self._apply_explicit_filters(plan, request)

    def _apply_explicit_filters(self, plan: SearchPlan, request: SearchRequest) -> SearchPlan:
        if request.countries:
            plan.countries = request.countries
        if request.start_date:
            plan.start_date = request.start_date
        if request.end_date:
            plan.end_date = request.end_date
        return plan
