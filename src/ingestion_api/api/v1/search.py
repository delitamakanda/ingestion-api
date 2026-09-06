from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, session

from ingestion_api.core.config import settings
from ingestion_api.core.database import get_db
from ingestion_api.domain.search.router import SearchRouter
from ingestion_api.domain.search.schemas import SearchResponse, SearchRequest
from ingestion_api.domain.search.strategies.keyword import KeywordSearchStrategy
from ingestion_api.domain.search.strategies.text import TextSearchStrategy
from ingestion_api.llm.embeddings.base import EmbeddingService
from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService
from ingestion_api.retrieval.lexical import LexicalRetriever
from ingestion_api.retrieval.vector import VectorRetriever


def get_search_router(
        session: AsyncSession = Depends(get_db),
    ):
    retriever = LexicalRetriever(session)

    return SearchRouter(
        keyword_strategy=KeywordSearchStrategy(retriever),
        text_strategy=TextSearchStrategy(retriever),
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



# todo: remove when hybrid search is implemented
@router.post("/vector", response_model=SearchResponse)
async def vector_search(
        request: SearchRequest,
        session: AsyncSession = Depends(get_db),
):
    embedding_service = SentenceTransformerEmbeddingService(model_name=settings.embedding_model)
    retrieval = VectorRetriever(session, embedding_service=embedding_service)
    return await retrieval.search(request)