"""path_changes: one free change of the career chosen at sign-up, then requests an admin answers

Revision ID: 0014
Revises: 0013
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('path_changes', sa.Integer(), server_default='0', nullable=False))
    op.create_table(
        'path_change_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_path', sa.String(80), nullable=False),
        sa.Column('to_path', sa.String(80), nullable=False),
        sa.Column('reason', sa.String(300), server_default='', nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('decided_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status in ('pending', 'approved', 'rejected')", name='ck_path_change_requests_status'),
    )
    op.create_index('ix_path_change_requests_user', 'path_change_requests', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_path_change_requests_user', 'path_change_requests')
    op.drop_table('path_change_requests')
    op.drop_column('users', 'path_changes')
