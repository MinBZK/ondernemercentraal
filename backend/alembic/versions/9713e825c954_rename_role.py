"""Rename role

Revision ID: 9713e825c954
Revises: a50a17e98c3c
Create Date: 2025-09-04 11:30:28.725929

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9713e825c954"
down_revision: Union[str, None] = "a50a17e98c3c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE role SET name = 'partner' WHERE name = 'trajectpartner'")
    op.execute("""UPDATE "user" SET name = 'partner' WHERE name = 'trajectpartner'""")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE role SET name = 'trajectpartner' WHERE name = 'partner'")
    op.execute("""UPDATE "user" SET name = 'trajectpartner' WHERE name = 'partner'""")
