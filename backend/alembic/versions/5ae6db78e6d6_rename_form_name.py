"""Rename form name

Revision ID: 5ae6db78e6d6
Revises: 9713e825c954
Create Date: 2025-09-09 11:16:27.528291

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5ae6db78e6d6"
down_revision: Union[str, None] = "9713e825c954"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        UPDATE form_template
        SET name = 'Eindevaluatie door partner'
        WHERE name = 'Eindevaluatie door trajectpartner'
          AND NOT EXISTS (
              SELECT 1 FROM form_template WHERE name = 'Eindevaluatie door partner'
          )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "UPDATE form_template SET name = 'Eindevaluatie door trajectpartner' where name ='Eindevaluatie door partner'"
    )
