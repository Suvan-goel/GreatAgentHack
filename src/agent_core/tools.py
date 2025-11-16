import os
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langgraph.store.memory import InMemoryStore
from langchain_community.document_loaders import read_file


def embed(texts: list[str]) -> list[list[float]]:
    return [[1.0, 2.0] * len(texts)]

store = InMemoryStore(index={"embed": embed, "dims": 2})
namespace = ("project", "supervisor")

@tool
def get_state() -> dict:
    """Load the current project state from memory."""
    state = store.get(namespace, "project_state")
    return state or {}  # return empty dict if none exists

@tool
def set_state(state: dict) -> str:
    """Persist the project state."""
    store.put(namespace, "project_state", state)
    return "STATE_UPDATED"

UPLOAD_FOLDER = "/app/uploads"

@tool
def list_uploaded_files() -> list[str]:
    """Return list of uploaded files available for processing."""
    try:
        files = [
            os.path.join(UPLOAD_FOLDER, f)
            for f in os.listdir(UPLOAD_FOLDER)
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))
        ]
        return files
    except Exception as e:
        return [f"ERROR: {str(e)}"]

@tool
def load_document_to_memory(file_path: str) -> dict:
    """
    Load a document, store it in memory, and return its content.
    """
    try:
        docs = read_file(file_path)
        content = "\n".join(doc.page_content for doc in docs)
        file_name = os.path.basename(file_path)

        store.put(namespace, file_name, {"content": content})

        return {
            "status": "DOCUMENT_SAVED",
            "file_name": file_name,
            "content": content,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@tool
def get_document_from_memory(file_name: str) -> str:
    """
    Retrieve a previously stored document from memory.

    Args:
        file_name (str): Name of the document key (e.g., 'assignment.pdf').

    Returns:
        str: The stored document content, or an error message if not found.
    """
    try:
        item = store.get(namespace, file_name)
        if not item:
            return f"ERROR: Document '{file_name}' not found in memory."

        # expected structure: {"content": "..."}
        content = item.get("content", None)
        if not content:
            return f"ERROR: Document '{file_name}' exists but has no content."

        return content

    except Exception as e:
        return f"ERROR: Unable to retrieve document '{file_name}': {str(e)}"

@tool
def save_document_to_memory(file_name: str, content: str) -> str:
    """Store the document content inside persistent memory."""
    store.put(
        namespace,
        file_name,
        {"content": content}
    )
    return "DOCUMENT_SAVED"

@tool
def micro_action():
    """
    Generate outline or rubric feedback
    :return:
    """
    return None

@tool
def corrective_action():
    """
    Reassign tasks or update plan
    :return:
    """
    return None

