from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class SearchIntent(StrEnum):
    FACTUAL = "factual"
    COMPARISON = "comparison"
    REGULATORY = "regulatory"
    TEMPORAL = "temporal"
    REGULATORY_COMPARISON = "regulatory_comparison"


class SearchPlan(BaseModel):
    int: SearchIntent = Field(..., description="The intent of the search")

    queries: list[str] = Field(min_length=1, max_length=10, description="The list of queries to search for")

    countries: list[str] = Field(default_factory=list, description="The list of countries to search in")

    topics: list[str] = Field(default_factory=list, description="The list of topics to search for")

    legal_references: list[str] = Field(default_factory=list, description="The list of legal references to search for")

    requires_temporal_analysis: bool = Field(default=False, description="Whether temporal analysis is required")

    start_date: date | None = Field(None, description="The start date of the search")

    end_date: date | None = Field(None, description="The end date of the search")


class AnswerClaim(BaseModel):
    text: str = Field(..., description="The text of the claim")
    source_ids: list[str] = Field(..., description="The IDs of the sources")


class GeneratedAnswer(BaseModel):
    summary: str = Field(..., description="The summary of the answer")
    claims: list[AnswerClaim] = Field(default_factory=list, description="The list of citations in the answer")
    insufficient_information: bool = Field(default=False, description="Whether the answer is insufficient information")
