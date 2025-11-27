"""empty message

Revision ID: 017ec9ea2098
Revises: 24250a7036a5, d52ca113c0cd
Create Date: 2025-05-15 15:51:45.566389

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "017ec9ea2098"
down_revision: Union[str, None] = ("24250a7036a5", "d52ca113c0cd")  # type: ignore
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
