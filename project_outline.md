1. One-liner pitch

“An AI project manager for uni group work that takes the brief + team skills, helps you converge on the best idea, then auto-plans and manages the work via GitHub.”

That hits:
	•	Pain point: chaotic group projects
	•	Differentiator: idea synthesis + task allocation + GitHub integration
	•	Agentic behaviour: it acts (creates issues, tracks progress, re-plans), not just chats

⸻

2. User flow (end-to-end)

Imagine what a demo looks like:
	1.	Create project
	•	Upload/ paste assignment brief + marking rubric + deadline.
	•	Add team members (names, skills, availability, maybe preferred roles).
	2.	Idea discussion
	•	Each member types in their idea(s) + constraints (e.g. “needs to use React”, “must include ML model”).
	•	The agent:
	•	Summarises current ideas
	•	Evaluates pros/cons vs the brief & rubric
	•	Suggests combined or alternative ideas (“What if we merge Alice’s API idea with Bob’s dashboard idea?”).
	3.	Converge on idea
	•	Team picks one (or the agent proposes a ranked list).
	•	Agent generates:
	•	A short project spec
	•	A rough architecture (tech stack, components, data flow)
	4.	Task breakdown + assignment
	•	Agent decomposes the project into tasks & milestones.
	•	Maps tasks to team members based on their skill profiles.
	•	Outputs a timeline (e.g. Kanban-style: “This week: X, next week: Y”).
	5.	GitHub integration
	•	Creates repo (or connects to existing one).
	•	Creates:
	•	Issues for each task
	•	Labels (frontend/backend/docs/priority)
	•	Milestones based on deadlines
	•	Optionally: creates branch naming conventions and PR templates.
	6.	Ongoing agentic support
	•	Periodically checks GitHub:
	•	Closed issues, open PRs, stale branches.
	•	Updates progress dashboard.
	•	Suggests adjustments:
	•	“Ali is overloaded; reassign testing task to Maya.”
	•	“Deadline in 3 days, docs aren’t started – here’s an outline and some draft text.”

For the hackathon, you don’t need all of this – just enough to show the autonomy loop.

⸻

3. Agent design: who does what?

You can frame it as a team of agents working together:
	1.	🧠 Brief & Rubric Analyst
	•	Input: assignment text, marking scheme, deadline.
	•	Output:
	•	Key constraints (e.g. “must use database”, “10-minute presentation”)
	•	Grading criteria with weights
	•	Used later to evaluate ideas and ensure the plan maximises marks.
	2.	💡 Idea Synthesiser & Evaluator
	•	Input: list of team ideas + brief analysis.
	•	Output:
	•	Grouped & summarised ideas
	•	For each idea: feasibility, mark-optimisation score, timeline roughness
	•	Suggests improved/combined ideas
	•	This is where you show off multi-perspective reasoning.
	3.	🛠️ Task Decomposer
	•	Input: chosen idea + basic tech stack.
	•	Output:
	•	Task graph: tasks, dependencies, estimated effort, suggested order.
	•	Categories: frontend / backend / infra / docs / testing.
	4.	🧩 Skill Matcher & Allocator
	•	Input: tasks + team skills/preferences.
	•	Output:
	•	Assignment of tasks to members
	•	Justification: “Gives backend tasks to X because of Node experience”
	•	You can store skills like: { name, skills: [ 'python', 'react', 'design' ], hours_per_week }.
	5.	🐙 GitHub Agent
	•	Input: tasks, milestones, repo info, GitHub token.
	•	Output (actions):
	•	Create repo (optional)
	•	Create labels/milestones
	•	Create issues (with descriptions & checklists)
	•	Later: Reads repo state (issues/PRs) to update progress.
	6.	📈 Progress & Re-planning Agent (stretch goal)
	•	Periodically:
	•	Checks which issues are still open and who’s behind schedule.
	•	Suggests reassignments or scope cuts.
	•	Makes it feel truly agentic, not just one-shot.

You might implement them as separate “modes” of one backend service, or literally separate agents orchestrated by a simple planner.

⸻

4. MVP scope for hackathon (be ruthless)

To ship something solid in hackathon time, I’d aim for:

Must-have:
	•	Upload/paste brief + rubric.
	•	Add 3–5 team members with skills.
	•	Enter 2–4 initial project ideas.
	•	Agent:
	•	Analyses brief.
	•	Scores and refines ideas.
	•	Produces a chosen project spec + task breakdown.
	•	Suggests task allocation per teammate.
	•	GitHub:
	•	Connect via personal access token.
	•	Create issues & milestones from the plan.

Nice-to-have (if time permits):
	•	Progress dashboard with GitHub sync.
	•	Re-planning suggestions when progress is slow.
	•	Real-time collaborative chat where the agent joins in.

Don’t overbuild UI; focus on the magic moment:

“We paste in a messy assignment brief + random ideas → system gives us a smart plan and pushes it into GitHub automatically.”

⸻

5. Technical architecture (concrete)

Here’s a simple stack that fits hackathon constraints:
	•	Frontend:
	•	React / Next.js
	•	Pages:
	•	Project setup (brief, rubric, deadline)
	•	Team setup (members + skills)
	•	Ideas board (where chat/ideas appear and agent responds)
	•	Plan view (tasks, assignments, “Push to GitHub” button)
	•	Backend:
	•	Node.js or Python (FastAPI / Express).
	•	Routes like:
	•	POST /analyze-brief
	•	POST /evaluate-ideas
	•	POST /plan-tasks
	•	POST /allocate-tasks
	•	POST /github/sync
	•	Agents / LLM logic:
	•	Orchestrated server-side.
	•	Each route calls the right “agent” prompt with relevant context.
	•	Add light memory: store everything in a DB record for “project”.
	•	Database:
	•	Supabase / Firebase / simple Postgres.
	•	Entities:
	•	Project { id, title, brief, rubric, deadline }
	•	TeamMember { id, projectId, name, skills[], hours }
	•	Idea { id, projectId, text, authorId }
	•	Task { id, projectId, title, description, assigneeId, status, githubIssueId }
	•	GitHub integration:
	•	Use GitHub REST API.
	•	User gives a PAT (personal access token) and repo name.
	•	Backend:
	•	POST /github/init → create labels, milestones.
	•	POST /github/create-issues → loop over tasks and create issues.

⸻

6. How to make it feel agentic, not just “LLM-powered”

Judges will be looking for autonomy and multi-step behaviour. You can highlight:
	1.	Planning loop
	•	It doesn’t just answer; it:
	•	extracts constraints from the brief,
	•	evaluates ideas against rubric,
	•	proposes a plan and task graph.
	2.	Acting in external tools
	•	It affects the real world through GitHub: creates issues, milestones, etc.
	3.	Feedback loop (even a minimal version)
	•	After creating issues, you can call GitHub again and show:
	•	“I see 3 tasks completed, here’s what’s left and who should focus on what next.”
	4.	Team-awareness
	•	The allocation step uses explicit skill profiles, not just generic text.
	•	Show a case:
	•	Change someone’s skills → re-run allocation → different assignments.

⸻

7. Concrete demo script (for the pitch)

You can structure your demo like this:
	1.	“Here’s a typical uni assignment brief.” (Paste it in)
	2.	“We add our team and some rough ideas.”
	3.	Click ‘Generate Plan’:
	•	System:
	•	Summarises brief.
	•	Scores ideas and picks/optimises one.
	•	Shows tasks + who’s doing what.
	4.	Click ‘Create GitHub Issues’:
	•	Show the repo with:
	•	Issues per task
	•	Milestones
	5.	(If you implement tracking) Show how closing an issue triggers a progress update in your app.

That tells a clean story from chaos → clarity → execution.