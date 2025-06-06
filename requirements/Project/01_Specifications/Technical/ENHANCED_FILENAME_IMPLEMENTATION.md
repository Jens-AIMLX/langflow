# Enhanced Filename Exposure Implementation

This document describes the complete implementation of the enhanced filename exposure system for Langflow, providing backward-compatible access to original filenames throughout the application.

## 🎯 Overview

The enhanced filename exposure system solves the fundamental problem where Langflow components only receive UUID-based server paths instead of the original filenames uploaded by users. This implementation provides:

- **Zero Breaking Changes**: All existing functionality remains unchanged
- **Enhanced Capabilities**: New components can access original filenames directly
- **Gradual Migration**: Users can opt into enhanced features when ready
- **Backward Compatibility**: Legacy components continue to work exactly as before

## 🏗️ Architecture

### Core Components

1. **Database Layer**: Enhanced metadata storage alongside existing tables
2. **API Layer**: New v2 endpoints with enhanced file handling
3. **Input Layer**: Enhanced FileInput classes with metadata support
4. **Component Layer**: Backward-compatible component base classes
5. **Migration Layer**: Utilities to migrate existing files

### Data Flow

```
User Upload → Enhanced API → Enhanced Metadata Storage → Enhanced Components → Original Filename Access
     ↓              ↓                    ↓                       ↓                      ↓
Legacy Upload → Legacy API → Legacy Storage → Legacy Components → Database Lookup Fallback
```

## 📁 File Structure

```
src/backend/base/langflow/
├── api/v2/
│   ├── enhanced_files.py          # Enhanced file API endpoints
│   └── schemas.py                 # Enhanced schemas and types
├── services/
│   ├── database/models/
│   │   └── file_metadata.py       # Enhanced metadata models
│   ├── migration/
│   │   └── file_migration.py      # Migration utilities
│   └── settings/
│       └── feature_flags.py       # Feature flag for enhanced files
├── inputs/
│   └── enhanced_inputs.py         # Enhanced FileInput classes
├── custom/
│   └── enhanced_component.py      # Enhanced component base classes
└── alembic/versions/
    └── add_enhanced_file_metadata.py  # Database migration

custom_nodes/
└── file_metadata_extractor.py     # Updated with enhanced support

scripts/
└── migrate_enhanced_files.py      # CLI migration tool

test_enhanced_filename_implementation.py  # Comprehensive test suite
```

## 🚀 Quick Start

### 1. Enable Enhanced Features

Set the feature flag:
```bash
export LANGFLOW_FEATURE_ENHANCED_FILE_INPUTS=true
```

### 2. Run Database Migration

```bash
# Apply the enhanced metadata table migration
python -m alembic upgrade head
```

### 3. Test the Implementation

```bash
# Run comprehensive tests
python test_enhanced_filename_implementation.py

# Test database connection
python scripts/migrate_enhanced_files.py test-connection
```

### 4. Migrate Existing Files (Optional)

```bash
# Check migration status
python scripts/migrate_enhanced_files.py status

# Migrate all files
python scripts/migrate_enhanced_files.py migrate

# Migrate specific user's files
python scripts/migrate_enhanced_files.py migrate --user-id <user_id>
```

## 💻 Usage Examples

### Enhanced Component Development

```python
from langflow.custom.enhanced_component import BackwardCompatibleComponent
from langflow.io import FileInput, Output
from langflow.schema import Message

class MyEnhancedComponent(BackwardCompatibleComponent):
    inputs = [
        FileInput(
            name="input_file",
            display_name="Input File",
            file_types=["pdf", "txt", "docx"],
            required=True
        )
    ]
    
    outputs = [
        Output(display_name="Result", name="result", method="process_file")
    ]
    
    def process_file(self) -> Message:
        # Get comprehensive file information
        file_info = self.get_file_info_universal('input_file')
        
        original_filename = file_info['original_filename']
        file_path = file_info['path']
        is_enhanced = file_info['is_enhanced']
        
        # Process the file
        result = f"Processing {original_filename} ({'enhanced' if is_enhanced else 'legacy'} format)"
        
        return Message(text=result)
```

### Enhanced API Usage

```python
# Upload file with enhanced metadata
import aiohttp

async def upload_enhanced_file(file_path, original_filename):
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=original_filename)
            
            async with session.post('/api/v2/files/enhanced/upload', data=data) as resp:
                result = await resp.json()
                
                # Result contains both server path and original filename
                return {
                    'server_path': result['file_path'],
                    'original_filename': result['original_filename'],
                    'file_id': result['file_id']
                }
```

### Legacy Component Compatibility

```python
from langflow.custom import Component
from langflow.io import FileInput, Output

class LegacyComponent(Component):
    """This component works exactly as before - no changes needed!"""
    
    inputs = [
        FileInput(name="file_input", display_name="File Input", required=True)
    ]
    
    def process(self):
        # This continues to work exactly as before
        file_path = self.file_input
        return f"Processing: {file_path}"
```

## 🔧 Configuration

### Feature Flags

The enhanced filename system is controlled by feature flags:

```python
# In settings/feature_flags.py
class FeatureFlags(BaseSettings):
    enhanced_file_inputs: bool = False  # Set to True to enable
```

Environment variable:
```bash
export LANGFLOW_FEATURE_ENHANCED_FILE_INPUTS=true
```

### Database Configuration

The enhanced system adds a new table `file_metadata_enhanced` alongside existing tables:

```sql
CREATE TABLE file_metadata_enhanced (
    id UUID PRIMARY KEY,
    file_path VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    content_type VARCHAR,
    file_size BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    user_id UUID REFERENCES user(id),
    flow_id VARCHAR
);
```

## 🔄 Migration Guide

### Automatic Migration

Use the CLI tool to migrate existing files:

```bash
# Check what needs migration
python scripts/migrate_enhanced_files.py status

# Migrate all files
python scripts/migrate_enhanced_files.py migrate

# Migrate with dry run first
python scripts/migrate_enhanced_files.py migrate --dry-run
```

### Manual Migration

For specific files or custom migration logic:

```python
from langflow.services.migration.file_migration import FileMigrationService

async def migrate_specific_file():
    async with get_session() as session:
        migration_service = FileMigrationService(session)
        
        result = await migration_service.migrate_file_metadata(
            file_path="/path/to/server/file.txt",
            original_filename="user_document.txt"
        )
        
        print(f"Migrated: {result.original_filename}")
```


'''... remaining content of ENHANCED_FILENAME_IMPLEMENTATION.md ...''' 