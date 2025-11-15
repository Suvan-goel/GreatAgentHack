# Project Specification: Agentic Multi-Agent System

This specification outlines all agents, tools, LLM calls, state requirements, and behaviours necessary to implement the full multi-agent project using LangChain, LangGraph, and `create_react_agent`.

---

# 1. System Overview

The system contains **8 autonomous agents**, each operating with:
- A persistent **goal**
- Access to specific **tools**
- Read/write access to shared **graph state**
- A **reactive loop** (ReAct reasoning)

Agents communicate implicitly using shared state, not direct messaging.

---

# 2. Shared State Schema

Global state objects passed through LangGraph:

```yaml
type: ProjectState
fields:
  project_files: list
  parsed_docs: dict
  missing_items: list
  project_metadata: dict
  deliverables: list
  raw_tasks: list
  refined_tasks: list
  task_graph: dict
  users: list
  user_cvs: dict
  user_profiles: dict
  skill_profiles: dict
  ai_rankings: dict
  final_rankings: dict
  assignment_plan: dict
  final_report: dict
```

Each agent reads what it needs and writes new fields.

---

# 3. AGENTS, TOOLS, AND REQUIRED BEHAVIOURS

## **Agent 1 — Project Intake Agent**
**Goal:** Ensure all required project documents are collected and validated.

### Tools Required
1. **UploadTool**
   - Accept file uploads
   - Store in local storage / S3
   - Return file path
2. **FileClassifierTool**
   - Classify each uploaded file: brief, marking criteria, rubric, etc.
   - LLM call: *text classification*
3. **ParseTool**
   - Convert PDF/DOCX to plain text
4. **MissingDetectorTool**
   - Input: list of files
   - Output: missing required components
   - LLM call: *extract required sections*
5. **MetadataExtractorTool**
   - Extract deadlines, deliverables, criteria
   - LLM call: *structured JSON extraction*

### Agent Logic
- If no files → ask user
- Detect missing items → request them
- Parse documents
- Extract preliminary metadata
- Write `ProjectRawBundle` to state

---

## **Agent 2 — Task Structuring Agent**
**Goal:** Produce complete, validated, dependency-aware `ProjectTaskGraph`.

### Tools Required
1. **DeliverableExtractorTool**
   - Read raw docs / metadata
   - Extract deliverables
   - LLM call: *list extraction*
2. **TaskDecomposerTool**
   - Input: deliverables
   - Output: raw tasks
   - LLM call: *decompose into tasks*
3. **TaskRefinerTool**
   - Convert raw tasks → atomic tasks
   - Extract skills, deadlines, difficulty
   - LLM call: *task refinement + tagging*
4. **DependencyInferTool**
   - Build dependency graph
   - LLM call: *infer before/after relationships*
5. **GraphValidatorTool**
   - Check missing fields, cycles
   - LLM call: *validation explanation*

### Agent Logic
- Infer deliverables if missing
- Generate raw tasks
- Refine tasks
- Infer dependencies
- Validate task graph

---

## **Agent 3 — User Onboarding Agent**
**Goal:** Collect all users, CVs, preferences, and constraints.

### Tools Required
1. **UserRegistryTool**
   - Add/remove/update users
2. **CVUploadTool**
   - Accept CV uploads
3. **PreferenceFormTool**
   - Collect availability, constraints, preferences

### LLM Usage
Minimal (mostly tool-based).

### Agent Logic
- Ensure all users registered
- Collect CVs
- Collect preferences

---

## **Agent 4 — CV Skill Profiling Agent**
**Goal:** Build structured skill profiles from raw CVs + user forms.

### Tools Required
1. **CVParserTool**
   - Extract education, tools, experiences
   - LLM call: *structured extraction*
2. **SkillExtractorTool**
   - Convert CV text → normalized skill list
   - LLM call: *skill tagging*
3. **EmbeddingTool**
   - Embed user skills for similarity scoring

### Agent Logic
- Parse CVs
- Extract skills
- Compute embeddings
- Validate profiles

---

## **Agent 5 — AI Task Ranking Agent**
**Goal:** Rank tasks for each user based on their skill profile.

### Tools Required
1. **SimilarityScorerTool**
   - Compare task requirements vs user embeddings
2. **TaskRankingTool**
   - Combine similarity + difficulty + deadlines
3. **ExplanationGeneratorTool**
   - Explain ranking rationale
   - LLM call: *reasoning + justification*

### Agent Logic
- Score fit between each task and user
- Generate ranked list
- Produce explanations

---

## **Agent 6 — User Ranking Adjustment Agent**
**Goal:** Finalise user preferences through reordering and constraints.

### Tools Required
1. **RankingUIUpdateTool**
   - Accept user drag-and-drop updates
2. **ConstraintValidationTool**
   - Validate user constraints
   - LLM call: *detect conflicts*

### Agent Logic
- Present ranking
- Accept adjustments
- Validate
- Save final ranking

---

## **Agent 7 — Task Allocation Agent**
**Goal:** Optimise tasks across users fairly.

### Tools Required
1. **OptimisationMatrixBuilderTool**
   - Build assignment matrix
2. **HungarianSolverTool**
   - Run optimal assignment
3. **FairnessCheckTool**
   - Analyse workload balance
4. **ReoptimiseTool (optional)**
   - If fairness fails, rerun with penalties

### LLM Usage
- Only in explanation or conflict resolution.

### Agent Logic
- Build matrix
- Solve assignment
- Validate fairness
- Produce plan

---

## **Agent 8 — Transparency & Reporting Agent**
**Goal:** Produce a transparent explanation of final assignment.

### Tools Required
1. **ReportGeneratorTool**
   - Build PDF/HTML/Markdown report
2. **AssignmentExplanationTool**
   - Explain fairness, skill match, preferences
   - LLM call: *structured explanation*
3. **CalendarExporterTool**
   - Export deadlines to user calendar

### Agent Logic
- Retrieve assignment
- Generate rationale
- Produce final report

---

# 4. LLM CALL SPECIFICATIONS

### **Extraction prompts (Agents 1–2)**
- Summarise
- Extract fields
- Produce JSON

### **Skill profiling prompts (Agent 4)**
- Convert CV to structured entities
- Normalise skills

### **Ranking prompts (Agent 5)**
- Score task-user fit
- Provide justifications

### **Validation prompts (Agents 2, 6, 7)**
- Detect missing fields
- Detect inconsistencies

### **Reporting prompts (Agent 8)**
- Explain reasoning step-by-step
- Highlight fairness

---

# 5. SYSTEM INPUT & OUTPUT FLOW

### Input
- Assignment documents
- Marking criteria
- User list
- CVs
- User preferences

### Output
- Structured task graph
- User skill profiles
- AI task rankings
- Final task assignment
- Transparent report

---

# 6. IMPLEMENTATION REQUIREMENTS

### Frontend
- File uploads
- Task drag-and-drop re-ranking
- Dashboard showing assignment

### Backend
- LangGraph orchestrator
- FastAPI or Next.js API endpoints

### Database
- Postgres or SQLite for persistent state
- ChromaDB/FAISS for embeddings

### Cloud (optional)
- S3 bucket for file storage
- Railway/Render for deployment

---

# 7. COMPLETION CRITERIA

The system is considered complete when:
1. All 8 agents autonomous, reactive, and goal-driven
2. Task graph generated correctly from any UCL assignment
3. Each user receives personalised task rankings
4. System computes an optimal and fair assignment
5. Report is transparent, auditable, and exportable

---

# End of spec.md