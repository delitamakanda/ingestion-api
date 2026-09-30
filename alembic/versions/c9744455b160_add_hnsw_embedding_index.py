"""add hnsw embedding index

Revision ID: c9744455b160
Revises: 3b951bf79ab4
Create Date: 2026-09-06 12:08:02.330985

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9744455b160"
down_revision: str | Sequence[str] | None = "3b951bf79ab4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE INDEX
            ix_document_chunks_embedding_hnsw
            ON document_chunks
            USING hnsw (
            embedding vector_cosine_ops
            )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
