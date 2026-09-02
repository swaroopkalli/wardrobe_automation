"""Add missing layer_index column to wardrobe_items.

Revision ID: 0002_layer_index
Revises: 0001_initial_wardrobe
Create Date: 2026-09-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002_layer_index'
down_revision: Union[str, None] = '0001_initial_wardrobe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'wardrobe_items',
        sa.Column('layer_index', sa.Integer(), nullable=False, server_default='0')
    )
    op.alter_column('wardrobe_items', 'layer_index', server_default=None)


def downgrade() -> None:
    op.drop_column('wardrobe_items', 'layer_index')
