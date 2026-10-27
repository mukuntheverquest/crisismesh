"""
CrisisMesh Base Agent Classes - Open Agent Hackathon 2026
Foundation for all agents with Meterless tracing integration
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from datetime import datetime
from uuid import uuid4

from app.config import settings
from app.agents.state import AgentState, AgentType, TaskStatus


# ============================================
# Meterless Tracing Decorators
# ============================================

def trace_agent(agent_name: str, operation: str = "execute"):
    """Decorator to trace agent execution with Meterless"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = str(uuid4())
            
            # Log start
            print(f"[METERLESS] 🟢 Agent:{agent_name} | Op:{operation} | Trace:{trace_id} | START")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                print(f"[METERLESS] ✅ Agent:{agent_name} | Op:{operation} | Trace:{trace_id} | "
                      f"DURATION:{duration:.3f}s | STATUS:success")
                
                # Record metric
                _record_metric(f"agent.{agent_name}.duration_seconds", duration)
                _record_metric(f"agent.{agent_name}.success", 1)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"[METERLESS] ❌ Agent:{agent_name} | Op:{operation} | Trace:{trace_id} | "
                      f"DURATION:{duration:.3f}s | STATUS:error | ERROR:{str(e)}")
                
                _record_metric(f"agent.{agent_name}.duration_seconds", duration)
                _record_metric(f"agent.{agent_name}.errors", 1)
                raise
                
        return wrapper
    return decorator


def trace_tool_call(agent_name: str, tool_name: str):
    """Decorator to trace tool calls within agents"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = str(uuid4())
            
            print(f"[METERLESS] 🔧 Tool:{tool_name} | Agent:{agent_name} | Trace:{trace_id} | START")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                print(f"[METERLESS] ✅ Tool:{tool_name} | Agent:{agent_name} | Trace:{trace_id} | "
                      f"DURATION:{duration:.3f}s | STATUS:success")
                
                _record_metric(f"tool.{tool_name}.duration_seconds", duration)
                _record_metric(f"tool.{tool_name}.success", 1)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"[METERLESS] ❌ Tool:{tool_name} | Agent:{agent_name} | Trace:{trace_id} | "
                      f"DURATION:{duration:.3f}s | STATUS:error | ERROR:{str(e)}")
                
                _record_metric(f"tool.{tool_name}.duration_seconds", duration)
                _record_metric(f"tool.{tool_name}.errors", 1)
                raise
                
        return wrapper
    return decorator


def _record_metric(name: str, value: float, labels: Dict[str, str] = None):
    """Record a metric to Meterless (placeholder for actual SDK call)"""
    # In production, this would call the Meterless SDK
    # meterless_client.record_metric(name, value, labels)
    pass


# ============================================
# Base Agent Class
# ============================================

class BaseAgent(ABC):
    """Abstract base class for all CrisisMesh agents"""
    
    def __init__(self, agent_type: AgentType):
        self._agent_type = agent_type
        self.name = agent_type.value
        self.max_retries = settings.AGENT_MAX_RETRIES
        self.timeout = settings.AGENT_TIMEOUT_SECONDS
    
    @property
    def agent_type(self) -> AgentType:
        """Return the agent type"""
        return self._agent_type
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute the agent's primary logic"""
        pass
    
    async def validate(self, state: AgentState) -> bool:
        """Validate agent output (optional override)"""
        return True
    
    async def critique(self, state: AgentState) -> Dict[str, Any]:
        """Provide critique for planner feedback (optional override)"""
        return {"critique": "No critique available", "suggestions": []}
    
    def _update_state_trace(self, state: AgentState, output: Dict[str, Any]) -> AgentState:
        """Update state with agent output and trace info"""
        state[f"{self.name}_output"] = output
        state["provenance"]["agent_trace"][self.name] = {
            "executed_at": datetime.utcnow().isoformat(),
            "output_summary": self._summarize_output(output)
        }
        state["updated_at"] = datetime.utcnow().isoformat()
        return state
    
    def _summarize_output(self, output: Dict[str, Any]) -> str:
        """Create a brief summary of agent output"""
        if not output:
            return "No output"
        keys = list(output.keys())[:5]
        return f"Keys: {', '.join(keys)}"
    
    def _add_error(self, state: AgentState, error: str, fatal: bool = False) -> AgentState:
        """Add error to state"""
        state["errors"].append({
            "agent": self.name,
            "error": error,
            "fatal": fatal,
            "timestamp": datetime.utcnow().isoformat()
        })
        if fatal:
            state["should_continue"] = False
        return state


# ============================================
# Agent Factory
# ============================================

class AgentFactory:
    """Factory for creating and managing agent instances"""
    
    _agents: Dict[AgentType, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent_type: AgentType, agent: BaseAgent):
        cls._agents[agent_type] = agent
    
    @classmethod
    def get(cls, agent_type: AgentType) -> Optional[BaseAgent]:
        return cls._agents.get(agent_type)
    
    @classmethod
    def get_all(cls) -> Dict[AgentType, BaseAgent]:
        return cls._agents.copy()
    
    @classmethod
    async def execute_agent(cls, agent_type: AgentType, state: AgentState) -> AgentState:
        """Execute a specific agent by type"""
        agent = cls.get(agent_type)
        if not agent:
            raise ValueError(f"Agent {agent_type} not registered")
        return await agent.execute(state)


# ============================================
# Utility Functions
# ============================================

async def run_with_timeout(coro, timeout: int):
    """Run coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """Retry decorator with exponential backoff"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed: {e}. "
                          f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"[RETRY] All {max_retries} retries exhausted")
        raise last_exception
    return wrapper


__all__ = [
    "BaseAgent",
    "AgentFactory",
    "trace_agent",
    "trace_tool_call",
    "run_with_timeout",
    "retry_with_backoff"
]