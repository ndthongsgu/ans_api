"""add close_hours to stalls

Revision ID: c4f7b9d2a1e0
Revises: b3e9015173cc
Create Date: 2026-03-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4f7b9d2a1e0"
down_revision: Union[str, Sequence[str], None] = "b3e9015173cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stalls", sa.Column("close_hours", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("stalls", "close_hours")
