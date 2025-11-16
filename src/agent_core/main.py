import os
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)

    content = await file.read()

    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "status": "success",
        "filename": file.filename,
        "stored_at": filepath
    }