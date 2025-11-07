"""empty message

Revision ID: f7bf465f9c2c
Revises: 5850b285a8b5, afdb8d23866d
Create Date: 2025-05-14 15:32:22.007023

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "f7bf465f9c2c"
down_revision: Union[str, None] = ("5850b285a8b5", "afdb8d23866d")  # type: ignore
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
