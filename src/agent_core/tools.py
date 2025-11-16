import os
from langchain_core.tools import tool
from langgraph.store.memory import InMemoryStore
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredFileLoader,
    JSONLoader,
    CSVLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_huggingface import HuggingFaceEmbeddings

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "src/uploads"))

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def embed(texts: list[str]) -> list[list[float]]:
    return emb.embed_documents(texts)

store = InMemoryStore(index={"embed": embed, "dims": 2})
namespace = ("project", "supervisor")

@tool
def get_state() -> dict:
    """Load the current project state from memory."""
    state = store.get(namespace, "project_state")
    return state or {}

@tool
def set_state(state: dict) -> str:
    """Persist the project state."""
    store.put(namespace, "project_state", state)
    return "STATE_UPDATED"

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

def get_loader_for_file(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return PyPDFLoader(file_path)

    if ext in [".txt", ".md"]:
        return TextLoader(file_path)

    if ext in [".doc", ".docx"]:
        return Docx2txtLoader(file_path)

    if ext == ".json":
        return JSONLoader(file_path)

    if ext == ".csv":
        return CSVLoader(file_path)

    return UnstructuredFileLoader(file_path)


@tool
def load_document_to_memory(file_path: str) -> dict:
    """
    Load a document (PDF, DOCX, TXT...), store it in memory, and return its content.
    Prevents double-imports.
    """
    try:
        file_name = os.path.basename(file_path)

        existing_item = store.get(namespace, file_name)

        if existing_item is not None:
            stored_value = existing_item.value
            return {
                "status": "ALREADY_EXISTS",
                "file_name": file_name,
                "content": stored_value.get("content", "")
            }

        loader = get_loader_for_file(file_path)
        docs = loader.load()

        content = "\n".join(d.page_content for d in docs)

        store.put(namespace, file_name, {
            "content": content,
            "metadata": {
                "file_path": file_path,
                "file_name": file_name,
                "length": len(content),
            }
        })

        return {
            "status": "DOCUMENT_SAVED",
            "file_name": file_name,
            "content": content,
        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@tool
def get_document_from_memory(file_name: str) -> dict:
    """
    Retrieve a previously stored document from memory.
    Returns content + metadata in a stable format.
    """
    try:
        item = store.get(namespace, file_name)

        if item is None:
            return {
                "status": "NOT_FOUND",
                "file_name": file_name,
                "content": ""
            }

        # item.value is the actual stored dictionary
        data = item.value

        return {
            "status": "OK",
            "file_name": file_name,
            "content": data.get("content", ""),
            "metadata": data.get("metadata", {})
        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@tool
def save_document_to_memory(file_name: str, content: str) -> str:
    """
    Store document content manually (used if agent generates a micro-action).
    """
    store.put(namespace, file_name, {"content": content})
    return "DOCUMENT_SAVED"

# @tool
# def ask_user(message: str):
#     """
#     prompts the user to ask for a specific input
#     args:
#         message (str): message to prompt the user
#     return:
#         user_input (str): user input
#     """
#     return input(message)

@tool
def ask_user(message: str) -> dict:
    """
    Request input from the user through the UI (FastAPI).
    This does NOT block.

    Stores the prompt in memory and returns a "waiting" status.
    """
    # Save the pending question
    store.put(
        namespace,
        "pending_prompt",
        {"message": message, "answered": False, "response": None}
    )

    return {
        "status": "WAITING_FOR_USER",
        "message_to_user": message
    }

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

