"""update_segment_table

Revision ID: 2231e49ab5da
Revises: aab6bc0a44c3
Create Date: 2024-11-13 06:00:15.446331

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2231e49ab5da"
down_revision: Union[str, None] = "aab6bc0a44c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'va_segment',
        sa.Column('month', sa.Integer(), nullable=False),
    )
    op.add_column(
        'va_segment',
        sa.Column('year', sa.Integer(), nullable=False),
    )
    op.alter_column(
        'va_segment',
        'category_id',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'va_segment',
        'category_id',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.drop_column('va_segment', 'month')
    op.drop_column('va_segment', 'year')
