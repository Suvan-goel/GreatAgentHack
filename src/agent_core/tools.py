from langchain_core.tools import tool

@tool
def project_file_requirements() -> str:
    """
    Describe which files are required for the project planner agent.
    """
    return (
        "I need the following files:\n"
        "1) Assignment brief (PDF or DOCX).\n"
        "2) Deadline sheet (Excel/CSV with dates & deliverables).\n"
        "3) Optional: marking criteria.\n"
        "Please upload them via the FastAPI /chat-with-upload endpoint."
    )