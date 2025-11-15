"""
ScopeAgent: turn project brief into structured tasks.

We can optionally use agent_core.Agent here as a wrapper around the LLM.
"""

from typing import List, Dict
# these imports come from your existing code:
from agent_core.agent import Agent  # type: ignore
from agent_core.memory import Memory  # type: ignore
from agent_core.tools import Tool  # type: ignore


def run_scope_agent(brief_text: str, deadline: str) -> List[Dict]:
    """
    Call the LLM (via agent_core.Agent) to parse the brief and generate tasks.

    For now this is just a placeholder; we only show how it connects to agent_core.
    """
    # Example shape – adjust to match how agent_core.Agent actually works:
    agent = Agent(
        system_prompt="You are a helpful planner that breaks a uni group project into tasks.",
        memory=Memory(),
        tools=[],  # add Tool instances later if needed
    )

    # TODO: define proper prompt + output schema
    _ = agent  # avoid unused warning

    # Placeholder: return a single fake task so the pipeline is wired up.
    return [
        {
            "id": "task_1",
            "title": "Read the brief",
            "description": "Understand the assignment requirements.",
            "package": "Planning",
            "estimated_hours": 2,
            "dependencies": [],
        }
    ]
