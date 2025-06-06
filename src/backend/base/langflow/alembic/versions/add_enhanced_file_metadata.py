"""Add enhanced file metadata table

Revision ID: enhanced_file_metadata_001
Revises: [previous_revision]
Create Date: 2024-01-15 10:00:00.000000

This migration adds support for enhanced file metadata while maintaining
complete backward compatibility with existing file storage.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = 'enhanced_file_metadata_001'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced file metadata table and optional columns."""
    
    # Create new table for enhanced file metadata
    op.create_table(
        'file_metadata_enhanced',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('flow_id', sa.String(), nullable=True),
        sa.Column('upload_session_id', sa.String(), nullable=True),
        sa.Column('is_temporary', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_file_metadata_enhanced_file_path', 'file_path'),
        sa.Index('ix_file_metadata_enhanced_user_id', 'user_id'),
        sa.Index('ix_file_metadata_enhanced_flow_id', 'flow_id'),
    )
    
    # Add foreign key constraint to user table if it exists
    try:
        op.create_foreign_key(
            'fk_file_metadata_enhanced_user_id',
            'file_metadata_enhanced',
            'user',
            ['user_id'],
            ['id'],
            ondelete='SET NULL'
        )
    except Exception:
        # User table might not exist or have different structure
        # This is non-critical for the enhanced functionality
        pass
    
    # Optionally add a column to existing file table for backward compatibility
    # This is completely optional and non-breaking
    try:
        op.add_column('file', sa.Column('enhanced_metadata_id', sa.UUID(), nullable=True))
        op.create_index('ix_file_enhanced_metadata_id', 'file', ['enhanced_metadata_id'])
        
        # Add foreign key to enhanced metadata
        op.create_foreign_key(
            'fk_file_enhanced_metadata',
            'file',
            'file_metadata_enhanced',
            ['enhanced_metadata_id'],
            ['id'],
            ondelete='SET NULL'
        )
    except Exception:
        # File table might not exist or have different structure
        # Enhanced functionality works without this
        pass


def downgrade():
    """Remove enhanced file metadata table and related changes."""
    
    # Remove foreign key constraints first
    try:
        op.drop_constraint('fk_file_enhanced_metadata', 'file', type_='foreignkey')
        op.drop_index('ix_file_enhanced_metadata_id', 'file')
        op.drop_column('file', 'enhanced_metadata_id')
    except Exception:
        # Column/constraint might not exist
        pass
    
    try:
        op.drop_constraint('fk_file_metadata_enhanced_user_id', 'file_metadata_enhanced', type_='foreignkey')
    except Exception:
        # Constraint might not exist
        pass
    
    # Drop the enhanced metadata table
    op.drop_table('file_metadata_enhanced')


def migrate_existing_files():
    """
    Optional function to migrate existing files to enhanced metadata format.
    This can be called separately after the migration is applied.
    """
    from sqlalchemy import create_engine, text
    from langflow.services.database.models.file_metadata import FileMetadataService
    
    # This would be implemented as a separate migration script
    # to avoid making the main migration too complex
    pass


# Migration verification queries
def verify_migration():
    """Verify that the migration was applied correctly."""
    from sqlalchemy import create_engine, text
    
    queries = [
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'file_metadata_enhanced'",
        "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'file_metadata_enhanced' AND column_name = 'original_filename'",
    ]
    
    # These would be used in tests to verify migration success
    return queries
