from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    name: str
    description: str
    deadline: str
    status: str
    assigned_to: str

class UserTasks(BaseModel):
    user: str
    expertise: str
    assigned_tasks: List[Task]

class ProjectOutputModel(BaseModel):
    project_title: str
    deadline: str
    team_summary: List[UserTasks]
