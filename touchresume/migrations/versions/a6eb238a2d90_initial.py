"""
initial

Revision ID: a6eb238a2d90
Revises:
Create Date: 2019-08-21 17:18:19.359961

"""
from alembic import op
import sqlalchemy as sa


revision = 'a6eb238a2d90'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users',
        sa.Column('identity', sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint('identity'))
    op.create_index(
        op.f('ix_users_identity'), 'users', ['identity'], unique=True)

    op.create_table(
        'accounts',
        sa.Column('identity', sa.String(length=120), nullable=False),
        sa.Column('access', sa.String(length=200), nullable=False),
        sa.Column('refresh', sa.String(length=200), nullable=False),
        sa.Column('expires', sa.DateTime(), nullable=False),
        sa.Column('provider', sa.String(length=120), nullable=False),
        sa.Column('user_id', sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.identity'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('identity'))
    op.create_index(
        op.f('ix_accounts_identity'), 'accounts', ['identity'], unique=True)

    op.create_table(
        'resume',
        sa.Column('identity', sa.String(length=120), nullable=False),
        sa.Column('published', sa.DateTime(), nullable=False),
        sa.Column('autoupdate', sa.Boolean(), nullable=False),
        sa.Column('account_id', sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ['account_id'], ['accounts.identity'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('identity'))
    op.create_index(
        op.f('ix_resume_identity'), 'resume', ['identity'], unique=True)

    op.create_table(
        'tasks',
        sa.Column('identity', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=False),
        sa.Column('success', sa.Integer(), nullable=False),
        sa.Column('skipped', sa.Integer(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('identity'))
    op.create_index(
        op.f('ix_tasks_identity'), 'tasks', ['identity'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tasks_identity'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_resume_identity'), table_name='resume')
    op.drop_table('resume')
    op.drop_index(op.f('ix_accounts_identity'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_users_identity'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###