from pydantic import BaseModel, Field

from ingestion_api.domain.search.enums import SearchMode

class ExpectedResults(BaseModel):
    """
    Model representing the expected results for a search query.
    """

    document_ids: list[str] = Field(default_factory=list, description="The IDs of the documents expected to be returned.")
    chunks_ids: list[str] = Field(default_factory=list, description="The IDs of the chunks expected to be returned.")
    terms: list[str] = Field(default_factory=list, description="The terms expected to be returned.")


class EvaluationCase(BaseModel):
    """
    Model representing an evaluation case for a search query.
    """
    id: str = Field(..., description="The ID of the evaluation case.")
    query: str = Field(..., description="The search query to be evaluated.")
    expected: ExpectedResults = Field(..., description="The expected results for the search query.")
    mode: SearchMode = Field(..., description="The search mode to be used for the evaluation case.")
    countries: list[str] = Field(default_factory=list, description="The countries to be considered for the evaluation case.")
    chunks_ids: list[str] = Field(default_factory=list, description="The IDs of the chunks to be considered for the evaluation case.")
    document_ids: list[str] = Field(default_factory=list, description="The IDs of the documents to be considered for the evaluation case.")
    terms: list[str] = Field(default_factory=list, description="The terms to be considered for the evaluation case.")

    def model_post_init(self, __context) -> None:
        if not self.chunks_ids:
            self.chunks_ids = self.expected.chunks_ids
        if not self.document_ids:
            self.document_ids = self.expected.document_ids
        if not self.terms:
            self.terms = self.expected.terms

class EvaluationResult(BaseModel):
    """
    Model representing the result of an evaluation case.
    """
    case_id: str = Field(..., description="The ID of the evaluation case.")
    recall_at_5: float = Field(..., description="The recall at 5 for the evaluation case.")
    recall_at_10: float = Field(..., description="The recall at 10 for the evaluation case.")
    precision_at_5: float = Field(..., description="The precision at 5 for the evaluation case.")
    reciprocal_rank: float = Field(..., description="The reciprocal rank for the evaluation case.")
    term_hit_rate: float = Field(..., description="The term hit rate for the evaluation case.")
    retrieved_chunks_ids: list[str] = Field(default_factory=list, description="The IDs of the chunks retrieved for the evaluation case.")