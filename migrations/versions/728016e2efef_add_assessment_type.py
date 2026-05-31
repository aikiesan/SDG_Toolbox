"""Add assessment_type

Revision ID: 728016e2efef
Revises: b2c3d4e5f6a1
Create Date: 2026-04-21 13:29:11.139487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '728016e2efef'
down_revision = 'b2c3d4e5f6a1'
branch_labels = None
depends_on = None


def upgrade():
    # NOTE: This migration was originally an auto-generated diff that re-added
    # columns the initial migration already creates (assessment_type,
    # raw_expert_data) and dropped the performance indexes added by
    # 25a094b7dccf — both unintended, and the column re-add crashed on a fresh
    # PostgreSQL database (DuplicateColumn). It now only ensures the two columns
    # exist, idempotently, and leaves the indexes in place.
    bind = op.get_bind()
    existing_columns = {c['name'] for c in sa.inspect(bind).get_columns('assessments')}

    if 'assessment_type' not in existing_columns:
        op.add_column('assessments', sa.Column(
            'assessment_type', sa.String(length=50), nullable=True, server_default='standard'))
    if 'raw_expert_data' not in existing_columns:
        op.add_column('assessments', sa.Column('raw_expert_data', sa.JSON(), nullable=True))


def downgrade():
    bind = op.get_bind()
    existing_columns = {c['name'] for c in sa.inspect(bind).get_columns('assessments')}

    if 'raw_expert_data' in existing_columns:
        op.drop_column('assessments', 'raw_expert_data')
    if 'assessment_type' in existing_columns:
        op.drop_column('assessments', 'assessment_type')
