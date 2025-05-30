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
  file_size?: number;
  upload_timestamp?: string;
}

// Union type for backward compatibility
export type FileInputValue = string | EnhancedFileMetadata;

// Utility functions for type checking
export const isEnhancedFileMetadata = (value: any): value is EnhancedFileMetadata => {
  return value && typeof value === 'object' && 'original_filename' in value;
};

export const getFilePath = (value: FileInputValue): string => {
  return isEnhancedFileMetadata(value) ? value.path : value;
};

export const getOriginalFilename = (value: FileInputValue): string => {
  return isEnhancedFileMetadata(value)
    ? value.original_filename
    : basename(value);
};

// Keep all existing types unchanged
```

---

## 3. Component Framework Extensions

### 3.1 Enhanced FileInput Class (Parallel Implementation)

**File:** `src/backend/base/langflow/inputs/enhanced_inputs.py` (NEW FILE)

```python
from langflow.inputs.inputs import FileInput
from langflow.api.v2.schemas import FileMetadata
from typing import Union, Optional
import os

class EnhancedFileInput(FileInput):
    """Enhanced FileInput that preserves original filename information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._enhanced_metadata: Optional[FileMetadata] = None

    @property
    def enhanced_value(self) -> Optional[FileMetadata]:
        """Get enhanced file metadata if available."""
        return self._enhanced_metadata

    @property
    def original_filename(self) -> str:
        """Get original filename, with fallback to basename."""
        if self._enhanced_metadata:
            return self._enhanced_metadata.original_filename

        # Fallback to existing database lookup for legacy files
        return self._get_original_filename_fallback()

    def set_enhanced_value(self, metadata: Union[str, dict, FileMetadata]):
        """Set value with enhanced metadata support."""
        if isinstance(metadata, str):
            # Legacy string path - maintain backward compatibility
            self.value = metadata
            self._enhanced_metadata = None
        elif isinstance(metadata, dict):
            # Convert dict to FileMetadata
            self.value = metadata.get('path', '')
            self._enhanced_metadata = FileMetadata(**metadata)
        elif isinstance(metadata, FileMetadata):
            # Direct FileMetadata object
            self.value = metadata.path
            self._enhanced_metadata = metadata

    def _get_original_filename_fallback(self) -> str:
        """Fallback method using database lookup for legacy files."""
        # Use our existing database lookup implementation
        # This ensures backward compatibility
        try:
            return self._database_lookup_original_filename(self.value)
        except Exception:
            return os.path.basename(self.value)

# Keep existing FileInput class completely unchanged

### 3.2 Enhanced Component Base Classes

**File:** `src/backend/base/langflow/custom/enhanced_component.py` (NEW FILE)

```python
from langflow.custom import Component
from langflow.inputs.enhanced_inputs import EnhancedFileInput
from langflow.api.v2.schemas import FileMetadata
from typing import Union, Optional

class EnhancedComponent(Component):
    """Enhanced component base class with original filename support."""

    def get_file_metadata(self, input_name: str) -> Optional[FileMetadata]:
        """Get enhanced file metadata for a file input."""
        if hasattr(self, '_inputs') and input_name in self._inputs:
            file_input = self._inputs[input_name]
            if isinstance(file_input, EnhancedFileInput):
                return file_input.enhanced_value
        return None

    def get_original_filename(self, input_name: str) -> str:
        """Get original filename with automatic fallback."""
        metadata = self.get_file_metadata(input_name)
        if metadata:
            return metadata.original_filename

        # Fallback to legacy method
        file_path = getattr(self, input_name, '')
        return self._legacy_filename_lookup(file_path)

    def _legacy_filename_lookup(self, file_path: str) -> str:
        """Legacy filename lookup for backward compatibility."""
        # Use existing database lookup implementation
        # This ensures all existing components continue to work
        try:
            return self._database_lookup_original_filename(file_path)
        except Exception:
            return os.path.basename(file_path)

# Utility functions for any component to use
def get_enhanced_file_info(component: Component, input_name: str) -> dict:
    """Utility function to get file info from any component."""
    file_value = getattr(component, input_name, None)

    if isinstance(file_value, FileMetadata):
        return {
            'path': file_value.path,
            'original_filename': file_value.original_filename,
            'content_type': file_value.content_type,
            'file_size': file_value.file_size,
            'is_enhanced': True
        }
    elif isinstance(file_value, str):
        return {
            'path': file_value,
            'original_filename': os.path.basename(file_value),
            'content_type': None,
            'file_size': None,
            'is_enhanced': False
        }
    else:
        return {
            'path': '',
            'original_filename': 'Unknown',
            'content_type': None,
            'file_size': None,
            'is_enhanced': False
        }
```

---

## 4. Migration Strategy & Implementation

### 4.1 Feature Flags

**File:** `src/backend/base/langflow/services/settings/service.py` (EXTEND)

```python
class Settings(BaseSettings):
    # Existing settings remain unchanged

    # New feature flags for enhanced functionality
    enable_enhanced_file_inputs: bool = Field(
        default=False,
        description="Enable enhanced file input functionality"
    )

    enhanced_file_api_version: str = Field(
        default="v1",
        description="API version for file operations (v1|v2)"
    )

    migrate_legacy_files: bool = Field(
        default=False,
        description="Automatically migrate legacy file metadata"
    )
```

### 4.2 Gradual Migration Utilities

**File:** `src/backend/base/langflow/services/migration/file_migration.py` (NEW FILE)

```python
from langflow.services.database.models.file_metadata import FileMetadata
from langflow.services.database.models.file import File as LegacyFile
from sqlmodel import Session, select

class FileMigrationService:
    """Service to migrate legacy files to enhanced metadata format."""

    def __init__(self, session: Session):
        self.session = session

    def migrate_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Migrate a single file to enhanced metadata format."""

        # Check if already migrated
        existing = self.session.exec(
            select(FileMetadata).where(FileMetadata.file_path == file_path)
        ).first()

        if existing:
            return existing

        # Look up in legacy file table
        legacy_file = self.session.exec(
            select(LegacyFile).where(LegacyFile.path.contains(os.path.basename(file_path)))
        ).first()

        if legacy_file:
            # Create enhanced metadata from legacy data
            enhanced = FileMetadata(
                file_path=file_path,
                original_filename=legacy_file.name,
                content_type=None,  # Not available in legacy
                file_size=None,     # Not available in legacy
            )

            self.session.add(enhanced)
            self.session.commit()
            return enhanced

        return None

    def bulk_migrate_files(self, batch_size: int = 100) -> int:
        """Migrate all legacy files in batches."""
        migrated_count = 0

        # Get all legacy files that haven't been migrated
        legacy_files = self.session.exec(
            select(LegacyFile).limit(batch_size)
        ).all()

        for legacy_file in legacy_files:
            try:
                self.migrate_file_metadata(legacy_file.path)
                migrated_count += 1
            except Exception as e:
                print(f"Failed to migrate {legacy_file.path}: {e}")

        return migrated_count
```

### 4.3 Backward Compatibility Layer

**File:** `src/backend/base/langflow/compatibility/file_input_adapter.py` (NEW FILE)

```python
from typing import Union, Any
from langflow.api.v2.schemas import FileMetadata

class FileInputAdapter:
    """Adapter to handle both legacy and enhanced file inputs."""

    @staticmethod
    def normalize_file_input(value: Any) -> Union[str, FileMetadata]:
        """Normalize file input to consistent format."""

        if isinstance(value, str):
            # Legacy string path
            return value
        elif isinstance(value, dict):
            # Enhanced metadata as dict
            return FileMetadata(**value)
        elif isinstance(value, FileMetadata):
            # Already enhanced metadata
            return value
        else:
            # Unknown format - return empty string for safety
            return ""

    @staticmethod
    def get_file_path(value: Any) -> str:
        """Extract file path from any file input format."""
        normalized = FileInputAdapter.normalize_file_input(value)

        if isinstance(normalized, FileMetadata):
            return normalized.path
        else:
            return str(normalized)

    @staticmethod
    def get_original_filename(value: Any) -> str:
        """Extract original filename from any file input format."""
        normalized = FileInputAdapter.normalize_file_input(value)

        if isinstance(normalized, FileMetadata):
            return normalized.original_filename
        else:
            # Fallback to basename for legacy inputs
            return os.path.basename(str(normalized))

    @staticmethod
    def is_enhanced_input(value: Any) -> bool:
        """Check if input uses enhanced metadata format."""
        return isinstance(value, (FileMetadata, dict)) and \
               (hasattr(value, 'original_filename') or 'original_filename' in value)
```

---

## 5. Updated File Metadata Extractor (Backward Compatible)

**File:** `custom_nodes/enhanced_file_metadata_extractor.py` (NEW FILE)

```python
from langflow.custom import Component
from langflow.io import FileInput, Output
from langflow.schema import Message
from langflow.compatibility.file_input_adapter import FileInputAdapter
import json

class EnhancedFileMetadataExtractor(Component):
    display_name = "Enhanced File Metadata Extractor"
    description = "Extract file metadata with automatic original filename detection"
    icon = "file-search-2"
    name = "EnhancedFileMetadataExtractor"

    inputs = [
        FileInput(
            name="input_file",
            display_name="Input File",
            info="Upload any file - automatically detects enhanced metadata",
            file_types=["pdf", "doc", "docx", "rtf", "txt", "jpg", "jpeg", "png", "gif", "bmp", "zip", "tar"],
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Metadata", name="metadata", method="extract_metadata"),
    ]

    def extract_metadata(self) -> Message:
        """Extract metadata with automatic format detection."""
        try:
            file_input = self.input_file

            # Use adapter for backward compatibility
            file_path = FileInputAdapter.get_file_path(file_input)
            original_filename = FileInputAdapter.get_original_filename(file_input)
            is_enhanced = FileInputAdapter.is_enhanced_input(file_input)

            # Extract metadata using existing logic
            metadata = self._extract_comprehensive_metadata(file_path, original_filename)

            # Add compatibility information
            metadata["compatibility_info"] = {
                "input_format": "enhanced" if is_enhanced else "legacy",
                "original_filename_source": "metadata" if is_enhanced else "fallback",
                "adapter_version": "1.0.0"
            }

            # Create summary
            summary = self._create_enhanced_summary(metadata, is_enhanced)

            return Message(
                text=f"{summary}\n\n=== DETAILED METADATA ===\n{json.dumps(metadata, indent=2)}",
                sender="Enhanced File Metadata Extractor",
                sender_name="Enhanced File Metadata Extractor"
            )

        except Exception as e:
            return Message(
                text=f"Error extracting metadata: {str(e)}",
                sender="Enhanced File Metadata Extractor",
                sender_name="Enhanced File Metadata Extractor"
            )

    def _create_enhanced_summary(self, metadata: dict, is_enhanced: bool) -> str:
        """Create summary with compatibility indicators."""
        summary_lines = ["=== ENHANCED FILE METADATA SUMMARY ==="]

        # Add compatibility indicator
        format_indicator = "✨ Enhanced Format" if is_enhanced else "🔄 Legacy Compatible"
        summary_lines.append(f"📊 Input Format: {format_indicator}")

        # Add existing summary logic
        fs = metadata.get("file_system", {})
        if fs and "original_filename" in fs:
            summary_lines.extend([
                f"📁 Original Filename: {fs['original_filename']}",
                f"📏 File Size: {fs.get('file_size_human', 'Unknown')}",
                f"🏷️ File Type: {fs.get('file_extension', 'Unknown')}",
            ])

        return "\n".join(summary_lines)

# Keep original file_metadata_extractor.py unchanged for backward compatibility
```

---

## 6. Testing & Validation Strategy

### 6.1 Compatibility Test Suite

```python
# Test both legacy and enhanced functionality
class TestBackwardCompatibility:

    def test_legacy_file_input_unchanged(self):
        """Ensure existing FileInput components work exactly as before."""
        # Test existing components with string file paths
        pass

    def test_enhanced_file_input_new_functionality(self):
        """Test new enhanced file input functionality."""
        # Test new components with FileMetadata objects
        pass

    def test_mixed_environment(self):
        """Test environment with both legacy and enhanced components."""
        # Ensure they can coexist without conflicts
        pass

    def test_database_migration_safety(self):
        """Ensure database migrations are safe and reversible."""
        # Test additive-only database changes
        pass
```

### 6.2 Deployment Checklist

- [ ] All existing API endpoints continue to work
- [ ] Legacy FileInput components function unchanged
- [ ] Database migrations are additive only
- [ ] Feature flags allow gradual rollout
- [ ] Rollback procedures are tested and documented
- [ ] Performance impact is minimal
- [ ] Documentation covers both legacy and enhanced usage

---

## 7. Success Metrics

### Immediate Success (Phase 1)
- ✅ Zero breaking changes to existing installations
- ✅ All current custom components continue to function
- ✅ New enhanced functionality is available for opt-in

### Migration Success (Phase 2-3)
- ✅ Users can gradually migrate to enhanced functionality
- ✅ Clear migration path with documentation
- ✅ Performance improvements from reduced database lookups

### Long-term Success (Phase 4+)
- ✅ Majority of users adopt enhanced functionality
- ✅ Simplified codebase with fewer workarounds
- ✅ Improved user experience with reliable original filenames

This backward-compatible approach ensures that Langflow can evolve while maintaining stability for existing users and providing a clear path forward for enhanced functionality.
```
