"""add missing document chunks search vector index

Revision ID: dcc157bbf9e4
Revises: fcdc2c58f662
Create Date: 2026-10-01 23:31:34.519382

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dcc157bbf9e4'
down_revision: str | Sequence[str] | None = 'fcdc2c58f662'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_document_chunks_search_vector",
        "document_chunks",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_document_chunks_search_vector",
        table_name="document_chunks",
        if_exists=True,
    )
