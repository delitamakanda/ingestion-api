"""add trigram search index

Revision ID: bd9fff6f9535
Revises: 4c29abd55148
Create Date: 2026-09-05 17:25:38.339940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd9fff6f9535'
down_revision: Union[str, Sequence[str], None] = '4c29abd55148'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_document_chunks_text_trgm",
        "document_chunks",
        ["text"],
        postgresql_using="gin",
        postgresql_ops={
            "text": "gin_trgm_ops"
        },
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
