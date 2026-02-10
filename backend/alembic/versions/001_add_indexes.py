"""Add missing composite indexes for load testing

Revision ID: 001_add_indexes
Create Date: 2026-02-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. CRITICAL: Partial Index for finding the "Current Placeholder Question"
    # This makes the query "WHERE session_id=X AND user_answer IS NULL" instant.
    op.create_index(
        'ix_response_todo_item',
        'responses',
        ['session_id', 'user_answer'],
        postgresql_where=sa.text("user_answer IS NULL")
    )
    
    # 2. CRITICAL: Composite Index for joining Responses <-> Questions
    # You query by session_id and question_id frequently in "submit_answer"
    op.create_index(
        'ix_response_session_question',
        'responses',
        ['session_id', 'question_id']
    )
    
    # 3. FIXED: Index on QUESTIONS table for Calibration Status
    # Claude put this on 'responses' by mistake. It belongs on 'questions'.
    # This helps when selecting "operational" vs "pretest" items.
    op.create_index(
        'ix_questions_calibration',
        'questions',
        ['calibration_status']
    )

def downgrade() -> None:
    op.drop_index('ix_questions_calibration', table_name='questions')
    op.drop_index('ix_response_session_question', table_name='responses')
    op.drop_index('ix_response_todo_item', table_name='responses')