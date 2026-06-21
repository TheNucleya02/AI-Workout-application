"""Add plan_feedbacks table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-21 20:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add plan_feedbacks table."""
    op.create_table(
        'plan_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_type', sa.String(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=False),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        # Intentionally NOT a FK to workout_plans/nutrition_plans — source_plan_id
        # is stored as plain int so the feedback record survives if a plan is deleted.
        sa.Column('source_plan_id', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_plan_feedbacks_id'), 'plan_feedbacks', ['id'], unique=False)
    op.create_index(op.f('ix_plan_feedbacks_user_id'), 'plan_feedbacks', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop plan_feedbacks table."""
    op.drop_index(op.f('ix_plan_feedbacks_user_id'), table_name='plan_feedbacks')
    op.drop_index(op.f('ix_plan_feedbacks_id'), table_name='plan_feedbacks')
    op.drop_table('plan_feedbacks')
