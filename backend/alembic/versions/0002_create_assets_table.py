"""create assets table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

asset_type_enum = postgresql.ENUM(
    "server", "virtual_machine", "network_device", "container", "application", name="asset_type"
)
asset_status_enum = postgresql.ENUM(
    "active", "inactive", "maintenance", "decommissioned", name="asset_status"
)


def upgrade() -> None:
    asset_type_enum.create(op.get_bind(), checkfirst=True)
    asset_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "asset_type",
            postgresql.ENUM(
                "server",
                "virtual_machine",
                "network_device",
                "container",
                "application",
                name="asset_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "inactive",
                "maintenance",
                "decommissioned",
                name="asset_status",
                create_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("environment", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("attributes", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_assets_name", "assets", ["name"])
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"])


def downgrade() -> None:
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_index("ix_assets_name", table_name="assets")
    op.drop_table("assets")
    asset_status_enum.drop(op.get_bind(), checkfirst=True)
    asset_type_enum.drop(op.get_bind(), checkfirst=True)
