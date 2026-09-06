from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, session

from ingestion_api.core.config import settings
from ingestion_api.core.database import get_db
from ingestion_api.domain.search.router import SearchRouter
from ingestion_api.domain.search.schemas import SearchResponse, SearchRequest
from ingestion_api.domain.search.strategies.keyword import KeywordSearchStrategy
from ingestion_api.domain.search.strategies.natural_language import NaturalLanguageSearchStrategy
from ingestion_api.domain.search.strategies.text import TextSearchStrategy
from ingestion_api.llm.agents.query_planner import QueryPlannerAgent
from ingestion_api.llm.agents.synthesis import SynthesisAgent
from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService
from ingestion_api.llm.providers.openai import OpenAILLMProvider
from ingestion_api.retrieval.hybrid import HybridRetriever
from ingestion_api.retrieval.lexical import LexicalRetriever
from ingestion_api.retrieval.vector import VectorRetriever

from functools import lru_cache

@lru_cache()
def get_embedding_service():
    return SentenceTransformerEmbeddingService(model_name=settings.embedding_model)

@lru_cache()
def get_llm_provider():
    return OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.llm_model)


def get_search_router(
        session: AsyncSession = Depends(get_db),
    ):
    retriever = LexicalRetriever(session)

    embedding_service = (get_embedding_service())

    vector = VectorRetriever(session, embedding_service=embedding_service)

    hybrid = HybridRetriever(lexical_retriever=retriever, vector_retriever=vector)

    llm_provider = get_llm_provider()

    query_planner = QueryPlannerAgent(llm_provider)

    synthesize_agent = SynthesisAgent(llm_provider)

    return SearchRouter(
        keyword_strategy=KeywordSearchStrategy(retriever),
        text_strategy=TextSearchStrategy(retriever),
        natural_language_strategy=NaturalLanguageSearchStrategy(query_planner,hybrid,synthesize_agent)
    )

router = APIRouter(
    prefix="/search",
    tags=["search"],)

@router.post("", response_model=SearchResponse)
async def search(
        request: SearchRequest,
        search_router: SearchRouter = Depends(get_search_router)
):
    return await search_router.search(request)
