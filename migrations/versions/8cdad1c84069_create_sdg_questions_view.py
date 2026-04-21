"""Create sdg_questions_view

Revision ID: 8cdad1c84069
Revises: 32f963355613
Create Date: 2025-06-23 12:15:25.333977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cdad1c84069'
down_revision = '32f963355613'
branch_labels = None
depends_on = None


def upgrade():
    # Check database dialect to use appropriate syntax
    bind = op.get_bind()
    
    if bind.engine.name == 'postgresql':
        # PostgreSQL supports CREATE OR REPLACE VIEW
        op.execute("""
            CREATE OR REPLACE VIEW sdg_questions_view AS
            SELECT q.id, q.text, q.type, q.sdg_id as primary_sdg_id, 
                   g.number as sdg_number, g.name as sdg_name, q.max_score
            FROM sdg_questions q
            JOIN sdg_goals g ON q.sdg_id = g.id
        """)
    elif bind.engine.name == 'sqlite':
        # SQLite requires DROP first, then CREATE
        op.execute("DROP VIEW IF EXISTS sdg_questions_view")
        op.execute("""
            CREATE VIEW sdg_questions_view AS
            SELECT q.id, q.text, q.type, q.sdg_id as primary_sdg_id, 
                   g.number as sdg_number, g.name as sdg_name, q.max_score
            FROM sdg_questions q
            JOIN sdg_goals g ON q.sdg_id = g.id
        """)


def downgrade():
    op.execute("DROP VIEW IF EXISTS sdg_questions_view")
