"""add documentation to assets and create asset_attachments table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-24

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("documentation", sa.Text(), nullable=True))

    op.create_table(
        "asset_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_asset_attachments_asset_id", "asset_attachments", ["asset_id"])


def downgrade() -> None:
    op.drop_index("ix_asset_attachments_asset_id", table_name="asset_attachments")
    op.drop_table("asset_attachments")
    op.drop_column("assets", "documentation")
