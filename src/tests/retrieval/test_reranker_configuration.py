from unittest.mock import Mock

import pytest

from ingestion_api.api.v1 import search


@pytest.mark.unit
def test_empty_reranker_model_disables_reranker(monkeypatch):
    monkeypatch.setattr(search.settings, "reranker_model", "")
    monkeypatch.setattr(search, "get_embedding_service", Mock())
    monkeypatch.setattr(search, "get_llm_provider", Mock())
    reranker_factory = Mock()
    monkeypatch.setattr(search, "CrossEncoderReranker", reranker_factory)
    hybrid_factory = Mock()
    monkeypatch.setattr(search, "HybridRetriever", hybrid_factory)

    search.get_search_router(session=object())

    reranker_factory.assert_not_called()
    assert hybrid_factory.call_args.kwargs["reranker"] is None
