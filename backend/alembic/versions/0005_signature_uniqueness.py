"""Prevent duplicate signatures for the same request and purpose."""
from alembic import op

revision = "0005_signature_uniqueness"
down_revision = "0004_user_signatures"
branch_labels = None
depends_on = None

def upgrade():
    op.create_unique_constraint("uq_signatures_request_purpose", "signatures", ["request_id", "purpose"])

def downgrade():
    op.drop_constraint("uq_signatures_request_purpose", "signatures", type_="unique")
