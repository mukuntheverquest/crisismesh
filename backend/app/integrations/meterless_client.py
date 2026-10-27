"""
CrisisMesh Meterless Client - Open Agent Hackathon 2026
Agent observability with H-Mem, Markovian, and World Model engines
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import asyncio
import json
import uuid

from app.config import settings


@dataclass
class TraceEvent:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    agent_name: str
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None


@dataclass
class AgentTrace:
    trace_id: str
    job_id: str
    agent_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[TraceEvent] = field(default_factory=list)
    state_snapshots: List[Dict[str, Any]] = field(default_factory=list)


class MeterlessClient:
    """Client for Meterless Agent Observability Platform"""
    
    def __init__(self):
        self.base_url = settings.METERLESS_URL
        self.api_key = settings.METERLESS_API_KEY
        self.project_id = settings.METERLESS_PROJECT_ID
        self.connected = False
        self._traces: Dict[str, AgentTrace] = {}
        self._current_trace: Optional[AgentTrace] = None
    
    async def connect(self) -> bool:
        """Connect to Meterless"""
        if settings.SAMPLE_MODE:
            self.connected = True
            return True
        
        # In production: initialize Meterless SDK
        self.connected = True
        return True
    
    async def disconnect(self):
        """Disconnect from Meterless"""
        self.connected = False
    
    def start_trace(self, job_id: str, agent_type: str) -> str:
        """Start a new agent trace"""
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        
        trace = AgentTrace(
            trace_id=trace_id,
            job_id=job_id,
            agent_type=agent_type,
            start_time=datetime.utcnow()
        )
        
        self._traces[trace_id] = trace
        self._current_trace = trace
        
        return trace_id
    
    def end_trace(self, trace_id: str, status: str = "completed", error: Optional[str] = None):
        """End an agent trace"""
        if trace_id in self._traces:
            trace = self._traces[trace_id]
            trace.end_time = datetime.utcnow()
            # Update last event status
            if trace.events:
                trace.events[-1].status = status
                trace.events[-1].error = error
    
    def add_event(
        self,
        trace_id: str,
        agent_name: str,
        operation: str,
        input_data: Dict[str, Any] = None,
        output_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        parent_span_id: str = None
    ) -> str:
        """Add a trace event"""
        if trace_id not in self._traces:
            return ""
        
        trace = self._traces[trace_id]
        span_id = f"span_{uuid.uuid4().hex[:8]}"
        
        event = TraceEvent(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            agent_name=agent_name,
            operation=operation,
            start_time=datetime.utcnow(),
            input_data=input_data or {},
            output_data=output_data or {},
            metadata=metadata or {}
        )
        
        trace.events.append(event)
        return span_id
    
    def end_event(self, trace_id: str, span_id: str, output_data: Dict[str, Any] = None, error: str = None):
        """End a trace event"""
        if trace_id in self._traces:
            trace = self._traces[trace_id]
            for event in trace.events:
                if event.span_id == span_id:
                    event.end_time = datetime.utcnow()
                    event.duration_ms = (event.end_time - event.start_time).total_seconds() * 1000
                    if output_data:
                        event.output_data = output_data
                    if error:
                        event.status = "failed"
                        event.error = error
                    else:
                        event.status = "completed"
                    break
    
    def add_state_snapshot(self, trace_id: str, state: Dict[str, Any]):
        """Add state snapshot for H-Mem"""
        if trace_id in self._traces:
            self._traces[trace_id].state_snapshots.append({
                "timestamp": datetime.utcnow().isoformat(),
                "state": state
            })
    
    def get_trace(self, trace_id: str) -> Optional[AgentTrace]:
        """Get trace by ID"""
        return self._traces.get(trace_id)
    
    def get_job_traces(self, job_id: str) -> List[AgentTrace]:
        """Get all traces for a job"""
        return [t for t in self._traces.values() if t.job_id == job_id]
    
    async def send_trace(self, trace: AgentTrace) -> bool:
        """Send trace to Meterless platform"""
        if settings.SAMPLE_MODE:
            # Log to console/file in sample mode
            print(f"[Meterless] Trace {trace.trace_id} completed with {len(trace.events)} events")
            return True
        
        # In production: send to Meterless API
        return False
    
    # Markovian Router integration
    async def log_markovian_transition(
        self,
        trace_id: str,
        from_state: str,
        to_state: str,
        trigger: str,
        confidence: float,
        auto_bypass: bool = False
    ):
        """Log Markovian state transition"""
        self.add_event(
            trace_id=trace_id,
            agent_name="MarkovianRouter",
            operation="state_transition",
            input_data={"from_state": from_state, "trigger": trigger},
            output_data={"to_state": to_state, "confidence": confidence, "auto_bypass": auto_bypass},
            metadata={"markovian": True}
        )
    
    # World Model Simulator integration
    async def log_simulation(
        self,
        trace_id: str,
        simulation_type: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any]
    ):
        """Log world model simulation"""
        self.add_event(
            trace_id=trace_id,
            agent_name="WorldModelSimulator",
            operation="simulation",
            input_data=inputs,
            output_data=outputs,
            metadata={"simulation_type": simulation_type}
        )
    
    # H-Mem Store integration
    async def log_hmem_retrieval(
        self,
        trace_id: str,
        query: str,
        results: List[Dict[str, Any]],
        match_scores: List[float]
    ):
        """Log H-Mem retrieval"""
        self.add_event(
            trace_id=trace_id,
            agent_name="HMemStore",
            operation="retrieve",
            input_data={"query": query},
            output_data={"results": results, "match_scores": match_scores},
            metadata={"hmem": True}
        )
    
    async def log_hmem_store(
        self,
        trace_id: str,
        key: str,
        value: Any,
        metadata: Dict[str, Any]
    ):
        """Log H-Mem storage"""
        self.add_event(
            trace_id=trace_id,
            agent_name="HMemStore",
            operation="store",
            input_data={"key": key, "value": value},
            output_data={"stored": True},
            metadata={**metadata, "hmem": True}
        )


# ============================================
# Module-level wrapper functions for decorator use
# ============================================

_meterless_client: Optional[MeterlessClient] = None


async def get_meterless_client() -> MeterlessClient:
    """Get or create Meterless client"""
    global _meterless_client
    if _meterless_client is None:
        _meterless_client = MeterlessClient()
        await _meterless_client.connect()
    return _meterless_client


async def close_meterless_client():
    """Close Meterless client"""
    global _meterless_client
    if _meterless_client:
        await _meterless_client.disconnect()
        _meterless_client = None


# Wrapper functions for module-level use in decorators
def trace_agent(agent_name: str, operation: str = "execute"):
    """Decorator to trace agent execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get or create client
            client = await get_meterless_client()
            
            # Extract job_id from args/kwargs if available
            job_id = kwargs.get("job_id", f"job_{uuid.uuid4().hex[:8]}")
            
            # Start trace
            trace_id = client.start_trace(job_id, agent_name)
            
            # Add start event
            span_id = client.add_event(
                trace_id=trace_id,
                agent_name=agent_name,
                operation=operation,
                input_data={"args": str(args)[:200], "kwargs": str(kwargs)[:200]}
            )
            
            try:
                result = await func(*args, **kwargs)
                client.end_event(trace_id, span_id, output_data={"status": "success"})
                client.end_trace(trace_id, "completed")
                return result
            except Exception as e:
                client.end_event(trace_id, span_id, error=str(e))
                client.end_trace(trace_id, "failed", str(e))
                raise
        
        return wrapper
    return decorator


def trace_tool_call(tool_name: str, operation: str = "call"):
    """Decorator to trace tool calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            client = await get_meterless_client()
            
            # Generate trace_id for this tool call
            trace_id = f"tool_{uuid.uuid4().hex[:12]}"
            client.start_trace(trace_id, tool_name)
            
            span_id = client.add_event(
                trace_id=trace_id,
                agent_name=tool_name,
                operation=operation,
                input_data={"args": str(args)[:200], "kwargs": str(kwargs)[:200]}
            )
            
            try:
                result = await func(*args, **kwargs)
                client.end_event(trace_id, span_id, output_data={"result_type": type(result).__name__})
                client.end_trace(trace_id, "completed")
                return result
            except Exception as e:
                client.end_event(trace_id, span_id, error=str(e))
                client.end_trace(trace_id, "failed", str(e))
                raise
        
        return wrapper
    return decorator


__all__ = [
    "MeterlessClient",
    "TraceEvent",
    "AgentTrace",
    "get_meterless_client",
    "close_meterless_client",
    "trace_agent",
    "trace_tool_call"
]