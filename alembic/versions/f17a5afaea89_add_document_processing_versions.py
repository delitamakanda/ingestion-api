"""add document processing versions

Revision ID: f17a5afaea89
Revises: 4f9ee61da440
Create Date: 2026-09-20 22:05:50.551173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f17a5afaea89'
down_revision: Union[str, Sequence[str], None] = '4f9ee61da440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
