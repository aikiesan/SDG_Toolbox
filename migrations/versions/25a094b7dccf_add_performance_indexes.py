"""add_performance_indexes

Revision ID: 25a094b7dccf
Revises: caee37c95edb
Create Date: 2026-02-20 22:15:49.587155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25a094b7dccf'
down_revision = 'caee37c95edb'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes on assessments table
    op.create_index('ix_assessments_project_id', 'assessments', ['project_id'])
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])
    op.create_index('ix_assessments_status', 'assessments', ['status'])
    op.create_index('ix_assessments_project_status', 'assessments', ['project_id', 'status'])

    # Add indexes on sdg_scores table
    op.create_index('ix_sdg_scores_assessment_id', 'sdg_scores', ['assessment_id'])
    op.create_index('ix_sdg_scores_sdg_id', 'sdg_scores', ['sdg_id'])
    op.create_index('ix_sdg_scores_assessment_sdg', 'sdg_scores', ['assessment_id', 'sdg_id'])

    # Add indexes on question_responses table
    op.create_index('ix_question_responses_assessment_id', 'question_responses', ['assessment_id'])
    op.create_index('ix_question_responses_question_id', 'question_responses', ['question_id'])

    # Add index on projects table
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])


def downgrade():
    # Remove indexes from projects table
    op.drop_index('ix_projects_user_id', 'projects')

    # Remove indexes from question_responses table
    op.drop_index('ix_question_responses_question_id', 'question_responses')
    op.drop_index('ix_question_responses_assessment_id', 'question_responses')

    # Remove indexes from sdg_scores table
    op.drop_index('ix_sdg_scores_assessment_sdg', 'sdg_scores')
    op.drop_index('ix_sdg_scores_sdg_id', 'sdg_scores')
    op.drop_index('ix_sdg_scores_assessment_id', 'sdg_scores')

    # Remove indexes from assessments table
    op.drop_index('ix_assessments_project_status', 'assessments')
    op.drop_index('ix_assessments_status', 'assessments')
    op.drop_index('ix_assessments_user_id', 'assessments')
    op.drop_index('ix_assessments_project_id', 'assessments')
