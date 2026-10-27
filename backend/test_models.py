print("Starting import test...")
import sys
sys.path.insert(0, 'C:/Users/venka/Gen AI Hackathon/CrisisMesh/backend')

print("Step 1: Importing basic modules...")
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field
print("Step 1: Basic imports OK")

print("Step 2: Defining AgentType enum...")
class AgentType(str, Enum):
    PLANNER = "planner"
    FORMAT_DETECTOR = "format_detector"
    INGESTION_EXECUTOR = "ingestion_executor"
    EVALUATOR = "evaluator"
    RISK_DISPATCH = "risk_dispatch"
    MARKOVIAN_ROUTER = "markovian_router"
    WORLD_MODEL_SIMULATOR = "world_model_simulator"
    HMEM_STORE = "hmem_store"
    REPORTER = "reporter"
print("Step 2: AgentType OK")

print("Step 3: Defining TaskNode...")
class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 3,
        "backoff": "exponential",
        "fallback_agent": None
    })
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
print("Step 3: TaskNode OK")

print("Step 4: Creating instance...")
t = TaskNode(agent_type="planner")
print("Step 4: Instance created:", t.task_id)

print("All tests passed!")