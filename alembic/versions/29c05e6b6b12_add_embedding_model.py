"""add embedding model

Revision ID: 29c05e6b6b12
Revises: 09e8d2408d4a
Create Date: 2026-09-20 22:43:06.857320

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "29c05e6b6b12"
down_revision: str | Sequence[str] | None = "09e8d2408d4a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "documents",
        sa.Column("embedding_model", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("documents", "embedding_model")
