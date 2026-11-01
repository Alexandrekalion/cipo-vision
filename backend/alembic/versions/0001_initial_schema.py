"""Initial CIPO VISION development schema."""
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('users', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('username',sa.String(120),nullable=False), sa.Column('display_name',sa.String(160),nullable=False), sa.Column('role',sa.String(80),nullable=False), sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_index('ix_users_username','users',['username'],unique=True)
    op.create_table('requests', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('protocol',sa.String(40),nullable=False), sa.Column('requester_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False), sa.Column('manager_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False), sa.Column('status',sa.String(80),nullable=False), sa.Column('employee',sa.String(160),nullable=False), sa.Column('occurrence_type',sa.String(120),nullable=False), sa.Column('occurred_at',sa.DateTime(timezone=True),nullable=False), sa.Column('location',sa.String(200),nullable=False), sa.Column('camera_area',sa.String(200)), sa.Column('reason',sa.Text(),nullable=False), sa.Column('rh_required',sa.Boolean()), sa.Column('witness_id',sa.Integer(),sa.ForeignKey('users.id')), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_requests_protocol','requests',['protocol'],unique=True)
    op.create_table('signatures', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('request_id',sa.Integer(),sa.ForeignKey('requests.id'),nullable=False), sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False), sa.Column('kind',sa.String(80),nullable=False), sa.Column('document_version',sa.String(40),nullable=False), sa.Column('confirmed_at',sa.DateTime(timezone=True),nullable=False))
    op.create_table('audit_events', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('request_id',sa.Integer(),sa.ForeignKey('requests.id')), sa.Column('actor_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False), sa.Column('action',sa.String(120),nullable=False), sa.Column('detail',sa.Text(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))

def downgrade():
    op.drop_table('audit_events'); op.drop_table('signatures'); op.drop_index('ix_requests_protocol',table_name='requests'); op.drop_table('requests'); op.drop_index('ix_users_username',table_name='users'); op.drop_table('users')
