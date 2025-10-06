"""add contact_person model

Revision ID: 84ea5ec44d04
Revises: 46501db38e0d
Create Date: 2025-10-06 16:12:53.414069

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '84ea5ec44d04'
down_revision = '46501db38e0d'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if 'contact_person' not in tables:
        op.create_table(
            'contact_person',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.Column('full_name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=120), nullable=True),
            sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contact.id'), nullable=False)
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if 'contact_person' in tables:
        op.drop_table('contact_person')
