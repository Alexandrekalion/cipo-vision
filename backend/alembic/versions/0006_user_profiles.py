"""Add first-access corporate profile fields without changing existing accounts."""
from alembic import op
import sqlalchemy as sa

revision = "0006_user_profiles"
down_revision = "0005_signature_uniqueness"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("full_name", sa.String(length=200), nullable=True))
    op.add_column("users", sa.Column("employee_number", sa.String(length=80), nullable=True))
    op.add_column("users", sa.Column("department", sa.String(length=160), nullable=True))
    op.add_column("users", sa.Column("ad_subject_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("ad_groups", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("authorized_profiles", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("profile_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_users_ad_subject_id", "users", ["ad_subject_id"])

def downgrade():
    op.drop_constraint("uq_users_ad_subject_id", "users", type_="unique")
    for name in ("profile_completed_at", "authorized_profiles", "ad_groups", "ad_subject_id", "department", "employee_number", "full_name"):
        op.drop_column("users", name)
