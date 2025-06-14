from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional, List
from uuid import UUID
import os
from pathlib import Path

from langflow.api.v2.schemas import (
    EnhancedFileResponse,
    FileMetadata,
    FileUploadRequest,
    FileMetadataUpdate,
    FileListResponse,
    FileDeleteResponse
)
from langflow.services.database.models.file_metadata import FileMetadataService, FileMetadataEnhanced
from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.deps import get_storage_service, get_settings_service
from langflow.services.storage.service import StorageService
from langflow.services.settings.service import SettingsService

router = APIRouter(prefix="/enhanced", tags=["enhanced-files"])


@router.post("/upload", response_model=EnhancedFileResponse)
async def upload_file_enhanced(
    file: UploadFile = File(...),
    flow_id: Optional[str] = Query(default=None),
    is_temporary: bool = Query(default=False),
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends(),
    storage_service: StorageService = Depends(get_storage_service),
    settings_service: SettingsService = Depends(get_settings_service)
) -> EnhancedFileResponse:
    """Enhanced file upload that preserves original filename and metadata."""
    
    try:
        # Validate file size
        max_file_size = settings_service.settings.max_file_size_upload * 1024 * 1024
        if file.size and file.size > max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file.size} exceeds maximum allowed size {max_file_size}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Generate unique filename
        import uuid
        file_id = uuid.uuid4()
        file_extension = Path(file.filename or "").suffix
        anonymized_file_name = f"{file_id}{file_extension}"
        
        # Use user ID as folder
        folder = str(current_user.id)
        
        # Save file using existing storage service
        await storage_service.save_file(
            flow_id=folder,
            file_name=anonymized_file_name,
            data=file_content
        )
        
        # Construct file path
        file_path = f"{folder}/{anonymized_file_name}"
        
        # Create enhanced metadata
        metadata_service = FileMetadataService(session)
        file_metadata = await metadata_service.create_file_metadata(
            file_path=file_path,
            original_filename=file.filename or "unknown",
            content_type=file.content_type,
            file_size=file.size,
            user_id=current_user.id,
            flow_id=flow_id
        )
        
        return EnhancedFileResponse(
            # Legacy fields for backward compatibility
            file_path=file_path,
            flow_id=flow_id,
            
            # Enhanced fields
            original_filename=file_metadata.original_filename,
            content_type=file_metadata.content_type,
            file_size=file_metadata.file_size,
            upload_timestamp=file_metadata.created_at,
            file_id=file_metadata.id,
            is_temporary=file_metadata.is_temporary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/metadata/{file_path:path}", response_model=FileMetadata)
async def get_file_metadata(
    file_path: str,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends()
) -> FileMetadata:
    """Get enhanced metadata for a specific file."""
    
    metadata_service = FileMetadataService(session)
    file_metadata = await metadata_service.get_file_metadata(file_path)
    
    if not file_metadata:
        # Try to create metadata from legacy file if it exists
        if os.path.exists(file_path):
            original_filename = os.path.basename(file_path)
            file_metadata = await metadata_service.create_file_metadata(
                file_path=file_path,
                original_filename=original_filename,
                user_id=current_user.id
            )
        else:
            raise HTTPException(status_code=404, detail="File metadata not found")
    
    return FileMetadata(
        path=file_metadata.file_path,
        original_filename=file_metadata.original_filename,
        content_type=file_metadata.content_type,
        file_size=file_metadata.file_size,
        upload_timestamp=file_metadata.created_at,
        file_id=file_metadata.id
    )


@router.get("/original-filename/{file_path:path}")
async def get_original_filename(
    file_path: str,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends()
) -> dict:
    """Get just the original filename for a file path (lightweight endpoint)."""
    
    metadata_service = FileMetadataService(session)
    original_filename = await metadata_service.get_original_filename(file_path)
    
    if not original_filename:
        # Fallback to basename
        original_filename = os.path.basename(file_path)
    
    return {
        "file_path": file_path,
        "original_filename": original_filename,
        "source": "enhanced_metadata" if original_filename != os.path.basename(file_path) else "fallback"
    }


@router.put("/metadata/{file_path:path}", response_model=FileMetadata)
async def update_file_metadata(
    file_path: str,
    updates: FileMetadataUpdate,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends()
) -> FileMetadata:
    """Update metadata for a specific file."""
    
    metadata_service = FileMetadataService(session)
    
    # Convert Pydantic model to dict, excluding None values
    update_data = updates.dict(exclude_none=True)
    
    file_metadata = await metadata_service.update_file_metadata(file_path, **update_data)
    
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File metadata not found")
    
    return FileMetadata(
        path=file_metadata.file_path,
        original_filename=file_metadata.original_filename,
        content_type=file_metadata.content_type,
        file_size=file_metadata.file_size,
        upload_timestamp=file_metadata.created_at,
        file_id=file_metadata.id
    )


@router.get("/list", response_model=FileListResponse)
async def list_enhanced_files(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    flow_id: Optional[str] = Query(default=None),
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends()
) -> FileListResponse:
    """List files with enhanced metadata."""
    
    from sqlmodel import select, func
    
    # Build query
    query = select(FileMetadataEnhanced).where(FileMetadataEnhanced.user_id == current_user.id)
    
    if flow_id:
        query = query.where(FileMetadataEnhanced.flow_id == flow_id)
    
    # Get total count
    count_query = select(func.count(FileMetadataEnhanced.id)).where(FileMetadataEnhanced.user_id == current_user.id)
    if flow_id:
        count_query = count_query.where(FileMetadataEnhanced.flow_id == flow_id)
    
    total_count = await session.exec(count_query).first()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    results = await session.exec(query).all()
    
    # Convert to FileMetadata objects
    files = [
        FileMetadata(
            path=result.file_path,
            original_filename=result.original_filename,
            content_type=result.content_type,
            file_size=result.file_size,
            upload_timestamp=result.created_at,
            file_id=result.id
        )
        for result in results
    ]
    
    return FileListResponse(
        files=files,
        total_count=total_count or 0,
        page=page,
        page_size=page_size
    )


@router.delete("/{file_path:path}", response_model=FileDeleteResponse)
async def delete_enhanced_file(
    file_path: str,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends(),
    storage_service: StorageService = Depends(get_storage_service)
) -> FileDeleteResponse:
    """Delete a file and its enhanced metadata."""
    
    try:
        metadata_service = FileMetadataService(session)
        
        # Delete metadata first
        metadata_deleted = await metadata_service.delete_file_metadata(file_path)
        
        # Delete physical file
        file_deleted = False
        if os.path.exists(file_path):
            try:
                # Extract folder and filename from path
                path_parts = file_path.split('/')
                if len(path_parts) >= 2:
                    folder = path_parts[-2]
                    filename = path_parts[-1]
                    await storage_service.delete_file(flow_id=folder, file_name=filename)
                    file_deleted = True
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to delete physical file {file_path}: {e}")
        
        success = metadata_deleted or file_deleted
        message = "File and metadata deleted successfully" if success else "File not found"
        
        return FileDeleteResponse(
            success=success,
            message=message,
            deleted_file_path=file_path if success else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")


@router.get("/download/{file_path:path}")
async def download_enhanced_file(
    file_path: str,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends(),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Download a file with its original filename."""
    
    # Get original filename from metadata
    metadata_service = FileMetadataService(session)
    file_metadata = await metadata_service.get_file_metadata(file_path)
    
    filename = file_metadata.original_filename if file_metadata else os.path.basename(file_path)
    
    # Extract folder and filename from path for storage service
    path_parts = file_path.split('/')
    if len(path_parts) >= 2:
        folder = path_parts[-2]
        storage_filename = path_parts[-1]
        
        try:
            # Get file content from storage
            file_content = await storage_service.get_file(flow_id=folder, file_name=storage_filename)
            
            # Create temporary file for download
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            return FileResponse(
                path=temp_file_path,
                filename=filename,
                media_type=file_metadata.content_type if file_metadata else 'application/octet-stream'
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Invalid file path format")


@router.post("/migrate-legacy")
async def migrate_legacy_file(
    file_path: str,
    original_filename: str,
    session: DbSession = Depends(),
    current_user: CurrentActiveUser = Depends()
) -> FileMetadata:
    """Migrate a legacy file to enhanced metadata format."""
    
    metadata_service = FileMetadataService(session)
    file_metadata = await metadata_service.migrate_legacy_file(file_path, original_filename)
    
    return FileMetadata(
        path=file_metadata.file_path,
        original_filename=file_metadata.original_filename,
        content_type=file_metadata.content_type,
        file_size=file_metadata.file_size,
        upload_timestamp=file_metadata.created_at,
        file_id=file_metadata.id
    )
