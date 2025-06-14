from langflow.inputs.inputs import FileInput
from langflow.api.v2.schemas import FileMetadata, normalize_file_input, get_file_path, get_original_filename
from typing import Union, Optional, Any
import os


class EnhancedFileInput(FileInput):
    """Enhanced FileInput that preserves original filename information."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._enhanced_metadata: Optional[FileMetadata] = None
        self._is_enhanced = False
    
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
    
    @property
    def is_enhanced(self) -> bool:
        """Check if this input contains enhanced metadata."""
        return self._is_enhanced
    
    def set_enhanced_value(self, metadata: Union[str, dict, FileMetadata]):
        """Set value with enhanced metadata support."""
        if isinstance(metadata, str):
            # Legacy string path - maintain backward compatibility
            self.value = metadata
            self._enhanced_metadata = None
            self._is_enhanced = False
        elif isinstance(metadata, dict):
            # Convert dict to FileMetadata
            self.value = metadata.get('path', '')
            try:
                self._enhanced_metadata = FileMetadata(**metadata)
                self._is_enhanced = True
            except Exception:
                # Invalid metadata format - fall back to legacy
                self._enhanced_metadata = None
                self._is_enhanced = False
        elif isinstance(metadata, FileMetadata):
            # Direct FileMetadata object
            self.value = metadata.path
            self._enhanced_metadata = metadata
            self._is_enhanced = True
        else:
            # Unknown format - convert to string
            self.value = str(metadata)
            self._enhanced_metadata = None
            self._is_enhanced = False
    
    def get_file_path(self) -> str:
        """Get the file path (server path)."""
        if self._enhanced_metadata:
            return self._enhanced_metadata.path
        return str(self.value) if self.value else ""
    
    def get_original_filename(self) -> str:
        """Get the original filename with fallback."""
        if self._enhanced_metadata:
            return self._enhanced_metadata.original_filename
        return self._get_original_filename_fallback()
    
    def get_content_type(self) -> Optional[str]:
        """Get the content type if available."""
        if self._enhanced_metadata:
            return self._enhanced_metadata.content_type
        return None
    
    def get_file_size(self) -> Optional[int]:
        """Get the file size if available."""
        if self._enhanced_metadata:
            return self._enhanced_metadata.file_size
        return None
    
    def _get_original_filename_fallback(self) -> str:
        """Fallback method using database lookup for legacy files."""
        file_path = str(self.value) if self.value else ""
        
        # Try database lookup (existing implementation)
        try:
            return self._database_lookup_original_filename(file_path)
        except Exception:
            return os.path.basename(file_path)
    
    def _database_lookup_original_filename(self, file_path: str) -> str:
        """Database lookup for original filename (legacy support)."""
        try:
            import sqlite3
            from pathlib import Path
            
            path_obj = Path(file_path)
            if len(path_obj.parts) >= 2:
                relative_path = f"{path_obj.parts[-2]}/{path_obj.parts[-1]}"
                
                db_paths = [
                    "langflow.db",
                    os.path.expanduser("~/.langflow/langflow.db"),
                    os.path.join(os.getcwd(), "langflow.db")
                ]
                
                for db_path in db_paths:
                    if os.path.exists(db_path):
                        try:
                            conn = sqlite3.connect(db_path)
                            cursor = conn.cursor()
                            cursor.execute("SELECT name FROM file WHERE path = ?", (relative_path,))
                            result = cursor.fetchone()
                            conn.close()
                            
                            if result:
                                return result[0]
                        except Exception:
                            continue
                            
        except Exception:
            pass
        
        return os.path.basename(file_path)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        if self._enhanced_metadata:
            return {
                "path": self._enhanced_metadata.path,
                "original_filename": self._enhanced_metadata.original_filename,
                "content_type": self._enhanced_metadata.content_type,
                "file_size": self._enhanced_metadata.file_size,
                "upload_timestamp": self._enhanced_metadata.upload_timestamp.isoformat() if self._enhanced_metadata.upload_timestamp else None,
                "file_id": str(self._enhanced_metadata.file_id) if self._enhanced_metadata.file_id else None,
                "is_enhanced": True
            }
        else:
            return {
                "path": str(self.value) if self.value else "",
                "original_filename": self.get_original_filename(),
                "content_type": None,
                "file_size": None,
                "upload_timestamp": None,
                "file_id": None,
                "is_enhanced": False
            }
    
    def __str__(self) -> str:
        """String representation returns file path for backward compatibility."""
        return self.get_file_path()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        if self._enhanced_metadata:
            return f"EnhancedFileInput(path='{self._enhanced_metadata.path}', original_filename='{self._enhanced_metadata.original_filename}', enhanced=True)"
        else:
            return f"EnhancedFileInput(path='{self.value}', enhanced=False)"


class FileInputAdapter:
    """Adapter to handle both legacy and enhanced file inputs."""
    
    @staticmethod
    def normalize_file_input(value: Any) -> Union[str, FileMetadata]:
        """Normalize file input to consistent format."""
        return normalize_file_input(value)
    
    @staticmethod
    def get_file_path(value: Any) -> str:
        """Extract file path from any file input format."""
        return get_file_path(value)
    
    @staticmethod
    def get_original_filename(value: Any) -> str:
        """Extract original filename from any file input format."""
        return get_original_filename(value)
    
    @staticmethod
    def is_enhanced_input(value: Any) -> bool:
        """Check if input uses enhanced metadata format."""
        if isinstance(value, EnhancedFileInput):
            return value.is_enhanced
        elif isinstance(value, FileMetadata):
            return True
        elif isinstance(value, dict):
            return 'original_filename' in value and 'path' in value
        return False
    
    @staticmethod
    def create_enhanced_input(**kwargs) -> EnhancedFileInput:
        """Create an enhanced file input with the given parameters."""
        enhanced_input = EnhancedFileInput(**kwargs)
        return enhanced_input
    
    @staticmethod
    def upgrade_legacy_input(legacy_input: FileInput, original_filename: Optional[str] = None) -> EnhancedFileInput:
        """Upgrade a legacy FileInput to EnhancedFileInput."""
        enhanced_input = EnhancedFileInput(
            name=legacy_input.name,
            display_name=legacy_input.display_name,
            info=legacy_input.info,
            file_types=legacy_input.file_types,
            required=legacy_input.required
        )
        
        # Set the value
        if original_filename:
            # Create enhanced metadata
            metadata = FileMetadata(
                path=str(legacy_input.value) if legacy_input.value else "",
                original_filename=original_filename
            )
            enhanced_input.set_enhanced_value(metadata)
        else:
            # Set as legacy value
            enhanced_input.set_enhanced_value(str(legacy_input.value) if legacy_input.value else "")
        
        return enhanced_input


# Utility functions for components
def get_enhanced_file_info(file_input: Any) -> dict:
    """Get comprehensive file information from any file input type."""
    adapter = FileInputAdapter()
    
    return {
        'path': adapter.get_file_path(file_input),
        'original_filename': adapter.get_original_filename(file_input),
        'is_enhanced': adapter.is_enhanced_input(file_input),
        'content_type': getattr(file_input, 'content_type', None) if hasattr(file_input, 'content_type') else None,
        'file_size': getattr(file_input, 'file_size', None) if hasattr(file_input, 'file_size') else None,
    }


def create_file_metadata(path: str, original_filename: str, **kwargs) -> FileMetadata:
    """Create FileMetadata object with the given parameters."""
    return FileMetadata(
        path=path,
        original_filename=original_filename,
        **kwargs
    )
