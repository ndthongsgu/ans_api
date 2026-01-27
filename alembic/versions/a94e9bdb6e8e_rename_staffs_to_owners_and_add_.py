"""Rename staffs to owners and add subscription_packages

Revision ID: a94e9bdb6e8e
Revises: 3dfaef9be011
Create Date: 2026-01-26 16:06:31.824566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a94e9bdb6e8e'
down_revision: str = '3dfaef9be011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename staffs table to owners
    op.rename_table('staffs', 'owners')

    # Add subscription_package_id to owners
    op.add_column('owners', sa.Column('subscription_package_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(None, 'owners', 'subscription_packages', ['subscription_package_id'], ['id'])

    # Rename staff_id to owner_id in stalls
    op.alter_column('stalls', 'staff_id', new_column_name='owner_id')

    # Update FK
    op.drop_constraint('fk_stalls_staff_id_staffs', 'stalls', type_='foreignkey')
    op.create_foreign_key(None, 'stalls', 'owners', ['owner_id'], ['id'])

    # Create subscription_packages table
    op.create_table('subscription_packages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('max_stalls', sa.Integer(), nullable=False),
    sa.Column('features', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop subscription_packages table
    op.drop_table('subscription_packages')

    # Remove FK and column from owners
    op.drop_constraint(None, 'owners', type_='foreignkey')  # assuming the FK name
    op.drop_column('owners', 'subscription_package_id')

    # Rename back owner_id to staff_id in stalls
    op.alter_column('stalls', 'owner_id', new_column_name='staff_id')

    # Update FK back
    op.drop_constraint(None, 'stalls', type_='foreignkey')
    op.create_foreign_key(None, 'stalls', 'staffs', ['staff_id'], ['id'])

    # Rename owners table back to staffs
    op.rename_table('owners', 'staffs')
