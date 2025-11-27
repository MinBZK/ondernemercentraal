"""Migrate appointment

Revision ID: 9670adff1a42
Revises: a6ba1110ba5f
Create Date: 2025-06-13 16:16:52.023324

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9670adff1a42"
down_revision: Union[str, None] = "a6ba1110ba5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE appointment_type SET name = 'Checkgesprek' WHERE name = 'Initial';")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE appointment_type SET name = 'Initial' WHERE name = 'Checkgesprek';")
