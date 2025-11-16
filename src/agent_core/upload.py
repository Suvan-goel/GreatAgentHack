# python
import os
import uuid
import json
import base64

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.tools import tool

# Config
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store for file requests and uploads
FILE_REQUESTS: dict[str, dict] = {}
# Example entry:
# FILE_REQUESTS[request_id] = {
#   "message": str,
#   "ready": bool,
#   "filename": Optional[str],
#   "path": Optional[str],
#   "mime": Optional[str],
#   "size": Optional[int]
# }

app = FastAPI(title="Agent File Inbox")

# Optional CORS for web UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _new_request_id() -> str:
    return str(uuid.uuid4())

def _safe_name(name: str) -> str:
    return os.path.basename(name)

@tool
def create_file_request(message: str) -> str:
    """
    Create a new file request and return JSON containing:
    - type: "file_request"
    - request_id
    - message
    - upload_url
    """
    request_id = _new_request_id()
    FILE_REQUESTS[request_id] = {
        "message": message,
        "ready": False,
        "filename": None,
        "path": None,
        "mime": None,
        "size": None,
    }
    payload = {
        "type": "file_request",
        "request_id": request_id,
        "message": message,
        "upload_url": f"{PUBLIC_BASE_URL}/upload/{request_id}",
        "status_url": f"{PUBLIC_BASE_URL}/requests/{request_id}",
    }
    return json.dumps(payload)

@tool
def get_uploaded_file(request_id: str, return_base64: bool = True) -> str:
    """
    Fetch uploaded file by request_id.
    Returns JSON containing metadata and optionally base64 content.
    """
    rec = FILE_REQUESTS.get(request_id)
    if not rec:
        raise ValueError("Unknown request_id.")
    if not rec["ready"]:
        return json.dumps({"status": "pending", "request_id": request_id})

    result = {
        "status": "ready",
        "request_id": request_id,
        "filename": rec["filename"],
        "mime": rec["mime"],
        "size": rec["size"],
        "path": rec["path"],
    }

    if return_base64:
        with open(rec["path"], "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        result["base64"] = b64

    return json.dumps(result)

@app.post("/upload/{request_id}")
async def upload_with_request(request_id: str, file: UploadFile = File(...)):
    rec = FILE_REQUESTS.get(request_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Unknown request_id.")

    safe_name = _safe_name(file.filename or "uploaded.bin")
    filepath = os.path.join(UPLOAD_DIR, f"{request_id}__{safe_name}")

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    rec["ready"] = True
    rec["filename"] = safe_name
    rec["path"] = filepath
    rec["mime"] = file.content_type
    rec["size"] = len(content)

    return {
        "status": "success",
        "request_id": request_id,
        "filename": safe_name,
        "stored_at": filepath,
    }

@app.get("/requests/{request_id}")
def get_request_status(request_id: str):
    rec = FILE_REQUESTS.get(request_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Unknown request_id.")
    return {
        "request_id": request_id,
        "message": rec["message"],
        "ready": rec["ready"],
        "filename": rec["filename"],
        "mime": rec["mime"],
        "size": rec["size"],
        "path": rec["path"],
    }
