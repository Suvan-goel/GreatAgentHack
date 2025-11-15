"""
In-memory state manager for GroupSync.

All runtime data for the single active project lives in project_state.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List

project_state: Dict[str, Any] = {
    "project": {"title": "", "description": "", "deadline": ""},
    "team": [],
    "tasks": [],
    "weekly_plan": [],
    "checkins": [],
    "risk_snapshots": [],
    "run_logs": [],
}


def reset_state() -> None:
    """Reset project_state to its initial empty structure."""
    global project_state
    project_state = {
        "project": {"title": "", "description": "", "deadline": ""},
        "team": [],
        "tasks": [],
        "weekly_plan": [],
        "checkins": [],
        "risk_snapshots": [],
        "run_logs": [],
    }


def get_state() -> Dict[str, Any]:
    """Return the current project_state."""
    return project_state


def update_project(project_data: Dict[str, Any]) -> None:
    project_state["project"].update(project_data)


def update_team(team_members: List[Dict[str, Any]]) -> None:
    project_state["team"] = team_members


def update_tasks(tasks: List[Dict[str, Any]]) -> None:
    project_state["tasks"] = tasks


def set_weekly_plan(weekly_plan: List[Dict[str, Any]]) -> None:
    project_state["weekly_plan"] = weekly_plan


def add_checkins(week_index: int, checkins: List[Dict[str, Any]]) -> None:
    for chk in checkins:
        chk["week_index"] = week_index
        project_state["checkins"].append(chk)


def add_risk_snapshot(snapshot: Dict[str, Any]) -> None:
    project_state["risk_snapshots"].append(snapshot)


def add_run_log(action: str, agents: List[str], status: str) -> None:
    project_state["run_logs"].append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "agents": agents,
            "status": status,
        }
    )
