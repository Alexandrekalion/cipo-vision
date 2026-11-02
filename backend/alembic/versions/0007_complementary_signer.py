"""Add the single department signer for the revised approval flow."""
from alembic import op
import sqlalchemy as sa

revision = "0007_complementary_signer"
down_revision = "0006_user_profiles"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("requests", sa.Column("complementary_department", sa.String(length=80), nullable=True))
    op.add_column("requests", sa.Column("complementary_signer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))

def downgrade():
    op.drop_column("requests", "complementary_signer_id")
    op.drop_column("requests", "complementary_department")
