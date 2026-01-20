"""update 

Revision ID: 4370a7dc2054
Revises: d4fea00b69e0
Create Date: 2025-12-18 10:41:05.964388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '4370a7dc2054'
down_revision: Union[str, Sequence[str], None] = 'd4fea00b69e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
