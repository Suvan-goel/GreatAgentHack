"""
FastAPI entrypoint for the GroupSync backend.

We keep this small: it just wires HTTP → state manager → agents.

Run with:
  uvicorn groupsync.app:app --reload --app-dir src
(from the repo root, with PYTHONPATH including src)
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .state import (
    get_state,
    reset_state,
    update_project,
    update_team,
    update_tasks,
    set_weekly_plan,
    add_checkins,
)
from .agents.scope_agent import run_scope_agent
from .agents.role_matching_agent import run_role_matching_agent
from .agents.plan_agent import run_plan_agent
from .agents.orchestration import run_weekly_analysis
from .utils.pdf_utils import extract_text_from_pdf

app = FastAPI(title="GroupSync – Group Project Wrangler & Tension Radar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/project/init")
async def init_project(
    deadline: str,
    brief_text: str | None = None,
    file: UploadFile | None = File(default=None),
):
    """
    Initialise project_state from a brief and a deadline.

    - Option A: brief_text param
    - Option B: PDF upload
    """
    reset_state()

    if file is not None:
        raw_bytes = await file.read()
        text = extract_text_from_pdf(raw_bytes)
    else:
        text = brief_text or ""

    # TODO: optionally use agent_core.Agent here
    tasks = run_scope_agent(text, deadline)

    update_project({"title": "Untitled project", "description": text[:200], "deadline": deadline})
    update_tasks(tasks)

    return {"project": get_state()["project"], "tasks": tasks}


@app.post("/project/team")
async def set_team_endpoint(team_members: list[dict]):
    """
    Set team members and generate assignments + weekly plan.
    """
    update_team(team_members)

    state = get_state()
    tasks_with_owners = run_role_matching_agent(state["tasks"], state["team"])
    update_tasks(tasks_with_owners)

    weekly_plan = run_plan_agent(tasks_with_owners, state["team"], state["project"]["deadline"])
    set_weekly_plan(weekly_plan)

    return {
        "tasks": tasks_with_owners,
        "weekly_plan": weekly_plan,
    }


@app.get("/project/state")
def project_state():
    return get_state()


@app.post("/checkins/{week_index}")
async def submit_checkins_endpoint(week_index: int, checkins: list[dict]):
    add_checkins(week_index, checkins)
    snapshot = run_weekly_analysis(week_index)
    return snapshot


@app.get("/week/{week_index}/summary")
def week_summary(week_index: int):
    """
    Return the risk snapshot for a given week, if it exists.
    """
    state = get_state()
    for snap in state["risk_snapshots"]:
        if snap.get("week_index") == week_index:
            return snap
    return {"error": "no snapshot for that week_index"}


@app.get("/debug/state")
def debug_state():
    return get_state()
