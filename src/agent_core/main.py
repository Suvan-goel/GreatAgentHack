import os
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Create directory if needed
    os.makedirs("uploads", exist_ok=True)

    # Read the uploaded file contents
    content = await file.read()

    # Save it locally
    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "status": "success",
        "filename": file.filename,
        "stored_at": filepath
    }