from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID


class EnhancedFileResponse(BaseModel):
    """Enhanced file upload response with original filename and metadata."""
    
    # Legacy fields (for backward compatibility)
    file_path: str = Field(description="Server file path (UUID-based)")
    flow_id: Optional[str] = Field(default=None, description="Associated flow ID")
    
    # Enhanced fields (new functionality)
    original_filename: str = Field(description="Original filename uploaded by user")
    content_type: Optional[str] = Field(default=None, description="MIME type of the file")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    upload_timestamp: datetime = Field(description="When the file was uploaded")
    file_id: UUID = Field(description="Unique identifier for the file metadata")
    
    # Additional metadata
    upload_session_id: Optional[str] = Field(default=None, description="Upload session identifier")
    is_temporary: bool = Field(default=False, description="Whether this is a temporary file")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileMetadata(BaseModel):
    """Enhanced file metadata for components."""
    
    path: str = Field(description="Server file path")
    original_filename: str = Field(description="Original filename")
    content_type: Optional[str] = Field(default=None, description="MIME type")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    upload_timestamp: Optional[datetime] = Field(default=None, description="Upload time")
    file_id: Optional[UUID] = Field(default=None, description="File metadata ID")
    
    # Backward compatibility methods
    def __str__(self) -> str:
        """Allow FileMetadata to be used as string (backward compatibility)."""
        return self.path
    
    def __fspath__(self) -> str:
        """Support os.path operations."""
        return self.path
    
    def __eq__(self, other) -> bool:
        """Support comparison with strings."""
        if isinstance(other, str):
            return self.path == other
        elif isinstance(other, FileMetadata):
            return self.path == other.path
        return False
    
    def __hash__(self) -> int:
        """Support use in sets and as dict keys."""
        return hash(self.path)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FileUploadRequest(BaseModel):
    """Request model for file uploads."""
    
    flow_id: Optional[str] = Field(default=None, description="Associated flow ID")
    is_temporary: bool = Field(default=False, description="Whether this is a temporary file")
    upload_session_id: Optional[str] = Field(default=None, description="Upload session identifier")


class FileMetadataUpdate(BaseModel):
    """Model for updating file metadata."""
    
    original_filename: Optional[str] = Field(default=None)
    content_type: Optional[str] = Field(default=None)
    file_size: Optional[int] = Field(default=None)
    is_temporary: Optional[bool] = Field(default=None)


class FileListResponse(BaseModel):
    """Response model for listing files."""
    
    files: list[FileMetadata] = Field(description="List of file metadata")
    total_count: int = Field(description="Total number of files")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=50, description="Number of files per page")


class FileDeleteResponse(BaseModel):
    """Response model for file deletion."""
    
    success: bool = Field(description="Whether the deletion was successful")
    message: str = Field(description="Status message")
    deleted_file_path: Optional[str] = Field(default=None, description="Path of deleted file")


# Union type for backward compatibility
FileInputValue = Union[str, FileMetadata, dict]


class LegacyFileResponse(BaseModel):
    """Legacy file response format for backward compatibility."""
    
    file_path: str = Field(description="Server file path")
    flow_id: Optional[str] = Field(default=None, description="Associated flow ID")
    
    # Optional enhanced fields that may be present
    original_filename: Optional[str] = Field(default=None)
    content_type: Optional[str] = Field(default=None)
    file_size: Optional[int] = Field(default=None)


# Utility functions for type checking and conversion
def is_enhanced_file_metadata(value: Any) -> bool:
    """Check if a value is enhanced file metadata."""
    if isinstance(value, FileMetadata):
        return True
    elif isinstance(value, dict):
        return 'original_filename' in value and 'path' in value
    return False


def normalize_file_input(value: FileInputValue) -> FileMetadata:
    """Normalize any file input to FileMetadata format."""
    if isinstance(value, FileMetadata):
        return value
    elif isinstance(value, dict):
        return FileMetadata(**value)
    elif isinstance(value, str):
        # Legacy string path - create minimal FileMetadata
        import os
        return FileMetadata(
            path=value,
            original_filename=os.path.basename(value)
        )
    else:
        raise ValueError(f"Cannot normalize file input of type {type(value)}")


def get_file_path(value: FileInputValue) -> str:
    """Extract file path from any file input format."""
    if isinstance(value, FileMetadata):
        return value.path
    elif isinstance(value, dict):
        return value.get('path', '')
    elif isinstance(value, str):
        return value
    else:
        return str(value)


def get_original_filename(value: FileInputValue) -> str:
    """Extract original filename from any file input format."""
    if isinstance(value, FileMetadata):
        return value.original_filename
    elif isinstance(value, dict):
        return value.get('original_filename', os.path.basename(value.get('path', '')))
    elif isinstance(value, str):
        import os
        return os.path.basename(value)
    else:
        return 'unknown_file'
