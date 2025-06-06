# Enhanced Filename Exposure - Backward Compatible Implementation

This document outlines a non-breaking approach to expose original filenames in Langflow while preserving all existing functionality.

## Architecture Overview

### Design Principles
- **Zero Breaking Changes**: All existing functionality remains unchanged
- **Parallel Implementation**: New features coexist with legacy systems
- **Opt-in Migration**: Users choose when to adopt new functionality
- **Additive Database Changes**: Only add new columns/tables, never modify existing ones

---

## 1. Backend Extensions

### 1.1 New API Endpoints (Parallel to Existing)

**File:** `src/backend/base/langflow/api/v2/files.py` (NEW FILE)

```python
from fastapi import APIRouter, UploadFile, File, Depends
from langflow.api.v2.schemas import EnhancedFileResponse
from langflow.services.storage.service import StorageService

router = APIRouter(prefix="/v2/files", tags=["files-v2"])

@router.post("/upload", response_model=EnhancedFileResponse)
async def upload_file_enhanced(
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service)
) -> EnhancedFileResponse:
    """Enhanced file upload that preserves original filename."""

    # Use existing storage service (no changes to core logic)
    file_path = await storage_service.save_file(file)

    # Store enhanced metadata
    file_metadata = await storage_service.save_file_metadata(
        file_path=file_path,
        original_filename=file.filename,
        content_type=file.content_type,
        size=file.size
    )

    return EnhancedFileResponse(
        # Existing fields (backward compatibility)
        file_path=file_path,
        flow_id=flow_id,

        # New enhanced fields
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file.size,
        upload_timestamp=file_metadata.created_at,
        file_id=file_metadata.id
    )

# Keep existing v1 endpoints completely unchanged
# They continue to work exactly as before
```

### 1.2 Enhanced Pydantic Schemas (Additive)

**File:** `src/backend/base/langflow/api/v2/schemas.py` (NEW FILE)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

# New enhanced response schema
class EnhancedFileResponse(BaseModel):
    # Legacy fields (for backward compatibility)
    file_path: str
    flow_id: str

    # Enhanced fields (new functionality)
    original_filename: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    upload_timestamp: datetime
    file_id: UUID

# Enhanced file metadata for components
class FileMetadata(BaseModel):
    path: str
    original_filename: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    upload_timestamp: Optional[datetime] = None

    # Backward compatibility method
    def __str__(self) -> str:
        """Allow FileMetadata to be used as string (backward compatibility)."""
        return self.path

    def __fspath__(self) -> str:
        """Support os.path operations."""
        return self.path

# Keep all existing schemas unchanged
```

### 1.3 Database Extensions (Additive Only)

**File:** `src/backend/base/langflow/services/database/models/file_metadata.py` (NEW FILE)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

# New table for enhanced file metadata
class FileMetadata(SQLModel, table=True):
    __tablename__ = "file_metadata_enhanced"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    file_path: str = Field(index=True)  # Links to existing file storage
    original_filename: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional: Link to existing user/flow tables if needed
    user_id: Optional[UUID] = Field(foreign_key="user.id", default=None)
    flow_id: Optional[str] = Field(default=None)

# Migration script (additive only)
class AddFileMetadataTable:
    """Database migration to add enhanced file metadata support."""

    def upgrade(self):
        # Add new table
        FileMetadata.__table__.create(engine, checkfirst=True)

        # Add optional column to existing file table (if desired)
        # This is optional and non-breaking
        with engine.connect() as conn:
            try:
                conn.execute(text(
                    "ALTER TABLE file ADD COLUMN original_filename_v2 TEXT DEFAULT NULL"
                ))
            except Exception:
                # Column already exists or not supported - ignore
                pass

    def downgrade(self):
        # Drop new table only (never touch existing data)
        FileMetadata.__table__.drop(engine, checkfirst=True)
```

---

## 2. Frontend Extensions

### 2.1 Enhanced FileInput Component (Parallel Implementation)

**File:** `src/frontend/src/components/core/parameterRenderComponent/components/enhancedFileInputComponent/index.tsx` (NEW FILE)

```typescript
import { FileComponentType } from "@/types/components";
import { InputProps } from "@/types/components";
import { EnhancedFileMetadata } from "@/types/files";

// New enhanced file input component
export default function EnhancedFileInputComponent({
  value,
  handleOnNewValue,
  disabled,
  fileTypes,
  ...props
}: InputProps<EnhancedFileMetadata | string, FileComponentType>): JSX.Element {

  // Handle both legacy string values and new enhanced metadata
  const isEnhancedValue = (val: any): val is EnhancedFileMetadata => {
    return val && typeof val === 'object' && 'original_filename' in val;
  };

  const displayName = isEnhancedValue(value)
    ? value.original_filename
    : (typeof value === 'string' ? basename(value) : "Upload a file...");

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return;

    const file = files[0];

    try {
      // Use new v2 API endpoint
      const response = await api.post<EnhancedFileResponse>(
        '/api/v2/files/upload',
        formData
      );

      // Return enhanced metadata object
      const enhancedMetadata: EnhancedFileMetadata = {
        path: response.data.file_path,
        original_filename: response.data.original_filename,
        content_type: response.data.content_type,
        file_size: response.data.file_size,
        upload_timestamp: response.data.upload_timestamp,
      };

      handleOnNewValue(enhancedMetadata);

    } catch (error) {
      // Fallback to legacy API if v2 not available
      const legacyResponse = await api.post<LegacyFileResponse>(
        '/api/v1/files/upload',
        formData
      );

      // Return legacy string format for backward compatibility
      handleOnNewValue(legacyResponse.data.file_path);
    }
  };

  return (
    <div className="enhanced-file-input">
      <input
        type="text"
        value={displayName}
        readOnly
        onClick={handleButtonClick}
        className="file-input-display"
      />
      <Button onClick={handleButtonClick}>
        {isEnhancedValue(value) ? "✨ Enhanced Upload" : "📁 Upload"}
      </Button>
    </div>
  );
}

// Keep existing FileInputComponent completely unchanged
```

### 2.2 Enhanced Type Definitions

**File:** `src/frontend/src/types/files.ts` (EXTEND EXISTING)

```typescript
// Add new types without modifying existing ones
export interface EnhancedFileMetadata {
  path: string;
  original_filename: string;
  content_type?: string;
} 