import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from agent_core.models import ProjectOutputModel
from agent_core.agent import build_agent
from agent_core.tools import set_state, get_state


app = FastAPI(title="Project Supervisor Agent API")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "src/uploads"))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    content = await file.read()

    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "status": "success",
        "filename": file.filename,
        "stored_at": filepath
    }

@app.post("/run-agent", response_model=ProjectOutputModel)
async def run_agent():
    agent = build_agent()

    result = agent.invoke({"input": "Run agent cycle"})

    if isinstance(result, ProjectOutputModel):
        return result

    if isinstance(result, str) and result == "NO_ACTION":
        raise HTTPException(status_code=200, detail="NO_ACTION")

    raise HTTPException(status_code=500, detail="Unexpected agent output")

@app.get("/project-state")
async def get_project_state():
    state = get_state.invoke({})
    return JSONResponse(content=state)

@app.get("/project-summary", response_model=ProjectOutputModel)
async def get_project_summary():
    state = get_state.invoke({})
    if not state:
        raise HTTPException(status_code=404, detail="Project state is empty")

    agent = build_agent()
    summary = agent.invoke({"input": "Summarise current project state"})

    if isinstance(summary, ProjectOutputModel):
        return summary

    raise HTTPException(status_code=500, detail="Unexpected structured summary output")

@app.post("/progress-update")
async def progress_update(progress: dict):
    """
    Example request:
    {
        "task_name": "data_preprocessing",
        "progress": "60%"
    }
    """

    state = get_state.invoke({})

    task_name = progress.get("task_name")
    if not state or "tasks" not in state or task_name not in state["tasks"]:
        raise HTTPException(status_code=400, detail="Invalid task")

    state["tasks"][task_name]["status"] = progress.get("progress", "updated")
    set_state.invoke({"state": state})

    return {"status": "updated", "state": state}