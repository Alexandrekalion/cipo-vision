"""Add workflow, signature evidence and extraction records."""
from alembic import op
import sqlalchemy as sa

revision = "0003_workflow_signatures"
down_revision = "0002_auth_sessions"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("requests", sa.Column("safety_required", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("signatures", sa.Column("purpose", sa.String(length=120), nullable=False, server_default="solicitacao"))
    op.add_column("signatures", sa.Column("document_hash", sa.String(length=128), nullable=False, server_default=""))
    op.add_column("signatures", sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("workflow_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_status", sa.String(length=80)),
        sa.Column("to_status", sa.String(length=80), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workflow_events_request_id", "workflow_events", ["request_id"])
    op.create_table("extractions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False, unique=True),
        sa.Column("operator_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("storage_reference", sa.String(length=255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )

def downgrade():
    op.drop_table("extractions")
    op.drop_index("ix_workflow_events_request_id", table_name="workflow_events")
    op.drop_table("workflow_events")
    op.drop_column("signatures", "confirmed")
    op.drop_column("signatures", "document_hash")
    op.drop_column("signatures", "purpose")
    op.drop_column("requests", "safety_required")
