"""change embedding dimension to 768

Revision ID: 3b951bf79ab4
Revises: 10ce27eafa4e
Create Date: 2026-09-06 11:31:40.531124

"""
from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3b951bf79ab4'
down_revision: str | Sequence[str] | None = '10ce27eafa4e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column(
        "document_chunks",
        "embedding",
    )

    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            Vector(dim=768),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
