"""add_calculation_so

Revision ID: 30c8018ac0a7
Revises: 11b549bf94e9
Create Date: 2024-12-17 17:43:00.503369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30c8018ac0a7'
down_revision: Union[str, None] = '11b549bf94e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('va_forecast_details_archive', 'deletable')
    op.add_column('va_slot_calculation_details', sa.Column('so', sa.Integer(), server_default=sa.text('0'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('va_slot_calculation_details', 'so')
    op.add_column('va_forecast_details_archive', sa.Column('deletable', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
