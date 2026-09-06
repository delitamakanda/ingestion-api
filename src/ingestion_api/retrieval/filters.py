from ingestion_api.domain.documents.models import Document

from ingestion_api.domain.search.schemas import SearchRequest


def apply_search_filters(
        statement, request: SearchRequest
):
    if request.countries:
        statement = statement.where(Document.countries.overlap(request.countries))

    if request.start_date:
        statement = statement.where(Document.publication_date >= request.start_date)

    if request.end_date:
        statement = statement.where(Document.publication_date <= request.end_date)
    return statement