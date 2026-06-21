"""Add tracking tables: daily_logs, body_metric_logs, user_streaks

Revision ID: a1b2c3d4e5f6
Revises: 987ae8e4f20b
Create Date: 2026-06-21 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '987ae8e4f20b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add daily_logs, body_metric_logs, and user_streaks tables."""

    # ── daily_logs ────────────────────────────────────────────────────────────
    op.create_table(
        'daily_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('completed_exercises', sa.JSON(), nullable=True),
        sa.Column('workout_plan_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_daily_logs_id'), 'daily_logs', ['id'], unique=False)
    op.create_index(op.f('ix_daily_logs_user_id'), 'daily_logs', ['user_id'], unique=False)
    # Composite unique: one log per user per date
    op.create_index(
        'uq_daily_logs_user_date',
        'daily_logs',
        ['user_id', 'log_date'],
        unique=True,
    )

    # ── body_metric_logs ──────────────────────────────────────────────────────
    op.create_table(
        'body_metric_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('logged_at', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('body_fat_pct', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_body_metric_logs_id'), 'body_metric_logs', ['id'], unique=False)
    op.create_index(op.f('ix_body_metric_logs_user_id'), 'body_metric_logs', ['user_id'], unique=False)
    # Composite unique: one body metric row per user per date
    op.create_index(
        'uq_body_metric_logs_user_date',
        'body_metric_logs',
        ['user_id', 'logged_at'],
        unique=True,
    )

    # ── user_streaks ──────────────────────────────────────────────────────────
    op.create_table(
        'user_streaks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_active_date', sa.Date(), nullable=True),
        sa.Column('total_workouts_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_user_streaks_id'), 'user_streaks', ['id'], unique=False)


def downgrade() -> None:
    """Drop tracking tables."""
    op.drop_index(op.f('ix_user_streaks_id'), table_name='user_streaks')
    op.drop_table('user_streaks')

    op.drop_index('uq_body_metric_logs_user_date', table_name='body_metric_logs')
    op.drop_index(op.f('ix_body_metric_logs_user_id'), table_name='body_metric_logs')
    op.drop_index(op.f('ix_body_metric_logs_id'), table_name='body_metric_logs')
    op.drop_table('body_metric_logs')

    op.drop_index('uq_daily_logs_user_date', table_name='daily_logs')
    op.drop_index(op.f('ix_daily_logs_user_id'), table_name='daily_logs')
    op.drop_index(op.f('ix_daily_logs_id'), table_name='daily_logs')
    op.drop_table('daily_logs')
