"""update database

Revision ID: d4fea00b69e0
Revises: 8c9733b397da
Create Date: 2025-12-18 10:37:41.872617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'd4fea00b69e0'
down_revision: Union[str, Sequence[str], None] = '8c9733b397da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
