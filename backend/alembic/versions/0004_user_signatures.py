"""Store individual signature profiles for explicit document confirmation."""
from alembic import op
import sqlalchemy as sa

revision = "0004_user_signatures"
down_revision = "0003_workflow_signatures"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("user_signatures",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("signature_data", sa.Text(), nullable=False),
        sa.Column("signature_digest", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("user_signatures")
