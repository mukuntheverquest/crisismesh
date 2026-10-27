print("state.py: Starting module load...")
from typing import Dict, Any, List, Optional, Literal, TypedDict
print("state.py: typing imported")
from datetime import datetime
print("state.py: datetime imported")
from uuid import UUID, uuid4
print("state.py: uuid imported")
from enum import Enum
print("state.py: enum imported")
from pydantic import BaseModel, Field
print("state.py: pydantic imported")

print("state.py: Defining enums...")
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

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    ESCALATED = "escalated"

print("state.py: Enums defined")
print("state.py: Module load complete")