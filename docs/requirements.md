# Legal Document Automator Pro: Minimal Flow Designer Requirements

## 1. Overview
This document outlines the requirements for integrating a minimal, stripped-down version of the Langflow flow designer into the legal-document-automator-pro application. The goal is to provide a focused, user-friendly interface for document automation using only the necessary components, with tight integration into the existing frontend and backend infrastructure.

---

## 2. Functional Requirements

### 2.1. Core Features
- **Flow Designer UI**: Provide a drag-and-drop interface for building document automation flows.
- **Supported Node Types**:
  - Local LLM (Llama.cpp, Ollama)
  - PDF extraction and reasoning
  - Image data extraction and reasoning (OCR)
  - Word (DOCX/RTF) extraction and reasoning
  - PDF/Word reading and writing
  - Metamodel node for mapping extracted fields to template placeholders
  - Web connector for fetching information from the web
  - Supabase connector for file storage and retrieval
- **Flow Execution**: Allow users to execute flows and view results.
- **Transformation Rules**: Enable users to define, save, and reuse transformation rules for mapping and processing document data.
- **File Upload**: Users can upload source documents and templates via the frontend, which are stored in Supabase.

### 2.2. Integration
- **Frontend Integration**: The flow designer must be embeddable as a React component in the main frontend, with no global store or unnecessary customization.
- **Backend Communication**: The frontend communicates with the backend (FastAPI/Supabase) for file operations, flow execution, and rule storage.
- **Minimal Dependencies**: Only include dependencies required for the selected components.

### 2.3. User Experience
- **Minimal UI**: No branding, user profiles, or extra features.
- **Sidebar**: Only display allowed node types.
- **Reusable Flows**: Users can save and load flow templates.

---

## 3. Non-Functional Requirements

- **Performance**: Fast load and execution times.
- **Security**: No direct backend exposure to users; all file and data operations go through the API.
- **Maintainability**: Modular codebase, easy to update node types or add new ones.
- **Portability**: The flow designer should be easily portable to other React-based projects.

---

## 4. Integration Points

- **Supabase**: For file storage, user management, and metadata.
- **Backend API**: For flow execution, transformation rule storage, and metamodel management.
- **Frontend**: Embeddable as a React component or via iframe if needed.

---

## 5. Out of Scope

- Full-featured Langflow UI (only minimal, selected nodes/components)
- Advanced customization, theming, or user management
- Direct backend/server modifications (unless required for new node types)

---

## 6. Open Questions

- Exact list of required node types and their configuration
- Any additional data sources or connectors needed in the future
- Versioning and migration strategy for transformation rules and flows 