"""usernames: log in with a username; the email is kept only for recovery. Also password reset codes.

Revision ID: 0015
Revises: 0014
"""
import re

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(20), nullable=True))
    # Existing accounts get a username from the start of their email, made unique
    connection = op.get_bind()
    taken = set()
    for user_id, email in connection.execute(sa.text("select id, email from users order by created_at")).all():
        base = re.sub(r"[^a-z0-9_.]", "", email.split("@")[0].lower())[:16] or "student"
        if len(base) < 3:
            base = (base + "user")[:16]
        name, number = base, 1
        while name in taken:
            number += 1
            name = f"{base[:16]}{number}"
        taken.add(name)
        connection.execute(sa.text("update users set username = :name where id = :id"), {"name": name, "id": user_id})
    op.alter_column('users', 'username', nullable=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_check_constraint('ck_users_username_lowercase', 'users', 'username = lower(username)')

    op.create_table(
        'password_resets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_password_resets_user', 'password_resets', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_password_resets_user', 'password_resets')
    op.drop_table('password_resets')
    op.drop_constraint('ck_users_username_lowercase', 'users')
    op.drop_index('ix_users_username', 'users')
    op.drop_column('users', 'username')
