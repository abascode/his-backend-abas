"""create_stock_pilots


Revision ID: c81896ab5bcc
Revises: dcb7f4b2feda
Create Date: 2024-11-14 23:46:27.865470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c81896ab5bcc'
down_revision: Union[str, None] = 'dcb7f4b2feda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
