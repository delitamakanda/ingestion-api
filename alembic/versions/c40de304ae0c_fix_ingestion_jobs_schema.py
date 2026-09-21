"""fix ingestion jobs schema

Revision ID: c40de304ae0c
Revises: 4c2d6a1154b6
Create Date: 2026-09-21 00:00:22.275175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c40de304ae0c'
down_revision: Union[str, Sequence[str], None] = '4c2d6a1154b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'ingestion_jobs',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True, index=True)
    )

    op.create_foreign_key(
        'fk_ingestion_jobs_document_id_documents',
        'ingestion_jobs', 'documents',
        ['document_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'fk_ingestion_jobs_document_id_documents',
        'ingestion_jobs',
        type_='foreignkey'
    )
    op.drop_column('ingestion_jobs', 'document_id')
