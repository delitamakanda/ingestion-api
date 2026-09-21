"""add document processing versions

Revision ID: 09e8d2408d4a
Revises: f17a5afaea89
Create Date: 2026-09-20 22:13:47.023012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09e8d2408d4a'
down_revision: Union[str, Sequence[str], None] = 'f17a5afaea89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
