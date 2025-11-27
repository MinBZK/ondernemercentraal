"""empty message

Revision ID: f6b37ab4421e
Revises: 18fe960cf1ab, f59649f21bd1
Create Date: 2025-05-01 09:28:04.654652

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "f6b37ab4421e"
down_revision: Union[str, None] = ("18fe960cf1ab", "f59649f21bd1")  # type: ignore
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
