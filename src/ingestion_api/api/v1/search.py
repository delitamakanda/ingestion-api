from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.database import get_db
from ingestion_api.domain.search.router import SearchRouter
from ingestion_api.domain.search.schemas import SearchResponse, SearchRequest
from ingestion_api.domain.search.strategies.keyword import KeywordSearchStrategy
from ingestion_api.domain.search.strategies.text import TextSearchStrategy
from ingestion_api.retrieval.lexical import LexicalRetriever


def get_search_router(
        session: AsyncSession = Depends(get_db)
):
    retriever = LexicalRetriever(session)

    return SearchRouter(
        keyword_strategy=KeywordSearchStrategy(retriever),
        text_strategy=TextSearchStrategy(retriever)
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