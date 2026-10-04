from uuid import uuid4

import pytest

from ingestion_api.domain.jobs.enums import JobStatus, ProcessingStep
from ingestion_api.domain.jobs.repository import JobRepository


@pytest.mark.integration
async def test_create_job(db_session):
    job_repository = JobRepository(db_session)
    job = await job_repository.create_job(
        original_filename="test_file.pdf",
        stored_filename="test_storage_path.pdf",
        content_hash="test_content_hash",
    )
    await db_session.commit()
    assert job.id is not None
    assert job.status == JobStatus.PENDING
    assert job.progress == 0


@pytest.mark.integration
async def test_get_job_by_id(db_session):
    job_repository = JobRepository(db_session)
    job = await job_repository.create_job(
        original_filename="test_file.pdf",
        stored_filename="test_storage_path.pdf",
        content_hash="test_content_hash",
    )
    await db_session.commit()
    retrieved_job = await job_repository.get_job_by_id(job.id)
    assert retrieved_job is not None
    assert retrieved_job.id == job.id
    assert retrieved_job.original_filename == "test_file.pdf"
    assert retrieved_job.stored_filename == "test_storage_path.pdf"
    assert retrieved_job.content_hash == "test_content_hash"


@pytest.mark.integration
async def test_job_lifecycle(db_session):
    job_repository = JobRepository(db_session)
    job = await job_repository.create_job(
        original_filename="test_file.pdf",
        stored_filename="test_storage_path.pdf",
        content_hash="test_content_hash",
    )
    await job_repository.mark_started(job)

    assert job.started_at is not None
    assert job.attempts == 1

    await job_repository.update_job_status(
        job, step=ProcessingStep.PARSING, progress=20
    )

    assert job.progress == 20

    await job_repository.mark_completed(job)
    assert job.progress == 100
    assert job.finished_at is not None


@pytest.mark.integration
async def test_find_active_job_by_content_hash(db_session):
    job_repository = JobRepository(db_session)
    content_hash = uuid4().hex
    job = await job_repository.create_job(
        original_filename="a.pdf",
        stored_filename="a.pdf",
        content_hash=content_hash,
    )
    await db_session.commit()
    active_job = await job_repository.find_by_content_hash(content_hash)
    assert active_job is not None
    assert active_job.id == job.id


@pytest.mark.integration
async def test_completed_job_is_not_returned_as_active(db_session):
    job_repository = JobRepository(db_session)
    job = await job_repository.create_job(
        original_filename="a.pdf",
        stored_filename="a.pdf",
        content_hash="completed-content",
    )
    await job_repository.mark_completed(job)
    await db_session.commit()
    found = await job_repository.find_by_content_hash("completed-content")
    assert found is None
