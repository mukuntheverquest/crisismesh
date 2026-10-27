import sys
sys.path.insert(0, 'C:/Users/venka/Gen AI Hackathon/CrisisMesh/backend')

print("Step 1: Basic imports...")
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field
print("Step 1 OK")

print("Step 2: Defining AgentType...")
class AgentType(str, Enum):
    PLANNER = "planner"
print("Step 2 OK")

print("Step 3: Defining TaskNode...")
class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: AgentType
print("Step 3 OK")

print("Step 4: Creating instance...")
t = TaskNode(agent_type=AgentType.PLANNER)
print("Step 4 OK:", t.task_id)

print("All tests passed!")