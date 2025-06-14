# Exposing the Original Filename End‐to‐End in LangFlow

This document walks you through all the changes needed—backend, cache, frontend, and custom‐component—to carry the **user’s original filename** from the file‐picker into your Python components.

---

## 1. Backend: FastAPI Upload Endpoint

**File:** `src/backend/routes/files.py`

Locate the route that handles file uploads (e.g. `POST /files`). Change it to return both the server‐side cache path **and** the original `UploadFile.filename`:

```python
from fastapi import APIRouter, UploadFile, File
from backend.schemas.file import FileResponse
from backend.service.file_cache import save_to_cache

router = APIRouter()

@router.post("/files", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    cache_path = await save_to_cache(contents)
    return {
        "path": cache_path,
        "original_filename": file.filename,
    }
```

---

## 2. Update the Pydantic Schema

**File:** `src/backend/schemas/file.py`

Extend the `FileResponse` model to include `original_filename`:

```python
from pydantic import BaseModel

class FileResponse(BaseModel):
    path: str
    original_filename: str
```

---

## 3. Cache/Storage Layer

If you persist file metadata in SQLite, add an `original_filename` column; otherwise just propagate it in your in‑memory dict.

**Example in** `src/backend/service/file_cache.py`

```python
def save_to_cache(contents: bytes, filename: str) -> str:
    path = write_bytes_to_disk(contents)
    # store (path, filename) in your DB
    save_metadata_to_db(path, filename)
    return path


def get_cached_file(path: str) -> dict:
    # Fetch metadata from DB or in‑memory store…
    metadata = query_db_for_file(path)
    return {
        "path": path,
        "original_filename": metadata["original_filename"],
        # …other fields…
    }
```

---

## 4. Frontend: FileInput Component

**File:** `web/src/components/FileInput.tsx`

1. Change the upload handler to store an object `{ path, original_filename }`:

   ```ts
   async function handleUpload(file: File) {
     const { path, original_filename } = await api.files.upload(file);
     onChange({ path, original_filename });
   }
   ```

2. Update the component’s value type:

   ```ts
   type FileValue = {
     path: string;
     original_filename: string;
   };
   ```

3. Render the original filename in the UI:

   ```tsx
   <span>
     {value?.original_filename ?? "No file selected"}
   </span>
   ```

---

## 5. Custom Component Consumption

In your `FileMetadataExtractor` (or any component that reads `self.input_file`), treat it as a dict:

```python
# file: file_metadata_extractor.py

class FileMetadataExtractor(Component):
    # … inputs include FileInput(name="input_file", …) …

    def extract_metadata(self) -> Message:
        file_meta = self.input_file  # now a dict
        path = file_meta["path"]
        original = file_meta["original_filename"]
        # … use `original` for your metadata outputs …
```

Remove any brittle DB‑lookup or `os.path.basename` hacks—use the value delivered by FastAPI and the frontend.

---

## 6. Deployment & Testing

1. **Rebuild backend**

   ```bash
   cd langflow
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```

2. **Rebuild frontend**

   ```bash
   cd web
   npm install
   npm run dev
   ```

3. **Restart LangFlow container** (if using Docker)

   ```powershell
   docker run --rm -d -p 7860:7860 \
     -v C:/path/to/custom_components:/app/custom_components \
     -e LANGFLOW_COMPONENTS_PATH=/app/custom_components \
     langflowai/langflow:latest
   ```

4. **Test end‑to‑end**

   * Open the file‑picker in LangFlow UI → select a file → you should see its **real** name displayed.
   * Run your `FileMetadataExtractor` → inspect the “📁 Original Filename” in the summary.

---

### Recap

1. **FastAPI** returns `original_filename`.
2. **Schema & cache** persist and load it.
3. **UI** stores & displays it.
4. **Custom components** simply consume the dict.

This end‑to‑end patch ensures your flows always see the true filename the user uploaded.
