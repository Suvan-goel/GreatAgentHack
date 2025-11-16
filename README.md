# GroupSync – Group Project Wrangler & Tension Radar

GroupSync is an **agentic copilot for student group projects**. It:

- Reads a project brief
- Breaks it into tasks
- Assigns work to team members
- Builds a simple schedule
- Collects weekly check-ins
- Runs a **Tension Radar** to detect overload, disengagement, and conflict
- Generates a weekly **Supervisor Report** with concrete suggestions and a neutral message you can paste into the group chat

This MVP is designed for a **single project** in memory, with no database.

---

## 1. High-Level Architecture

The system has four main layers:

1. **Frontend (React + TypeScript)**  
   - UI for project setup, plan overview, check-ins, and tension dashboard.

2. **API Layer (FastAPI)**  
   - HTTP endpoints that accept user input and return state snapshots.
   - Orchestrates calls into agent logic and the in-memory state manager.

3. **Agent & Tools Layer (Python)**  
   - Agents:
     - Scope Agent
     - Role Matching Agent
     - Plan & Deadline Agent
     - Check-In Agent
     - Tension Radar Agent
     - Supervisor Agent
   - Tools:
     - PDF to text
     - Simple scheduler
     - Check-in feature extraction

4. **In-Memory State Manager**  
   - A single `project_state` object in Python that stores:
     - Project metadata
     - Team info
     - Tasks and plan
     - Check-ins
     - Risk snapshots
     - Simple run logs

Everything is built in a **bottom-up** way: utilities and state first, agents on top, then APIs, then UI.

---

## 2. Tech Stack

### Backend

- **Language:** Python
- **Framework:** FastAPI
- **Agent framework:** LangGraph or LangChain (for multi-agent workflows)
- **LLM provider:** OpenAI models (e.g. GPT-4.* family)
- **PDF parsing:** `PyPDF2` or `pdfplumber`
- **State:** Single `project_state` dictionary in memory

### Frontend

- **Language:** TypeScript
- **Framework:** React
- **Bundler:** Vite
- **Styling:** Tailwind CSS
- **Charts / visuals:** Recharts or lightweight custom components

---
