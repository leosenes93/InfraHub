"""enable pg_trgm and add search indexes on assets

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24

"""
from collections.abc import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_assets_name_trgm ON assets USING gin (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_assets_description_trgm ON assets USING gin (description gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_assets_description_trgm")
    op.execute("DROP INDEX IF EXISTS ix_assets_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
