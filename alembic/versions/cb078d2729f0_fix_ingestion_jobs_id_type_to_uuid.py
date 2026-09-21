"""fix ingestion jobs id type to uuid

Revision ID: cb078d2729f0
Revises: c40de304ae0c
Create Date: 2026-09-21 00:42:22.772282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cb078d2729f0'
down_revision: Union[str, Sequence[str], None] = 'c40de304ae0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The 4c2d6a1154b6 "restore ingestion jobs" migration recreated this table
    # with `id` as VARCHAR(36) instead of UUID, which mismatches the ORM
    # model (UUID(as_uuid=True)) and breaks lookups like
    # `WHERE ingestion_jobs.id = $1::UUID`.
    op.alter_column(
        'ingestion_jobs',
        'id',
        type_=postgresql.UUID(as_uuid=True),
        existing_type=sa.String(length=36),
        postgresql_using='id::uuid',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'ingestion_jobs',
        'id',
        type_=sa.String(length=36),
        existing_type=postgresql.UUID(as_uuid=True),
        postgresql_using='id::varchar',
    )
