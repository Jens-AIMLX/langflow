from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional


class FileMetadataEnhanced(SQLModel, table=True):
    """Enhanced file metadata table for storing original filenames and additional metadata."""
    
    __tablename__ = "file_metadata_enhanced"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    file_path: str = Field(index=True, description="Server file path (UUID-based)")
    original_filename: str = Field(description="Original filename uploaded by user")
    content_type: Optional[str] = Field(default=None, description="MIME type of the file")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional relationships to existing tables
    user_id: Optional[UUID] = Field(foreign_key="user.id", default=None)
    flow_id: Optional[str] = Field(default=None, description="Associated flow ID")
    
    # Additional metadata fields
    upload_session_id: Optional[str] = Field(default=None, description="Upload session identifier")
    is_temporary: bool = Field(default=False, description="Whether this is a temporary file")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileMetadataService:
    """Service for managing enhanced file metadata."""
    
    def __init__(self, session):
        self.session = session
    
    async def create_file_metadata(
        self,
        file_path: str,
        original_filename: str,
        content_type: Optional[str] = None,
        file_size: Optional[int] = None,
        user_id: Optional[UUID] = None,
        flow_id: Optional[str] = None
    ) -> FileMetadataEnhanced:
        """Create new enhanced file metadata record."""
        
        metadata = FileMetadataEnhanced(
            file_path=file_path,
            original_filename=original_filename,
            content_type=content_type,
            file_size=file_size,
            user_id=user_id,
            flow_id=flow_id
        )
        
        self.session.add(metadata)
        await self.session.commit()
        await self.session.refresh(metadata)
        
        return metadata
    
    async def get_file_metadata(self, file_path: str) -> Optional[FileMetadataEnhanced]:
        """Get enhanced file metadata by file path."""
        from sqlmodel import select
        
        statement = select(FileMetadataEnhanced).where(
            FileMetadataEnhanced.file_path == file_path
        )
        result = await self.session.exec(statement)
        return result.first()
    
    async def get_original_filename(self, file_path: str) -> Optional[str]:
        """Get original filename for a given file path."""
        metadata = await self.get_file_metadata(file_path)
        return metadata.original_filename if metadata else None
    
    async def update_file_metadata(
        self,
        file_path: str,
        **updates
    ) -> Optional[FileMetadataEnhanced]:
        """Update existing file metadata."""
        metadata = await self.get_file_metadata(file_path)
        
        if metadata:
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            metadata.updated_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(metadata)
        
        return metadata
    
    async def delete_file_metadata(self, file_path: str) -> bool:
        """Delete file metadata record."""
        metadata = await self.get_file_metadata(file_path)
        
        if metadata:
            await self.session.delete(metadata)
            await self.session.commit()
            return True
        
        return False
    
    async def migrate_legacy_file(self, file_path: str, original_filename: str) -> FileMetadataEnhanced:
        """Migrate a legacy file to enhanced metadata format."""
        
        # Check if already migrated
        existing = await self.get_file_metadata(file_path)
        if existing:
            return existing
        
        # Create new metadata record
        return await self.create_file_metadata(
            file_path=file_path,
            original_filename=original_filename,
            content_type=None,  # Not available for legacy files
            file_size=None      # Not available for legacy files
        )
