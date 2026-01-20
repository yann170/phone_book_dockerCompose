"""uuid for user model

Revision ID: a529b5f4d108
Revises: ac6e049908ad
Create Date: 2025-10-17 14:58:37.160478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a529b5f4d108'
down_revision: Union[str, Sequence[str], None] = 'ac6e049908ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
