from langflow.custom import Component
from langflow.inputs.enhanced_inputs import EnhancedFileInput, FileInputAdapter, get_enhanced_file_info
from langflow.api.v2.schemas import FileMetadata
from typing import Union, Optional, Any, Dict
import os


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
        # Try enhanced metadata first
        metadata = self.get_file_metadata(input_name)
        if metadata:
            return metadata.original_filename
        
        # Try direct attribute access
        file_value = getattr(self, input_name, None)
        if file_value:
            return FileInputAdapter.get_original_filename(file_value)
        
        # Final fallback
        return "unknown_file"
    
    def get_file_path(self, input_name: str) -> str:
        """Get file path (server path) for a file input."""
        # Try enhanced metadata first
        metadata = self.get_file_metadata(input_name)
        if metadata:
            return metadata.path
        
        # Try direct attribute access
        file_value = getattr(self, input_name, None)
        if file_value:
            return FileInputAdapter.get_file_path(file_value)
        
        return ""
    
    def get_file_info(self, input_name: str) -> Dict[str, Any]:
        """Get comprehensive file information for a file input."""
        file_value = getattr(self, input_name, None)
        if file_value:
            return get_enhanced_file_info(file_value)
        
        return {
            'path': '',
            'original_filename': 'unknown_file',
            'is_enhanced': False,
            'content_type': None,
            'file_size': None,
        }
    
    def get_file_info_universal(self, input_name: str) -> Dict[str, Any]:
        """
        Universal file info extraction with comprehensive fallback strategy.
        This method works with any file input format and provides consistent results.
        """
        # Step 1: Try to get the file value from the component
        file_value = getattr(self, input_name, None)
        if not file_value:
            return {
                'path': '',
                'original_filename': 'no_file',
                'is_enhanced': False,
                'detection_method': 'no_file',
                'error': 'No file input found'
            }
            
        # Step 2: Check if we have an enhanced file input
        is_enhanced = False
        detection_method = 'legacy'
        original_filename = ''
        file_path = ''
        
        # Try enhanced metadata
        if hasattr(self, '_inputs') and input_name in self._inputs:
            file_input = self._inputs[input_name]
            if isinstance(file_input, EnhancedFileInput) and file_input.is_enhanced:
                is_enhanced = True
                detection_method = 'enhanced_input'
                original_filename = file_input.original_filename
                file_path = file_input.get_file_path()
        
        # If not enhanced, try adapter approach
        if not is_enhanced:
            if isinstance(file_value, dict) and 'original_filename' in file_value:
                is_enhanced = True
                detection_method = 'dict_format'
                original_filename = file_value['original_filename']
                file_path = file_value.get('path', '')
            elif hasattr(file_value, 'original_filename') and hasattr(file_value, 'path'):
                is_enhanced = True
                detection_method = 'object_format'
                original_filename = file_value.original_filename
                file_path = file_value.path
            else:
                # Fallback to string path and database lookup
                detection_method = 'legacy_fallback'
                file_path = str(file_value)
                original_filename = self._legacy_filename_lookup(file_path)
        
        # Step 3: Get file system information if available
        file_size = None
        content_type = None
        
        if os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path)
                import mimetypes
                content_type = mimetypes.guess_type(original_filename)[0]
            except Exception:
                pass
        
        # Step 4: Return comprehensive info
        return {
            'path': file_path,
            'original_filename': original_filename,
            'is_enhanced': is_enhanced,
            'detection_method': detection_method,
            'content_type': content_type,
            'file_size': file_size,
        }
    
    def is_enhanced_input(self, input_name: str) -> bool:
        """Check if a file input uses enhanced metadata."""
        file_value = getattr(self, input_name, None)
        return FileInputAdapter.is_enhanced_input(file_value)
    
    def _legacy_filename_lookup(self, file_path: str) -> str:
        """Legacy filename lookup for backward compatibility."""
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



class BackwardCompatibleComponent(EnhancedComponent):
    """
    Backward compatible component that provides enhanced file support
    while maintaining full compatibility with existing Langflow components.

    This class serves as a bridge between legacy and enhanced file handling,
    providing automatic detection and graceful fallbacks.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._enhanced_mode = True  # Enable enhanced features by default

    def get_file_info_universal(self, input_name: str) -> Dict[str, Any]:
        """
        Universal file info extraction with comprehensive fallback strategy.
        This method works with any file input format and provides consistent results.
        """
        # Use the parent class method but add backward compatibility enhancements
        info = super().get_file_info_universal(input_name)

        # Add backward compatibility metadata
        info['compatibility_info'] = {
            'component_type': 'backward_compatible',
            'enhanced_mode': self._enhanced_mode,
            'fallback_available': True,
            'migration_ready': True
        }

        return info

    def create_file_summary(self, input_name: str) -> str:
        """Create enhanced file summary with backward compatibility indicators."""
        info = self.get_file_info_universal(input_name)

        if info.get('error'):
            return f"❌ Error: {info['error']}"

        lines = []

        # Backward compatibility header
        lines.append("🔄 BACKWARD COMPATIBLE FILE PROCESSING")
        lines.append("=" * 45)

        # Enhanced vs Legacy indicator with migration info
        if info['is_enhanced']:
            lines.append("✨ Enhanced File Input - Full metadata available")
            lines.append("🚀 Migration Status: Already enhanced")
        else:
            lines.append("🔄 Legacy File Input - Using fallback methods")
            lines.append("📈 Migration Status: Ready for enhancement")

        # Basic file info
        lines.extend([
            f"📁 Original Filename: {info['original_filename']}",
            f"🗂️ Server Path: {os.path.basename(info['path'])}",
            f"🔍 Detection Method: {info['detection_method']}"
        ])

        # Additional metadata if available
        if info.get('content_type'):
            lines.append(f"🏷️ Content Type: {info['content_type']}")

        if info.get('file_size'):
            # Format file size
            size = info['file_size']
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    lines.append(f"📏 File Size: {size:.1f} {unit}")
                    break
                size /= 1024.0

        # Compatibility information
        compat = info.get('compatibility_info', {})
        lines.extend([
            "",
            "🔧 COMPATIBILITY INFORMATION",
            f"   Component Type: {compat.get('component_type', 'unknown')}",
            f"   Enhanced Mode: {'Enabled' if compat.get('enhanced_mode') else 'Disabled'}",
            f"   Fallback Available: {'Yes' if compat.get('fallback_available') else 'No'}",
            f"   Migration Ready: {'Yes' if compat.get('migration_ready') else 'No'}"
        ])

        return "\n".join(lines)

    def enable_enhanced_mode(self):
        """Enable enhanced file processing features."""
        self._enhanced_mode = True

    def disable_enhanced_mode(self):
        """Disable enhanced features and use legacy mode only."""
        self._enhanced_mode = False

    def is_enhanced_mode(self) -> bool:
        """Check if enhanced mode is enabled."""
        return self._enhanced_mode

    def get_migration_info(self, input_name: str) -> Dict[str, Any]:
        """Get information about migration status for a file input."""
        info = self.get_file_info_universal(input_name)

        return {
            'current_format': 'enhanced' if info['is_enhanced'] else 'legacy',
            'migration_needed': not info['is_enhanced'],
            'migration_available': True,
            'benefits': [
                'Preserved original filenames',
                'Enhanced metadata support',
                'Better error handling',
                'Performance improvements'
            ] if not info['is_enhanced'] else ['Already enhanced'],
            'compatibility_maintained': True
        }


# Utility functions for any component to use
def get_enhanced_file_info_universal(component: Component, input_name: str) -> Dict[str, Any]:
    """
    Universal utility function to get file info from any component.
    This works with both enhanced and legacy components.
    """
    if isinstance(component, (EnhancedComponent, BackwardCompatibleComponent)):
        return component.get_file_info_universal(input_name)
    else:
        # Fallback for regular components
        file_value = getattr(component, input_name, None)
        if file_value:
            return get_enhanced_file_info(file_value)
        else:
            return {
                'path': '',
                'original_filename': 'no_file',
                'is_enhanced': False,
                'content_type': None,
                'file_size': None,
                'detection_method': 'fallback_component'
            }


def create_enhanced_file_input(name: str, display_name: str, **kwargs) -> EnhancedFileInput:
    """Factory function to create enhanced file inputs."""
    return EnhancedFileInput(
        name=name,
        display_name=display_name,
        **kwargs
    )


def migrate_component_to_enhanced(component: Component, file_input_names: list) -> None:
    """
    Migrate a component's file inputs to enhanced format.
    This is a utility for gradual migration.
    """
    for input_name in file_input_names:
        if hasattr(component, '_inputs') and input_name in component._inputs:
            legacy_input = component._inputs[input_name]
            if not isinstance(legacy_input, EnhancedFileInput):
                # Upgrade to enhanced input
                enhanced_input = FileInputAdapter.upgrade_legacy_input(legacy_input)
                component._inputs[input_name] = enhanced_input
