"""
CrisisMesh Markovian Router Agent - Open Agent Hackathon 2026
Implements Meterless Markovian state routing for autonomous alert dispatch
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import random

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, AlertStatus
from app.config import settings


class MarkovState(str, Enum):
    """Markov states for alert routing"""
    MONITORING = "monitoring"
    TRIGGER_DETECTED = "trigger_detected"
    SUPERVISOR_NOTIFIED = "supervisor_notified"
    SUPERVISOR_ACKNOWLEDGED = "supervisor_acknowledged"
    DEADMAN_SWITCH_ARMED = "deadman_switch_armed"
    DEADMAN_SWITCH_TRIGGERED = "deadman_switch_triggered"
    ALERT_DISPATCHED = "alert_dispatched"
    ACKNOWLEDGED = "acknowledged"
    EXPIRED = "expired"


class MarkovianRouterAgent(BaseAgent):
    """Markovian state router for autonomous alert dispatch with dead-man's switch"""
    
    def __init__(self):
        super().__init__(AgentType.MARKOVIAN_ROUTER)
        self.transition_matrix = self._build_transition_matrix()
        self.current_state = MarkovState.MONITORING
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.MARKOVIAN_ROUTER
    
    def _build_transition_matrix(self) -> Dict[MarkovState, Dict[MarkovState, float]]:
        """Build Markov transition probability matrix"""
        return {
            MarkovState.MONITORING: {
                MarkovState.TRIGGER_DETECTED: 0.15,  # Multi-source trigger co-occurrence
                MarkovState.MONITORING: 0.85
            },
            MarkovState.TRIGGER_DETECTED: {
                MarkovState.SUPERVISOR_NOTIFIED: 0.95,  # Always notify supervisor first
                MarkovState.DEADMAN_SWITCH_ARMED: 0.05  # Rare direct arm
            },
            MarkovState.SUPERVISOR_NOTIFIED: {
                MarkovState.SUPERVISOR_ACKNOWLEDGED: 0.70,  # 70% respond in time
                MarkovState.DEADMAN_SWITCH_ARMED: 0.30  # 30% don't respond
            },
            MarkovState.SUPERVISOR_ACKNOWLEDGED: {
                MarkovState.ALERT_DISPATCHED: 0.95,  # Supervisor dispatches
                MarkovState.DEADMAN_SWITCH_ARMED: 0.05  # Supervisor fails to dispatch
            },
            MarkovState.DEADMAN_SWITCH_ARMED: {
                MarkovState.DEADMAN_SWITCH_TRIGGERED: 1.0  # Deterministic after timeout
            },
            MarkovState.DEADMAN_SWITCH_TRIGGERED: {
                MarkovState.ALERT_DISPATCHED: 1.0  # Auto-dispatch
            },
            MarkovState.ALERT_DISPATCHED: {
                MarkovState.ACKNOWLEDGED: 0.80,
                MarkovState.EXPIRED: 0.20
            },
            MarkovState.ACKNOWLEDGED: {
                MarkovState.MONITORING: 1.0
            },
            MarkovState.EXPIRED: {
                MarkovState.MONITORING: 1.0
            }
        }
    
    @trace_agent("markovian_router", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Execute Markovian routing for alert dispatch"""
        
        task_graph = state.get("task_graph")
        current_task_id = state.get("current_task_id")
        
        if not task_graph or not current_task_id:
            current_task_id = self._find_next_markovian_task(task_graph)
            state["current_task_id"] = current_task_id
        
        if not current_task_id:
            state["next_agent"] = AgentType.RISK_DISPATCH
            return state
        
        task = task_graph.nodes.get(current_task_id)
        if not task:
            state["next_agent"] = AgentType.RISK_DISPATCH
            return state
        
        task_input = task.input_data
        task_type = task_input.get("task", "")
        
        result = None
        try:
            if task_type == "deadman_switch_alert":
                result = await self._run_deadman_switch(state, task_input)
            elif task_type == "precautionary_override":
                result = await self._run_precautionary_override(state, task_input)
            elif task_type == "immediate_alert_dispatch":
                result = await self._run_immediate_dispatch(state, task_input)
            elif task_type == "offline_first_execution":
                result = await self._run_offline_execution(state, task_input)
            elif task_type == "state_transition":
                result = await self._run_state_transition(state, task_input)
            else:
                result = {"status": "unknown_task", "task": task_type}
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.attempts += 1
            state = self._add_error(state, f"Markovian router task {task_type} failed: {e}")
        
        state["markovian_router_output"] = result
        state["next_agent"] = AgentType.RISK_DISPATCH
        state = self._update_state_trace(state, result or {})
        
        return state
    
    def _find_next_markovian_task(self, task_graph: Optional[Any]) -> Optional[str]:
        """Find next pending markovian router task"""
        if not task_graph:
            return None
        
        for task_id, task in task_graph.nodes.items():
            if (task.agent_type == AgentType.MARKOVIAN_ROUTER and 
                task.status == "pending"):
                deps_met = all(
                    task_graph.nodes[dep_id].status == "completed"
                    for dep_id in task.dependencies
                    if dep_id in task_graph.nodes
                )
                if deps_met:
                    return task_id
        return None
    
    @trace_tool_call("markovian_router", "deadman_switch")
    async def _run_deadman_switch(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Execute dead-man's switch logic (Failure #1)"""
        
        timeout_seconds = task_input.get("timeout_seconds", settings.ALERT_DEADMAN_SWITCH_SECONDS)
        bypass_supervisor = task_input.get("bypass_supervisor", True)
        
        # Check multi-source trigger co-occurrence
        trigger_sources = self._check_trigger_cooccurrence(state)
        
        if not trigger_sources:
            return {
                "task": "deadman_switch_alert",
                "triggered": False,
                "reason": "Insufficient trigger co-occurrence",
                "sources_checked": ["NWS/DHM Warning", "River Gauge/SAR Spike", "Field Responder Call"],
                "sources_active": 0
            }
        
        # Simulate Markov state progression
        state_sequence = [
            MarkovState.MONITORING,
            MarkovState.TRIGGER_DETECTED,
            MarkovState.SUPERVISOR_NOTIFIED
        ]
        
        # Check if supervisor acknowledges within timeout
        supervisor_acknowledged = await self._simulate_supervisor_response(timeout_seconds)
        
        if supervisor_acknowledged:
            state_sequence.append(MarkovState.SUPERVISOR_ACKNOWLEDGED)
            state_sequence.append(MarkovState.ALERT_DISPATCHED)
            deadman_triggered = False
        else:
            state_sequence.append(MarkovState.DEADMAN_SWITCH_ARMED)
            state_sequence.append(MarkovState.DEADMAN_SWITCH_TRIGGERED)
            state_sequence.append(MarkovState.ALERT_DISPATCHED)
            deadman_triggered = True
        
        return {
            "task": "deadman_switch_alert",
            "triggered": True,
            "deadman_switch_triggered": deadman_triggered,
            "trigger_sources": trigger_sources,
            "state_sequence": [s.value for s in state_sequence],
            "supervisor_acknowledged": supervisor_acknowledged,
            "timeout_seconds": timeout_seconds,
            "bypass_supervisor": bypass_supervisor,
            "transition_probabilities": self._get_transition_probs(state_sequence),
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    def _check_trigger_cooccurrence(self, state: AgentState) -> List[str]:
        """Check for multi-source trigger co-occurrence"""
        active_sources = []
        
        # Check NWS/DHM Warning
        official_alerts = state.get("official_alerts", [])
        for alert in official_alerts:
            if alert.get("severity") in ["severe", "extreme", "emergency"]:
                active_sources.append("NWS/DHM Warning")
                break
        
        # Check River Gauge/SAR Spike
        sensor_readings = state.get("sensor_readings", [])
        for reading in sensor_readings:
            if reading.sensor_type == "river_gauge" and reading.value > 10:  # Mock threshold
                active_sources.append("River Gauge/SAR Spike")
                break
        
        # Check Field Responder Call
        social_media = state.get("social_media_posts", [])
        for post in social_media:
            if any(kw in post.content.lower() for kw in ["emergency", "help", "trapped", "flood"]):
                active_sources.append("Field Responder Call")
                break
        
        return active_sources
    
    async def _simulate_supervisor_response(self, timeout_seconds: int) -> bool:
        """Simulate supervisor response (in production: actual notification system)"""
        # Mock: 30% chance supervisor doesn't respond in time (Failure #1 statistic)
        # In production: integrate with actual supervisor notification system
        import asyncio
        await asyncio.sleep(0.01)  # Simulate check
        return random.random() > 0.3
    
    def _get_transition_probs(self, state_sequence: List[MarkovState]) -> Dict[str, float]:
        """Get transition probabilities for the observed sequence"""
        probs = {}
        for i in range(len(state_sequence) - 1):
            from_state = state_sequence[i]
            to_state = state_sequence[i + 1]
            prob = self.transition_matrix.get(from_state, {}).get(to_state, 0.0)
            probs[f"{from_state.value} -> {to_state.value}"] = prob
        return probs
    
    @trace_tool_call("markovian_router", "precautionary_override")
    async def _run_precautionary_override(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Execute precautionary override for contradictory messages (Failure #6)"""
        
        # Check for contradictory official messages
        format_output = state.get("format_detector_output", {})
        contradictory_alerts = [
            a for a in format_output.get("official_alerts", [])
            if a.get("is_contradictory", False)
        ]
        
        if not contradictory_alerts:
            return {
                "task": "precautionary_override",
                "override_activated": False,
                "reason": "No contradictory alerts detected"
            }
        
        # Force transition to override state
        override_actions = []
        for alert in contradictory_alerts:
            if "curfew" in alert.get("event", "").lower() and "flood" in str(state.get("context", {})).lower():
                override_actions.append("BLOCKED curfew order in flood inundation zone")
            if "shelter-in-place" in alert.get("event", "").lower() and "dam" in str(state.get("context", {})).lower():
                override_actions.append("BLOCKED shelter-in-place in dam breach zone")
            if "all-clear" in alert.get("event", "").lower() and "emergency" in str(state.get("context", {})).lower():
                override_actions.append("BLOCKED all-clear during active emergency")
        
        return {
            "task": "precautionary_override",
            "override_activated": True,
            "contradictory_alerts": len(contradictory_alerts),
            "actions": override_actions,
            "forced_state": MarkovState.DEADMAN_SWITCH_TRIGGERED.value,
            "authority": "Pre-authorized SOP / Meterless Markovian Router",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("markovian_router", "immediate_alert_dispatch")
    async def _run_immediate_dispatch(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Immediate alert dispatch bypassing normal approval (Failure #4)"""
        
        bypass_approval = task_input.get("bypass_normal_approval", True)
        
        return {
            "task": "immediate_alert_dispatch",
            "bypass_approval": bypass_approval,
            "dispatch_method": "Markovian auto-transition",
            "state_transition": "TRIGGER_DETECTED -> DEADMAN_SWITCH_TRIGGERED -> ALERT_DISPATCHED",
            "time_to_dispatch_seconds": 5,  # Near-instantaneous
            "approvals_bypassed": ["supervisor_signoff", "jurisdictional_review"],
            "legal_basis": "Pre-authorized emergency powers / Markovian deterministic routing",
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("markovian_router", "offline_first_execution")
    async def _run_offline_execution(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Execute in offline mode (Failure #8)"""
        
        sample_mode = task_input.get("sample_mode", settings.SAMPLE_MODE)
        
        return {
            "task": "offline_first_execution",
            "sample_mode": sample_mode,
            "offline_mode_executed": True,
            "local_models_used": [
                "sentence-transformers/all-MiniLM-L6-v2",
                "llama3.1:8b (via Ollama)",
                "filetype detection"
            ],
            "external_apis_bypassed": [
                "Zetaris (using local SQLite)",
                "Meterless (local logging)",
                "NWS/USGS (using cached data)"
            ],
            "fallback_communications": ["VHF Radio", "Siren System", "Community Focal Points"],
            "executed_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("markovian_router", "state_transition")
    async def _run_state_transition(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Execute explicit state transition"""
        
        from_state = task_input.get("from_state", self.current_state.value)
        to_state = task_input.get("to_state", "")
        
        if not to_state:
            # Auto-determine next state
            current = MarkovState(from_state)
            next_states = self.transition_matrix.get(current, {})
            if next_states:
                to_state = max(next_states, key=next_states.get).value
            else:
                to_state = MarkovState.MONITORING.value
        
        prob = self.transition_matrix.get(MarkovState(from_state), {}).get(MarkovState(to_state), 0.0)
        
        self.current_state = MarkovState(to_state)
        
        return {
            "task": "state_transition",
            "from_state": from_state,
            "to_state": to_state,
            "transition_probability": prob,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.MARKOVIAN_ROUTER, MarkovianRouterAgent())