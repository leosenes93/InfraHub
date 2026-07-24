"""add zabbix_host_id to assets

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-24

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("zabbix_host_id", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("assets", "zabbix_host_id")
