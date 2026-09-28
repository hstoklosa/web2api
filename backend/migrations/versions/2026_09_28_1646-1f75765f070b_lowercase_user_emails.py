"""lowercase user emails

Revision ID: 1f75765f070b
Revises: d97f0042f12a
Create Date: 2026-09-28 16:46:30.038375+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f75765f070b"
down_revision: str | Sequence[str] | None = "d97f0042f12a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Accounts whose emails differ only in case cannot be merged automatically,
    # so refuse to migrate until someone decides which of them to keep.
    duplicates = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT lower(email) FROM users GROUP BY lower(email) HAVING count(*) > 1"
            )
        )
        .scalars()
        .all()
    )
    if duplicates:
        raise RuntimeError(
            "Users with emails that differ only in case must be merged or deleted"
            f" before this migration: {', '.join(duplicates)}"
        )

    op.execute("UPDATE users SET email = lower(email) WHERE email <> lower(email)")
    op.create_check_constraint(
        op.f("ck_users_email_lowercase"), "users", "email = lower(email)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("ck_users_email_lowercase"), "users", type_="check")
