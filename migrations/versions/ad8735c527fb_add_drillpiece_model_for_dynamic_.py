"""Add DrillPiece model for dynamic practice structure

Revision ID: ad8735c527fb
Revises: 688824474a73
Create Date: 2025-09-09 16:06:54.353235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad8735c527fb'
down_revision = '688824474a73'
branch_labels = None
depends_on = None


def upgrade():
    # Create drill_piece table (only if it doesn't exist)
    try:
        op.create_table('drill_piece',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('time', sa.String(length=50), nullable=False),
            sa.Column('drill_name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('link_attachment', sa.String(length=500), nullable=True),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('practice_plan_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['practice_plan_id'], ['practice_plan.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    except Exception:
        # Table already exists, skip creation
        pass


def downgrade():
    # Drop drill_piece table
    op.drop_table('drill_piece')
