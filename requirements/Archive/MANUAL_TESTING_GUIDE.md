# 🧪 Enhanced Filename Support - Manual Testing Guide

## 📋 **OVERVIEW**

This guide provides step-by-step instructions for manually testing the enhanced filename support in Langflow to verify that original filenames are preserved throughout the user experience.

## 🎯 **TESTING OBJECTIVES**

- ✅ Verify original filenames are preserved during file upload
- ✅ Confirm enhanced metadata extraction works correctly
- ✅ Test component interactions maintain filename context
- ✅ Validate error handling includes original filenames
- ✅ Ensure backward compatibility with existing workflows

## 🚀 **PREREQUISITES**

### **1. Start Enhanced Langflow**
```batch
# Run the enhanced installation (if not done already)
install_langflow_uv_140.bat

# Start Langflow with enhanced features
run_langflow.bat
```

### **2. Verify Enhanced Features Are Active**
Look for this startup message:
```
🚀 Starting Enhanced Langflow...
================================
✅ Original filename preservation: ENABLED
✅ Enhanced metadata extraction: ENABLED
✅ File metadata extractors: READY
✅ Backward compatibility: MAINTAINED
```

### **3. Access Langflow UI**
- Open browser: `http://127.0.0.1:7860/flows`
- Wait for Langflow to fully load

## 📁 **TEST FILES PREPARATION**

Create these test files for comprehensive testing:

### **Test File Set 1: Common Documents**
- `my_important_report.pdf` (any PDF content)
- `quarterly_data_2024.xlsx` (any Excel content)
- `meeting_notes_jan_15.docx` (any Word content)
- `presentation_slides.pptx` (any PowerPoint content)

### **Test File Set 2: Special Characters**
- `file with spaces.txt`
- `file-with-dashes.txt`
- `file_with_underscores.txt`
- `file.with.dots.txt`

### **Test File Set 3: Various Formats**
- `image_photo.jpg` (any image)
- `data_backup.zip` (any archive)
- `config_settings.json` (JSON content)
- `script_code.py` (Python code)

## 🧪 **MANUAL TEST SCENARIOS**

### **Test 1: File Upload with Original Filename Preservation**

#### **Steps:**
1. **Create New Flow**
   - Click "New Flow" or "Blank Flow"
   - Wait for flow designer to load

2. **Add File Input Component**
   - Search for "File" in component sidebar
   - Drag "File" component to canvas
   - Click on the File component to configure

3. **Upload Test File**
   - Click "Upload File" or file upload area
   - Select `my_important_report.pdf`
   - Upload the file

#### **Expected Results:**
- ✅ File uploads successfully
- ✅ Original filename `my_important_report.pdf` is displayed (not a UUID)
- ✅ File path shows server location but UI shows original name
- ✅ No error messages

#### **Verification Points:**
- [ ] Original filename visible in component
- [ ] File upload confirmation shows original name
- [ ] Component configuration shows original filename

---

### **Test 2: Enhanced File Metadata Extractor Component**

#### **Steps:**
1. **Add File Metadata Extractor**
   - Search for "File Metadata Extractor" in components
   - Drag component to canvas
   - Connect File component output to Metadata Extractor input

2. **Configure Metadata Extractor**
   - Click on File Metadata Extractor component
   - Verify enhanced options are available
   - Enable "Extract Original Filename" if not already enabled

3. **Run the Flow**
   - Click "Run" or "Execute" button
   - Wait for processing to complete

#### **Expected Results:**
- ✅ Component found in component library
- ✅ Enhanced configuration options available
- ✅ Execution successful
- ✅ Output includes original filename `my_important_report.pdf`
- ✅ Metadata shows file properties with original name

#### **Verification Points:**
- [ ] File Metadata Extractor component available
- [ ] Enhanced configuration options visible
- [ ] Original filename in output
- [ ] Rich metadata extracted and displayed

---

### **Test 3: Component Chain with Filename Preservation**

#### **Steps:**
1. **Create Component Chain**
   - File Input → File Metadata Extractor → Text Output
   - Connect components in sequence

2. **Upload Different File Types**
   - Test with `quarterly_data_2024.xlsx`
   - Test with `meeting_notes_jan_15.docx`
   - Test with `presentation_slides.pptx`

3. **Execute Flow for Each File**
   - Run flow with each file type
   - Check output at each stage

#### **Expected Results:**
- ✅ All file types process successfully
- ✅ Original filenames preserved through entire chain
- ✅ Text output includes original filename context
- ✅ No filename corruption or UUID substitution

#### **Verification Points:**
- [ ] Excel file: `quarterly_data_2024.xlsx` preserved
- [ ] Word file: `meeting_notes_jan_15.docx` preserved
- [ ] PowerPoint file: `presentation_slides.pptx` preserved
- [ ] Filename context maintained in final output

---

### **Test 4: Special Characters and Edge Cases**

#### **Steps:**
1. **Test Files with Spaces**
   - Upload `file with spaces.txt`
   - Verify filename handling

2. **Test Files with Special Characters**
   - Upload `file-with-dashes.txt`
   - Upload `file_with_underscores.txt`
   - Upload `file.with.dots.txt`

3. **Check Display and Processing**
   - Verify each filename displays correctly
   - Run metadata extraction on each

#### **Expected Results:**
- ✅ All special characters preserved
- ✅ Spaces in filenames handled correctly
- ✅ Dashes, underscores, and dots preserved
- ✅ No filename sanitization that loses information

#### **Verification Points:**
- [ ] Spaces preserved: `file with spaces.txt`
- [ ] Dashes preserved: `file-with-dashes.txt`
- [ ] Underscores preserved: `file_with_underscores.txt`
- [ ] Dots preserved: `file.with.dots.txt`

---

### **Test 5: Error Handling with Filename Context**

#### **Steps:**
1. **Test Unsupported File Type**
   - Create file with unusual extension: `test.unknown`
   - Try to upload and process

2. **Test Large File (if applicable)**
   - Create or use a large file
   - Attempt upload

3. **Test Corrupted File**
   - Create a file with wrong extension (e.g., rename .txt to .pdf)
   - Try to process

#### **Expected Results:**
- ✅ Error messages include original filename
- ✅ User can identify which file caused the error
- ✅ Error handling is user-friendly
- ✅ Original filename context preserved in error messages

#### **Verification Points:**
- [ ] Error message mentions `test.unknown` by name
- [ ] Large file error includes original filename
- [ ] Corrupted file error shows original filename
- [ ] Error messages are helpful and specific

---

### **Test 6: Backward Compatibility**

#### **Steps:**
1. **Test with Legacy Components**
   - Use standard Langflow components (not enhanced ones)
   - Upload files through legacy file inputs

2. **Mix Legacy and Enhanced Components**
   - Legacy File Input → Enhanced Metadata Extractor
   - Test compatibility

3. **Verify Graceful Fallback**
   - Check that enhanced components work with legacy inputs
   - Verify no breaking changes

#### **Expected Results:**
- ✅ Legacy components continue to work
- ✅ Enhanced components handle legacy inputs gracefully
- ✅ Filename extraction works even with legacy inputs
- ✅ No breaking changes to existing workflows

#### **Verification Points:**
- [ ] Legacy file inputs still functional
- [ ] Enhanced components accept legacy inputs
- [ ] Filename extraction from legacy paths works
- [ ] No workflow disruption

---

### **Test 7: Performance and Bulk Operations**

#### **Steps:**
1. **Upload Multiple Files**
   - Upload 5-10 files of different types
   - Process them through metadata extractor

2. **Check Processing Speed**
   - Time the operations
   - Verify reasonable performance

3. **Verify All Filenames Preserved**
   - Check that all original filenames are maintained
   - No performance degradation

#### **Expected Results:**
- ✅ Multiple files process efficiently
- ✅ All original filenames preserved
- ✅ No significant performance impact
- ✅ Bulk operations maintain filename integrity

#### **Verification Points:**
- [ ] Multiple file upload works smoothly
- [ ] Processing time is reasonable
- [ ] All filenames preserved in bulk operations
- [ ] No memory or performance issues

## 📊 **TEST RESULTS CHECKLIST**

### **Core Functionality**
- [ ] File upload preserves original filenames
- [ ] Enhanced File Metadata Extractor component available
- [ ] Component chains maintain filename context
- [ ] Special characters in filenames handled correctly

### **User Experience**
- [ ] Original filenames visible throughout UI
- [ ] Error messages include filename context
- [ ] Component configuration is user-friendly
- [ ] Flow execution shows filename preservation

### **Compatibility**
- [ ] Legacy components continue to work
- [ ] Enhanced components handle legacy inputs
- [ ] No breaking changes to existing workflows
- [ ] Graceful fallback for unsupported scenarios

### **Performance**
- [ ] File upload performance acceptable
- [ ] Metadata extraction is fast
- [ ] Bulk operations work efficiently
- [ ] No memory leaks or performance degradation

## 🎯 **SUCCESS CRITERIA**

### **✅ PASS Criteria**
- All core functionality tests pass
- Original filenames preserved in all scenarios
- Enhanced components work as expected
- Backward compatibility maintained
- User experience is positive

### **❌ FAIL Criteria**
- Original filenames lost or corrupted
- Enhanced components not available
- Breaking changes to existing workflows
- Poor user experience or confusing UI
- Performance significantly degraded

## 🔧 **TROUBLESHOOTING**

### **If Enhanced Components Not Found:**
1. Check that enhanced features are enabled in startup
2. Verify `.env` file contains feature flags
3. Restart Langflow with `run_langflow.bat`

### **If Filenames Not Preserved:**
1. Check browser console for errors
2. Verify enhanced filename implementation is active
3. Test with different file types

### **If Performance Issues:**
1. Check file sizes (very large files may be slow)
2. Monitor browser memory usage
3. Test with fewer files

## 📝 **REPORTING RESULTS**

After completing manual testing, document:

1. **Test Environment**
   - Langflow version
   - Browser used
   - Operating system

2. **Test Results**
   - Which tests passed/failed
   - Any unexpected behavior
   - Performance observations

3. **User Experience Feedback**
   - Ease of use
   - Clarity of filename display
   - Quality of error messages

4. **Recommendations**
   - Any improvements needed
   - Additional features desired
   - Documentation updates required

---

**🎉 Congratulations on completing the manual testing!**

Your feedback helps ensure the enhanced filename support provides the best possible user experience in Langflow.
