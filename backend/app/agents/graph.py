"""
CrisisMesh LangGraph Orchestration - Open Agent Hackathon 2026
Wires agents into a state graph with dynamic routing, shared memory, and feedback loops
"""
from typing import Dict, Any, Literal, Callable, List, Optional
from langgraph.graph import StateGraph, END
import os
from pathlib import Path

from app.agents.state import AgentState, AgentType, TaskStatus
from app.config import settings

# Agent instances - lazy loaded
_agent_instances: Dict[AgentType, Any] = {}

def _get_agent(agent_type: AgentType):
    """Get or create agent instance (lazy loading)"""
    if agent_type not in _agent_instances:
        if agent_type == AgentType.PLANNER:
            from app.agents.planner import PlannerAgent
            _agent_instances[agent_type] = PlannerAgent()
        elif agent_type == AgentType.FORMAT_DETECTOR:
            from app.agents.domain_agents.format_detector import FormatDetectorAgent
            _agent_instances[agent_type] = FormatDetectorAgent()
        elif agent_type == AgentType.INGESTION_EXECUTOR:
            from app.agents.domain_agents.ingestion_executor import IngestionExecutorAgent
            _agent_instances[agent_type] = IngestionExecutorAgent()
        elif agent_type == AgentType.MARKOVIAN_ROUTER:
            from app.agents.domain_agents.markovian_router import MarkovianRouterAgent
            _agent_instances[agent_type] = MarkovianRouterAgent()
        elif agent_type == AgentType.WORLD_MODEL_SIMULATOR:
            from app.agents.domain_agents.world_model_simulator import WorldModelSimulatorAgent
            _agent_instances[agent_type] = WorldModelSimulatorAgent()
        elif agent_type == AgentType.HMEM_STORE:
            from app.agents.domain_agents.hmem_store import HMemStoreAgent
            _agent_instances[agent_type] = HMemStoreAgent()
        elif agent_type == AgentType.EVALUATOR:
            from app.agents.evaluator import EvaluatorAgent
            _agent_instances[agent_type] = EvaluatorAgent()
        elif agent_type == AgentType.RISK_DISPATCH:
            from app.agents.risk_agent import RiskDispatchAgent
            _agent_instances[agent_type] = RiskDispatchAgent()
        elif agent_type == AgentType.REPORTER:
            from app.agents.reporter import ReporterAgent
            _agent_instances[agent_type] = ReporterAgent()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    return _agent_instances[agent_type]

# ============================================
# Agent Node Functions (lazy loading)
# ============================================

async def planner_node(state: AgentState) -> AgentState:
    """Planner agent node"""
    agent = _get_agent(AgentType.PLANNER)
    return await agent.execute(state)

async def format_detector_node(state: AgentState) -> AgentState:
    """Format detector agent node"""
    agent = _get_agent(AgentType.FORMAT_DETECTOR)
    return await agent.execute(state)

async def ingestion_executor_node(state: AgentState) -> AgentState:
    """Ingestion executor agent node"""
    agent = _get_agent(AgentType.INGESTION_EXECUTOR)
    return await agent.execute(state)

async def markovian_router_node(state: AgentState) -> AgentState:
    """Markovian router agent node"""
    agent = _get_agent(AgentType.MARKOVIAN_ROUTER)
    return await agent.execute(state)

async def world_model_simulator_node(state: AgentState) -> AgentState:
    """World model simulator agent node"""
    agent = _get_agent(AgentType.WORLD_MODEL_SIMULATOR)
    return await agent.execute(state)

async def hmem_store_node(state: AgentState) -> AgentState:
    """H-Mem store agent node"""
    agent = _get_agent(AgentType.HMEM_STORE)
    return await agent.execute(state)

async def evaluator_node(state: AgentState) -> AgentState:
    """Evaluator agent node"""
    agent = _get_agent(AgentType.EVALUATOR)
    return await agent.execute(state)

async def risk_dispatch_node(state: AgentState) -> AgentState:
    """Risk dispatch agent node"""
    agent = _get_agent(AgentType.RISK_DISPATCH)
    return await agent.execute(state)

async def reporter_node(state: AgentState) -> AgentState:
    """Reporter agent node"""
    agent = _get_agent(AgentType.REPORTER)
    return await agent.execute(state)


# ============================================
# Conditional Routing Functions
# ============================================

def route_after_planner(state: AgentState) -> Literal["format_detector", "end"]:
    """Route after planner - always go to format detector"""
    return "format_detector"


def route_after_format_detector(state: AgentState) -> Literal["ingestion_executor", "end"]:
    """Route after format detector"""
    return "ingestion_executor"


def route_after_ingestion(state: AgentState) -> Literal["markovian_router", "world_model_simulator", "hmem_store", "end"]:
    """Route after ingestion based on disaster context"""
    disaster_type = state.get("context", {}).get("disaster_type", "")
    
    # For specific hazards, route to world model simulator first
    if disaster_type in ["flash_flood", "wildfire", "rock_ice_avalanche", "dam_failure", "hurricane"]:
        return "world_model_simulator"
    # For earthquake, go to hmem for SOPs
    elif disaster_type == "earthquake":
        return "hmem_store"
    else:
        return "markovian_router"


def route_after_world_model(state: AgentState) -> Literal["markovian_router", "hmem_store", "risk_dispatch", "end"]:
    """Route after world model simulation"""
    disaster_type = state.get("context", {}).get("disaster_type", "")
    
    # Flash flood/wildfire -> markovian router for alert dispatch
    if disaster_type in ["flash_flood", "wildfire", "hurricane"]:
        return "markovian_router"
    # Dam failure -> risk dispatch for precautionary override
    elif disaster_type == "dam_failure":
        return "risk_dispatch"
    # Rock-ice avalanche -> markovian for immediate dispatch
    elif disaster_type == "rock_ice_avalanche":
        return "markovian_router"
    # Earthquake -> hmem for SOPs
    elif disaster_type == "earthquake":
        return "hmem_store"
    else:
        return "risk_dispatch"


def route_after_markovian(state: AgentState) -> Literal["risk_dispatch", "evaluator", "end"]:
    """Route after markovian router"""
    return "risk_dispatch"


def route_after_hmem(state: AgentState) -> Literal["risk_dispatch", "evaluator", "end"]:
    """Route after H-Mem store"""
    return "risk_dispatch"


def route_after_risk_dispatch(state: AgentState) -> Literal["evaluator", "end"]:
    """Route after risk dispatch"""
    return "evaluator"


def route_after_evaluator(state: AgentState) -> Literal["planner", "risk_dispatch", "reporter", "end"]:
    """Route after evaluator based on quality scores"""
    
    # Check if evaluation passed
    evaluator_output = state.get("evaluator_output") or {}
    passed = evaluator_output.get("passed", False)
    
    if passed:
        return "reporter"
    
    # Check revision count
    revision_count = state.get("revision_count", 0)
    if revision_count < settings.MAX_REVISION_LOOPS:
        state["revision_count"] = revision_count + 1
        return "planner"
    
    # Max revisions reached - proceed to reporter with escalation flag
    state["escalation_needed"] = True
    return "reporter"


def route_after_reporter(state: AgentState) -> Literal["end"]:
    """Route after reporter - always end"""
    return "end"


# ============================================
# Graph Construction
# ============================================

def build_workflow() -> StateGraph:
    """Build the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add all agent nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("format_detector", format_detector_node)
    workflow.add_node("ingestion_executor", ingestion_executor_node)
    workflow.add_node("markovian_router", markovian_router_node)
    workflow.add_node("world_model_simulator", world_model_simulator_node)
    workflow.add_node("hmem_store", hmem_store_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("risk_dispatch", risk_dispatch_node)
    workflow.add_node("reporter", reporter_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add edges
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "format_detector": "format_detector",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "format_detector",
        route_after_format_detector,
        {
            "ingestion_executor": "ingestion_executor",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "ingestion_executor",
        route_after_ingestion,
        {
            "markovian_router": "markovian_router",
            "world_model_simulator": "world_model_simulator",
            "hmem_store": "hmem_store",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "world_model_simulator",
        route_after_world_model,
        {
            "markovian_router": "markovian_router",
            "hmem_store": "hmem_store",
            "risk_dispatch": "risk_dispatch",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "markovian_router",
        route_after_markovian,
        {
            "risk_dispatch": "risk_dispatch",
            "evaluator": "evaluator",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "hmem_store",
        route_after_hmem,
        {
            "risk_dispatch": "risk_dispatch",
            "evaluator": "evaluator",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "risk_dispatch",
        route_after_risk_dispatch,
        {
            "evaluator": "evaluator",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "planner": "planner",
            "risk_dispatch": "risk_dispatch",
            "reporter": "reporter",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "reporter",
        route_after_reporter,
        {
            "end": END
        }
    )
    
    return workflow.compile()


# ============================================
# Graph Factory
# ============================================

# Global compiled graph instance
_agent_graph = None


def get_agent_graph() -> StateGraph:
    """Get or create the compiled agent graph"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_workflow()
    return _agent_graph


async def create_agent_graph() -> StateGraph:
    """Create a new agent graph (for testing)"""
    return build_workflow()


# ============================================
# High-level Execution Function
# ============================================

async def run_agent_pipeline(
    job_id: str,
    input_files: List[Dict[str, Any]],
    user_request: str,
    user_preferences: Dict[str, Any] = None,
    sensor_readings: List[Any] = None,
    social_media_posts: List[Any] = None,
    official_alerts: List[Dict[str, Any]] = None,
    disaster_context: Dict[str, Any] = None
) -> AgentState:
    """Run the complete agent pipeline for a disaster response job"""
    
    from app.agents.state import create_initial_state
    
    # Create initial state
    initial_state = create_initial_state(
        job_id=job_id,
        input_files=input_files,
        user_request=user_request,
        user_preferences=user_preferences,
        sensor_readings=sensor_readings,
        social_media_posts=social_media_posts,
        official_alerts=official_alerts,
        disaster_context=disaster_context
    )
    
    # Get graph
    graph = get_agent_graph()
    
    # Run
    config = {"configurable": {"thread_id": job_id}}
    final_state = await graph.ainvoke(initial_state, config=config)
    
    return final_state


# ============================================
# Graph Visualization (for debugging)
# ============================================

def get_graph_visualization() -> str:
    """Get Mermaid diagram of the graph"""
    return """
graph TD
    A[Planner] --> B[Format Detector]
    B --> C[Ingestion Executor]
    C --> D{Disaster Type?}
    D -->|Flash Flood/Wildfire/Hurricane| E[World Model Simulator]
    D -->|Earthquake| F[H-Mem Store]
    D -->|Other| G[Markovian Router]
    E --> H{Disaster Type?}
    H -->|Flash Flood/Wildfire/Hurricane| G
    H -->|Dam Failure| I[Risk Dispatch]
    H -->|Rock-Ice Avalanche| G
    H -->|Earthquake| F
    F --> I
    G --> I
    I --> J[Evaluator]
    J --> K{Quality Check}
    K -->|Passed| L[Reporter]
    K -->|Failed - Revisions < Max| A
    K -->|Failed - Max Revisions| I
    L --> M[End]
"""


__all__ = [
    "build_workflow",
    "get_agent_graph",
    "create_agent_graph",
    "run_agent_pipeline",
    "get_graph_visualization"
]