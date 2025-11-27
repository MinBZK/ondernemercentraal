"""empty message

Revision ID: 2054237371ce
Revises: 86a7604f9edd, d1c34074ceaf
Create Date: 2025-10-09 16:17:14.610852

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "2054237371ce"
down_revision: str = "86a7604f9edd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
