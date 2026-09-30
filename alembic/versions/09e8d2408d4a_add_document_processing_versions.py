"""add document processing versions

Revision ID: 09e8d2408d4a
Revises: f17a5afaea89
Create Date: 2026-09-20 22:13:47.023012

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '09e8d2408d4a'
down_revision: str | Sequence[str] | None = 'f17a5afaea89'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
