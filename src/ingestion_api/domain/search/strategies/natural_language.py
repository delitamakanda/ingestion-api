from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse, CitationSource, SearchResult, \
    NaturalLanguageAnswerResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy
from ingestion_api.llm.agents.query_planner import QueryPlannerAgent
from ingestion_api.llm.agents.synthesis import SynthesisAgent
from ingestion_api.llm.agents.temporal import TemporalAgent
from ingestion_api.retrieval.hybrid import HybridRetriever


class NaturalLanguageSearchStrategy(SearchStrategy):

    def __init__(self, query_planner: QueryPlannerAgent, hybrid_retriever: HybridRetriever, synthesis_agent: SynthesisAgent, temporal_agent: TemporalAgent):
        self.query_planner = query_planner
        self.hybrid_retriever = hybrid_retriever
        self.synthesis_agent = synthesis_agent
        self.temporal_agent = temporal_agent

    async def search(self, request: SearchRequest) -> SearchResponse:
        plan = await self.query_planner.plan(request)

        timeline = None

        results = await self.hybrid_retriever.search_plan(plan, limit=request.limit)

        sources = self._build_sources(results)

        if plan.requires_temporal_analysis:
            timeline = (
                await self.temporal_agent.analyze(question=request.query, sources=sources)
            )
        generated = (
            await self.synthesis_agent.synthesize(
                question=request.query,
                sources=sources,
                timeline=timeline
            )
        )
        return SearchResponse(results=[], query=request.query, mode=request.mode, total=len(results), sources=sources,answer=NaturalLanguageAnswerResponse(
            summary=generated.summary,
            claims=generated.claims,
            insufficient_information=generated.insufficient_information
        ))

    def _build_sources(self, results: list[SearchResult]) -> list[CitationSource]:
        return [
            CitationSource(
                source_id=f"S{index}",
                document_id=result.document_id,
                filename=result.filename,
                page_start=result.page_start,
                page_end=result.page_end,
                section=result.sections,
                excerpt=result.text[:200],  # Limit excerpt to first 200 characters
            ) for index, result in enumerate(results, start=1)
        ]
