"""Add execution error classification

Revision ID: e28cc6ef2e28
Revises: 33a6b124c3f2
Create Date: 2026-11-20 19:33:51.560077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e28cc6ef2e28'
down_revision: Union[str, Sequence[str], None] = '33a6b124c3f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE executionstatus ADD VALUE IF NOT EXISTS 'TIMED_OUT'"
    )

    op.add_column(
        'executions',
        sa.Column('error_type', sa.String(length=30), nullable=True)
    )

    op.add_column(
        'executions',
        sa.Column('exception_type', sa.String(length=100), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('executions', 'exception_type')
    op.drop_column('executions', 'error_type')