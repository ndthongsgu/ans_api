"""alter stalls cover_image to text

Revision ID: f9a2d5c6e1b4
Revises: c4f7b9d2a1e0
Create Date: 2026-03-23 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9a2d5c6e1b4"
down_revision: Union[str, Sequence[str], None] = "c4f7b9d2a1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "stalls",
        "cover_image",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "stalls",
        "cover_image",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
