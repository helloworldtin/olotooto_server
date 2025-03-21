"""fix tag table

Revision ID: abb2cc9582a6
Revises: 79c0f92df837
Create Date: 2025-02-26 05:03:57.062450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'abb2cc9582a6'
down_revision: Union[str, None] = '79c0f92df837'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tags', 'post_uid',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tags', 'post_uid',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###
