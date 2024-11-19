"""first_migration

Revision ID: ec0a081a5fa0
Revises: 
Create Date: 2024-11-19 11:55:34.434059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec0a081a5fa0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('va_categories',
    sa.Column('id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_dealers',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_monthly_targets',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('month', sa.String(), nullable=False),
    sa.Column('year', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.Column('deleted_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deletable', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_segments',
    sa.Column('id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_forecasts',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('dealer_id', sa.String(length=255), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.Column('deleted_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deletable', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['dealer_id'], ['va_dealers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_models',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('manufacture_code', sa.String(length=255), nullable=False),
    sa.Column('group', sa.String(length=255), nullable=False),
    sa.Column('variant', sa.String(length=255), nullable=False),
    sa.Column('category_id', sa.String(length=255), nullable=False),
    sa.Column('segment_id', sa.String(length=255), nullable=False),
    sa.Column('usage', sa.String(length=255), nullable=False),
    sa.Column('euro', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['va_categories.id'], ),
    sa.ForeignKeyConstraint(['segment_id'], ['va_segments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_monthly_target_details',
    sa.Column('month_target_id', sa.String(), nullable=False),
    sa.Column('forecast_month', sa.String(), nullable=False),
    sa.Column('dealer_id', sa.String(), nullable=False),
    sa.Column('target', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.Column('deleted_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deletable', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['va_categories.id'], ),
    sa.ForeignKeyConstraint(['dealer_id'], ['va_dealers.id'], ),
    sa.ForeignKeyConstraint(['month_target_id'], ['va_monthly_targets.id'], ),
    sa.PrimaryKeyConstraint('month_target_id')
    )
    op.create_table('va_forecast_details',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('forecast_id', sa.String(), nullable=False),
    sa.Column('model_id', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.Column('deleted_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deletable', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['forecast_id'], ['va_forecasts.id'], ),
    sa.ForeignKeyConstraint(['model_id'], ['va_models.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('va_forecast_detail_months',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('forecast_detail_id', sa.String(), nullable=False),
    sa.Column('forecast_month', sa.String(), nullable=False),
    sa.Column('rs_gov', sa.Integer(), nullable=False),
    sa.Column('ws_gov', sa.Integer(), nullable=False),
    sa.Column('rs_priv', sa.Integer(), nullable=False),
    sa.Column('ws_priv', sa.Integer(), nullable=False),
    sa.Column('total_rs', sa.Integer(), nullable=False),
    sa.Column('prev_rs_gov', sa.Integer(), nullable=False),
    sa.Column('prev_rs_priv', sa.Integer(), nullable=False),
    sa.Column('total_prev_rs', sa.Integer(), nullable=False),
    sa.Column('total_ws', sa.Integer(), nullable=False),
    sa.Column('total_prev_final_conf_allocation', sa.Integer(), nullable=False),
    sa.Column('new_ws_req', sa.Integer(), nullable=False),
    sa.Column('hmsi_allocation', sa.Integer(), nullable=False),
    sa.Column('adjustment', sa.Integer(), nullable=False),
    sa.Column('confirmed_prev_final_ws_gov', sa.Integer(), nullable=False),
    sa.Column('confirmed_prev_final_ws_priv', sa.Integer(), nullable=False),
    sa.Column('confirmed_ws_gov', sa.Integer(), nullable=False),
    sa.Column('confirmed_ws_priv', sa.Integer(), nullable=False),
    sa.Column('confirmed_total_ws', sa.Integer(), nullable=False),
    sa.Column('confirmed_final_gov', sa.Integer(), nullable=False),
    sa.Column('confirmed_final_priv', sa.Integer(), nullable=False),
    sa.Column('confirmed_total_final_ws', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.Column('deleted_by', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deletable', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['forecast_detail_id'], ['va_forecast_details.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('va_forecast_detail_months')
    op.drop_table('va_forecast_details')
    op.drop_table('va_monthly_target_details')
    op.drop_table('va_models')
    op.drop_table('va_forecasts')
    op.drop_table('va_segments')
    op.drop_table('va_monthly_targets')
    op.drop_table('va_dealers')
    op.drop_table('va_categories')
    # ### end Alembic commands ###