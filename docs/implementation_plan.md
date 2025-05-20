# Implementation Plan: Minimal Flow Designer Integration

## 1. Overview
This plan describes the steps to implement a minimal, embeddable flow designer for legal-document-automator-pro, using only the required components and integrating tightly with the existing frontend and backend.

---

## 2. Architecture

- **Frontend**: Minimal React component for flow design, using React Flow and only the required node types.
- **Backend**: FastAPI/Supabase backend for file storage, flow execution, and rule management.
- **Integration**: The flow designer is imported and used as a component in the main frontend.

---

## 3. Implementation Steps

### 3.1. Requirements Finalization
- [ ] Confirm the exact list of required node types/components.
- [ ] Define the metamodel structure for mapping fields.

### 3.2. Minimal Flow Designer Extraction
- [ ] Identify and extract the core flow/canvas code from Langflow or React Flow.
- [ ] Remove all global store/context dependencies (Zustand, Redux, etc.).
- [ ] Refactor to use local React state for nodes, edges, and UI state.
- [ ] Register only the selected node types/components.
- [ ] Remove all branding, customization, and extra features.

### 3.3. Node/Component Implementation
- [ ] Implement or adapt nodes for:
    - Local LLM (Llama.cpp, Ollama)
    - PDF extraction/reading/writing
    - Image extraction (OCR)
    - Word/RTF extraction/reading/writing
    - Metamodel mapping
    - Web connector
    - Supabase connector
- [ ] Ensure each node/component has minimal, clear props and interfaces.

### 3.4. Backend/API Integration
- [ ] Ensure Supabase backend supports all required file and metadata operations.
- [ ] Implement API endpoints for flow execution, rule storage, and metamodel management if needed.
- [ ] Test file upload and retrieval from frontend to Supabase.

### 3.5. Frontend Integration
- [ ] Wrap the minimal flow designer as a standalone React component (e.g., `MinimalFlowDesigner`).
- [ ] Import and use it in the main frontend, passing any required props (e.g., user, file list, etc.).
- [ ] Style minimally to fit the main app's layout.

### 3.6. Testing & QA
- [ ] Test all node/component functionality in isolation.
- [ ] Test end-to-end flows: upload, extract, reason, map, generate, and save.
- [ ] Test saving/loading of transformation rules and flows.

### 3.7. Documentation
- [ ] Document the minimal flow designer's API, node/component list, and integration steps.
- [ ] Provide usage examples for common legal automation scenarios.

---

## 4. Responsibilities

- **Frontend Dev**: Extract and refactor flow designer, implement nodes, integrate with main app.
- **Backend Dev**: Ensure API and Supabase support, implement any new endpoints.
- **QA**: Test all features and flows, report bugs.
- **PM/Lead**: Finalize requirements, coordinate between teams, review deliverables.

---

## 5. Timeline (Example)

| Week | Task                                      |
|------|-------------------------------------------|
| 1    | Finalize requirements, node list          |
| 2-3  | Extract/refactor flow designer, implement nodes |
| 4    | Backend/API integration, Supabase testing |
| 5    | Frontend integration, styling             |
| 6    | Testing, bugfixes, documentation          |

---

## 6. Risks & Mitigations

- **Dependency issues**: Use only well-maintained, minimal dependencies.
- **Integration complexity**: Keep interfaces simple, document thoroughly.
- **Feature creep**: Stick to the minimal node/component list.

---

## 7. Deliverables
- Minimal flow designer React component
- Node/component implementations
- Integration with main frontend
- Documentation and usage examples 