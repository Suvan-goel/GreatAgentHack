# python
import asyncio
import os
import uuid
import json
import base64
import time
from typing import Dict, Optional

from dotenv import load_dotenv
from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()

os.environ["USER_AGENT"] = "my-langchain-agent/1.0"

# --------------------------------------------------------------------
# Simple in-memory store for file requests
# --------------------------------------------------------------------
FILE_REQUESTS: Dict[str, Dict] = {}
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

def _new_request_id() -> str:
    return str(uuid.uuid4())

@tool
def create_file_request(message: str) -> str:
    """
    Ask the user to upload a file. Returns JSON with:
    type, request_id, message, upload_url, status_url
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
    Retrieve uploaded file metadata (and optionally base64 contents).
    Returns pending status if not uploaded yet.
    """
    rec = FILE_REQUESTS.get(request_id)
    if not rec:
        return json.dumps({"error": "unknown_request_id", "request_id": request_id})
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
    if return_base64 and rec["path"]:
        try:
            with open(rec["path"], "rb") as f:
                result["base64"] = base64.b64encode(f.read()).decode("utf-8")
        except FileNotFoundError:
            result["file_error"] = "file_missing_on_disk"
    return json.dumps(result)

# --------------------------------------------------------------------
# Helper functions for flow
# --------------------------------------------------------------------
def parse_first_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None

async def agent_request_file(agent, message: str) -> dict:
    """
    Instruct agent to request a file; returns parsed JSON tool output.
    """
    resp = agent.invoke({
        "messages": [
            {"role": "user", "content": message}
        ]
    })
    # The agent may return a dict; scan values for JSON string
    if isinstance(resp, dict):
        for v in resp.values():
            if isinstance(v, str):
                parsed = parse_first_json(v)
                if parsed and parsed.get("type") == "file_request":
                    return parsed
    # Fallback: if direct string
    if isinstance(resp, str):
        parsed = parse_first_json(resp)
        if parsed:
            return parsed
    raise RuntimeError("No file_request JSON found.")

async def poll_file_ready(agent, request_id: str, timeout: int = 180, interval: float = 3.0) -> Optional[dict]:
    """
    Poll using the agent calling get_uploaded_file until ready or timeout.
    """
    start = time.time()
    while time.time() - start < timeout:
        resp = agent.invoke({
            "messages": [
                {"role": "user", "content": f"Check file upload for request_id {request_id}."}
            ]
        })
        candidate = None
        if isinstance(resp, dict):
            for v in resp.values():
                if isinstance(v, str):
                    parsed = parse_first_json(v)
                    if parsed:
                        candidate = parsed
        elif isinstance(resp, str):
            candidate = parse_first_json(resp)

        if candidate and candidate.get("status") == "ready":
            return candidate
        await asyncio.sleep(interval)
    return None

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
async def main():
    tools = [
        create_file_request,
        get_uploaded_file,
    ]

    llm = get_chat_model("claude-3-5-sonnet")
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant.\n"
            "- If the user asks to analyze or read a local file not yet provided, "
            "call create_file_request with a clear message describing which file to upload and its expected format.\n"
            "- After the user uploads, call get_uploaded_file with the request_id to access its contents.\n"
            "- Do not call get_uploaded_file before requesting a file.\n"
        )
    )

    # Phase 1: Ask user for a file
    file_req = await agent_request_file(
        agent,
        "I want to analyze the contents of a CSV named data.csv. Please request it from me."
    )
    print("File request created:", file_req)
    print("Upload URL (share with user):", file_req["upload_url"])

    print("\nWaiting for user to upload via FastAPI endpoint...")
    # User performs: curl -F 'file=@data.csv' <upload_url>

    # Phase 2: Poll until uploaded
    uploaded = await poll_file_ready(agent, file_req["request_id"])
    if not uploaded:
        print("Timeout: file not uploaded.")
        return
    print("Uploaded file metadata:", uploaded)
    if "base64" in uploaded:
        print("Base64 length:", len(uploaded["base64"]))

    # Continue with normal task once file is available
    follow_up = agent.invoke({
        "messages": [
            {"role": "user", "content": "Now summarize the CSV after loading it from the provided data."}
        ]
    })
    print("Follow-up result:", follow_up)

if __name__ == "__main__":
    asyncio.run(main())
