# File Metadata Extractor Component

A comprehensive Langflow custom component that extracts detailed metadata from uploaded files, including the original filename (not the UUID-based server filename).

## Features

### 🔍 **Comprehensive Metadata Extraction**
- **File System Attributes**: Original filename, file size, file extension, timestamps
- **Document Properties**: Title, author, subject, keywords, page/word count
- **Image Properties**: Dimensions, color depth, format, EXIF data
- **Archive Properties**: File count, compression ratio, file listings

### 📁 **Supported File Types**
- **Documents**: PDF, DOC, DOCX, RTF, TXT
- **Images**: JPG, JPEG, PNG, GIF, BMP
- **Archives**: ZIP, TAR, GZ, TGZ

### 🗄️ **Database Integration**
- Queries Langflow's file database to retrieve original filenames
- Handles UUID-based server paths transparently
- Graceful fallback when database lookup fails

### 📊 **Output Format**
- Human-readable summary with key file attributes
- Structured JSON metadata for programmatic use
- Comprehensive error reporting and extraction logs

## Installation

### 1. Copy Component File
```bash
cp file_metadata_extractor.py /path/to/langflow/custom_nodes/
```

### 2. Install Optional Dependencies
```bash
pip install -r metadata_extractor_requirements.txt
```

**Required for full functionality:**
- `PyPDF2>=3.0.0` - PDF metadata extraction
- `python-docx>=0.8.11` - Word document metadata
- `pyth>=0.7.0` - RTF document metadata  
- `Pillow>=9.0.0` - Image metadata and EXIF data

## Usage

### 1. Add Component to Flow
- In Langflow, add the "File Metadata Extractor" component to your flow
- Connect a FileInput or file source to the component

### 2. Upload File
- Upload any supported file type through the FileInput
- The component automatically detects file type and applies appropriate extraction methods

### 3. View Results
The component outputs a Message containing:

#### **Summary Section**
```
=== FILE METADATA SUMMARY ===
📁 Original Filename: gmbhsatzungkurz (1).RTF
📏 File Size: 2.3 KB
🏷️ File Type: .rtf (application/rtf)
📅 Modified: 2024-01-15 14:30:25
📝 Words: 1,247
📄 Pages: 3
👤 Author: John Doe
🔍 Extraction: 3 successful, 0 failed
```

#### **Detailed JSON Metadata**
```json
{
  "extraction_timestamp": "2024-01-15T14:30:25.123456",
  "extractor_version": "1.0.0",
  "file_system": {
    "original_filename": "gmbhsatzungkurz (1).RTF",
    "server_path": "C:\\...\\uuid.RTF",
    "file_size_bytes": 2345,
    "file_size_human": "2.3 KB",
    "file_extension": ".rtf",
    "mime_type": "application/rtf"
  },
  "document_properties": {
    "document_type": "RTF Document",
    "word_count": 1247,
    "character_count": 8934,
    "line_count": 45
  },
  "extraction_log": [
    "✅ File system metadata extracted successfully",
    "✅ Document metadata extracted successfully"
  ]
}
```

## Technical Implementation

### Original Filename Resolution
The component uses a multi-strategy approach to resolve original filenames:

1. **Primary Strategy**: Access `_inputs['input_file'].value` (most reliable)
2. **Fallback Strategy**: Direct SQLite query to Langflow database
3. **Final Fallback**: Use server filename basename

### Database Integration
```python
def get_original_filename(self, file_path: str) -> str:
    # Extract relative path from server path
    relative_path = f"{user_id}/{uuid_filename}"
    
    # Query Langflow database
    cursor.execute("SELECT name FROM file WHERE path = ?", (relative_path,))
    result = cursor.fetchone()
    
    return result[0] if result else os.path.basename(file_path)
```

### Error Handling
- Graceful degradation when optional libraries are missing
- Comprehensive error reporting for each extraction method
- Extraction continues even if individual methods fail
- Detailed logging of success/failure for each metadata type

## Example Output for Different File Types

### PDF Document
```
📁 Original Filename: research_paper.pdf
📏 File Size: 1.2 MB
📄 Pages: 15
📝 Words: 4,523
📋 Title: Advanced Machine Learning Techniques
👤 Author: Dr. Jane Smith
📅 Created: 2024-01-10 09:15:30
```

### Image File
```
📁 Original Filename: vacation_photo.jpg
📏 File Size: 3.4 MB
🖼️ Dimensions: 4032x3024
🎨 Format: JPEG
📷 Camera: Canon EOS R5
📅 Taken: 2024-01-12 15:45:22
```

### Archive File
```
📁 Original Filename: project_backup.zip
📏 File Size: 15.7 MB
📦 Files in Archive: 127
🗜️ Compression: 68.3%
📁 Contains: src/, docs/, tests/, README.md...
```

## Error Scenarios

### Missing Dependencies
```
❌ Document metadata extraction failed: PyPDF2 not installed
ℹ️ Install with: pip install PyPDF2>=3.0.0
```

### Corrupted Files
```
❌ Image metadata extraction failed: cannot identify image file
✅ File system metadata extracted successfully
```

### Unsupported File Types
```
ℹ️ Unsupported file type for content extraction: .xyz
✅ File system metadata extracted successfully
```

## Integration with File Management Systems

This component serves as a foundation for building file management applications on Langflow:

### Use Cases
- **Document Management**: Organize files by author, creation date, content type
- **Digital Asset Management**: Catalog images with EXIF data and dimensions
- **Archive Analysis**: Inventory compressed files and their contents
- **Content Search**: Index documents by title, author, and keywords
- **File Validation**: Verify file integrity and extract technical specifications

### Workflow Integration
```
File Upload → Metadata Extractor → Database Storage → Search Index → File Browser
```

## Troubleshooting

### Original Filename Shows UUID
- **Cause**: Database lookup failed or frontend not sending original filename
- **Solution**: Check Langflow database connectivity and file upload process

### Missing Metadata Fields
- **Cause**: Optional dependencies not installed or file format limitations
- **Solution**: Install required packages and check extraction logs

### Performance Issues
- **Cause**: Large files or complex archives
- **Solution**: Consider file size limits and async processing for large files

## Contributing

To extend the component:

1. **Add New File Types**: Implement extraction methods for additional formats
2. **Enhanced Metadata**: Extract more specific properties for existing types
3. **Performance Optimization**: Add caching and async processing
4. **Database Integration**: Support additional database backends

## License

This component is designed for use with Langflow and follows the same licensing terms.
