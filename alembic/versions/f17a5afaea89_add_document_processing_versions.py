"""add document processing versions

Revision ID: f17a5afaea89
Revises: 4f9ee61da440
Create Date: 2026-09-20 22:05:50.551173

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "f17a5afaea89"
down_revision: str | Sequence[str] | None = "4f9ee61da440"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
