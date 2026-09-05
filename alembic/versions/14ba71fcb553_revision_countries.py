"""revision countries

Revision ID: 14ba71fcb553
Revises: 012f1e3e4e87
Create Date: 2026-09-05 18:09:54.919036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '14ba71fcb553'
down_revision: Union[str, Sequence[str], None] = '012f1e3e4e87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        UPDATE documents
        SET countries = ARRAY[]::VARCHAR[]
        WHERE countries IS NULL
        """
    )

    op.alter_column(
        "documents",
        "countries",
        existing_type=postgresql.ARRAY(sa.String()),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
