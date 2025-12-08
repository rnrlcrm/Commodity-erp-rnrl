"""create_events_table

Revision ID: bc14937b8b59
Revises: ebf8bb791693
Create Date: 2025-11-21 07:23:53.121407

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'bc14937b8b59'
down_revision = 'ebf8bb791693'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create events table for event sourcing.
    
    This table stores ALL events from ALL modules.
    JSONB provides flexibility for different event payloads.
    """
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('aggregate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('aggregate_type', sa.String(length=50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index('ix_events_event_type', 'events', ['event_type'])
    op.create_index('ix_events_aggregate_id', 'events', ['aggregate_id'])
    op.create_index('ix_events_aggregate_type', 'events', ['aggregate_type'])
    op.create_index('ix_events_user_id', 'events', ['user_id'])
    op.create_index('ix_events_timestamp', 'events', ['timestamp'])
    
    # Composite index for common query pattern: get all events for an aggregate
    op.create_index('ix_events_aggregate_composite', 'events', ['aggregate_id', 'aggregate_type', 'timestamp'])


def downgrade() -> None:
    """Drop events table and all indexes"""
    op.execute('DROP INDEX IF EXISTS ix_events_aggregate_composite')
op.execute('DROP INDEX IF EXISTS ix_events_timestamp')
op.execute('DROP INDEX IF EXISTS ix_events_user_id')
op.execute('DROP INDEX IF EXISTS ix_events_aggregate_type')
op.execute('DROP INDEX IF EXISTS ix_events_aggregate_id')
op.execute('DROP INDEX IF EXISTS ix_events_event_type')
op.drop_table('events')
