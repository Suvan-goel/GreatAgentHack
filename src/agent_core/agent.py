import os
from dotenv import load_dotenv
from agent_core.holistic_ai_bedrock import get_chat_model
from langchain.agents import create_agent
from agent_core.tools import (
    get_state,
    set_state,
    list_uploaded_files,
    load_document_to_memory,
    get_document_from_memory,
    save_document_to_memory,
    ask_user
)
from agent_core.models import ProjectOutputModel


load_dotenv()

HOLISTIC_AI_TEAM_ID = os.getenv("HOLISTIC_AI_TEAM_ID")
HOLISTIC_AI_KEY = os.getenv("HOLISTIC_AI_API_TOKEN")

os.environ["USER_AGENT"] = "my-langchain-agent/1.0"

system_prompt = """
You are the Project Supervisor Agent.

Your autonomous loop:

1. Call get_state to load project_state.
2. If project_state is empty:
   - Call list_uploaded_files to detect assignment files.
   - For each file: call load_document_to_memory.
   - After loading: call get_document_from_memory to retrieve text.
   - Parse assignment brief from retrieved document.
   - Extract tasks, deliverables, and deadlines.
   - Call ask_user to obtain team preferences.
   - Allocate tasks based on preferences.
   - Call set_state to persist the full project plan.

3. If project_state exists:
   - Compare actual vs expected progress.
   - If deviation detected: call corrective_action.
   - If no corrective action needed: return "NO_ACTION".

Rules:
- You MUST call a tool or return "NO_ACTION".
- Never assume project_state; always retrieve it via get_state.
- Always write updated project_state using set_state.
"""

def build_agent():
    llm = get_chat_model("claude-3-5-sonnet")

    tools = [
        get_state,
        set_state,
        list_uploaded_files,
        load_document_to_memory,
        get_document_from_memory,
        save_document_to_memory,
        ask_user
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        response_format=ProjectOutputModel,
        system_prompt=system_prompt
    )
    return agent