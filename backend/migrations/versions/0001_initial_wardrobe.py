"""Initial wardrobe_items migration

Revision ID: 0001_initial_wardrobe
Revises: 
Create Date: 2026-09-03 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_wardrobe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wardrobe_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('color_name', sa.String(length=50), nullable=True),
        sa.Column('reds', sa.Integer(), nullable=False, default=0),
        sa.Column('green', sa.Integer(), nullable=False, default=0),
        sa.Column('blue', sa.Integer(), nullable=False, default=0),
        sa.Column('hue', sa.Float(), nullable=False, default=0.0),
        sa.Column('strap_reds', sa.Integer(), nullable=True),
        sa.Column('strap_green', sa.Integer(), nullable=True),
        sa.Column('strap_blue', sa.Integer(), nullable=True),
        sa.Column('strap_hue', sa.Float(), nullable=True),
        sa.Column('dial_reds', sa.Integer(), nullable=True),
        sa.Column('dial_green', sa.Integer(), nullable=True),
        sa.Column('dial_blue', sa.Integer(), nullable=True),
        sa.Column('dial_hue', sa.Float(), nullable=True),
        sa.Column('formality', sa.Float(), nullable=False, default=5.0),
        sa.Column('vibe', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_name')
    )
    op.create_index(op.f('ix_wardrobe_items_id'), 'wardrobe_items', ['id'], unique=False)
    op.create_index(op.f('ix_wardrobe_items_item_name'), 'wardrobe_items', ['item_name'], unique=True)
    op.create_index(op.f('ix_wardrobe_items_type'), 'wardrobe_items', ['type'], unique=False)
    op.create_index(op.f('ix_wardrobe_items_category'), 'wardrobe_items', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_wardrobe_items_category'), table_name='wardrobe_items')
    op.drop_index(op.f('ix_wardrobe_items_type'), table_name='wardrobe_items')
    op.drop_index(op.f('ix_wardrobe_items_item_name'), table_name='wardrobe_items')
    op.drop_index(op.f('ix_wardrobe_items_id'), table_name='wardrobe_items')
    op.drop_table('wardrobe_items')
