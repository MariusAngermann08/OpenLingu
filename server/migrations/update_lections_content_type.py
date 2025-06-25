"""Update Lection content column to use Text type

Revision ID: update_lections_content_type
Revises: 
Create Date: 2025-06-25 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_lections_content_type'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Change the column type from String to Text
    with op.batch_alter_table('lections') as batch_op:
        batch_op.alter_column('content', type_=sa.Text())

def downgrade():
    # Revert back to String if needed (though this might truncate data)
    with op.batch_alter_table('lections') as batch_op:
        batch_op.alter_column('content', type_=sa.String())
