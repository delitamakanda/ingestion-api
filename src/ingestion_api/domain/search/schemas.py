from datetime import date
from pydantic import BaseModel, Field

from ingestion_api.domain.search.enums import SearchMode

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string")
    mode: SearchMode = Field(..., description="The mode of the search")
    countries: list[str] = Field(default_factory=list, description="The list of countries to search in")
    start_date: date | None = Field(None, description="The start date of the search")
    end_date: date | None = Field(None, description="The end date of the search")
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

class SearchResult(BaseModel):
    document_id: str = Field(..., description="The ID of the document")
    chunk_id: str = Field(..., description="The ID of the chunk")
    filename: str = Field(..., description="The filename of the document")
    chunk_index: int = Field(..., description="The index of the chunk in the document")
    sections: str = Field(..., description="The section of the document")
    page_start: int | None = Field(..., description="The start page of the chunk")
    page_end: int | None = Field(..., description="The end page of the chunk")
    text: str = Field(..., description="The text of the document")
    score: float = Field(..., description="The relevance score of the document")

class SearchResponse(BaseModel):
    query: str = Field(..., description="The search query string")
    mode: SearchMode = Field(..., description="The mode of the search")
    results: list[SearchResult] = Field(..., description="The list of search results")
    total: int = Field(..., description="The total number of results")
