"""
CrisisMesh Agents Package - Open Agent Hackathon 2026
"""
from app.agents.base import (
    BaseAgent,
    AgentFactory,
    trace_agent,
    trace_tool_call,
    run_with_timeout,
    retry_with_backoff
)
from app.agents.state import (
    AgentType,
    TaskStatus,
    DisasterType,
    SeverityLevel,
    AlertStatus,
    AssetType,
    TaskNode,
    TaskGraph,
    AlertPolygon,
    SensorReading,
    SocialMediaDistress,
    SurvivorRecord,
    AssetRecord,
    SOPRecord,
    AgentState,
    create_initial_state
)

# Agent classes - imported lazily when needed
# from app.agents.planner import PlannerAgent
# from app.agents.domain_agents.format_detector import FormatDetectorAgent
# from app.agents.domain_agents.ingestion_executor import IngestionExecutorAgent
# from app.agents.domain_agents.markovian_router import MarkovianRouterAgent
# from app.agents.domain_agents.world_model_simulator import WorldModelSimulatorAgent
# from app.agents.domain_agents.hmem_store import HMemStoreAgent
# from app.agents.evaluator import EvaluatorAgent
# from app.agents.risk_agent import RiskDispatchAgent
# from app.agents.reporter import ReporterAgent

# Lazy agent registration
_agents_registered = False
_agent_classes = {}

def _get_agent_class(agent_type: AgentType):
    """Get agent class by type (lazy import)"""
    if agent_type not in _agent_classes:
        if agent_type == AgentType.PLANNER:
            from app.agents.planner import PlannerAgent
            _agent_classes[agent_type] = PlannerAgent
        elif agent_type == AgentType.FORMAT_DETECTOR:
            from app.agents.domain_agents.format_detector import FormatDetectorAgent
            _agent_classes[agent_type] = FormatDetectorAgent
        elif agent_type == AgentType.INGESTION_EXECUTOR:
            from app.agents.domain_agents.ingestion_executor import IngestionExecutorAgent
            _agent_classes[agent_type] = IngestionExecutorAgent
        elif agent_type == AgentType.MARKOVIAN_ROUTER:
            from app.agents.domain_agents.markovian_router import MarkovianRouterAgent
            _agent_classes[agent_type] = MarkovianRouterAgent
        elif agent_type == AgentType.WORLD_MODEL_SIMULATOR:
            from app.agents.domain_agents.world_model_simulator import WorldModelSimulatorAgent
            _agent_classes[agent_type] = WorldModelSimulatorAgent
        elif agent_type == AgentType.HMEM_STORE:
            from app.agents.domain_agents.hmem_store import HMemStoreAgent
            _agent_classes[agent_type] = HMemStoreAgent
        elif agent_type == AgentType.EVALUATOR:
            from app.agents.evaluator import EvaluatorAgent
            _agent_classes[agent_type] = EvaluatorAgent
        elif agent_type == AgentType.RISK_DISPATCH:
            from app.agents.risk_agent import RiskDispatchAgent
            _agent_classes[agent_type] = RiskDispatchAgent
        elif agent_type == AgentType.REPORTER:
            from app.agents.reporter import ReporterAgent
            _agent_classes[agent_type] = ReporterAgent
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    return _agent_classes[agent_type]

def _register_agents():
    """Register all agents with the factory (called lazily)"""
    global _agents_registered
    if not _agents_registered:
        for agent_type in AgentType:
            agent_class = _get_agent_class(agent_type)
            AgentFactory.register(agent_type, agent_class())
        _agents_registered = True

def ensure_agents_registered():
    """Ensure agents are registered (call this before using AgentFactory)"""
    _register_agents()

def get_agent_class(agent_type: AgentType):
    """Get agent class by type"""
    ensure_agents_registered()
    return _get_agent_class(agent_type)

__all__ = [
    "BaseAgent",
    "AgentFactory",
    "trace_agent",
    "trace_tool_call",
    "run_with_timeout",
    "retry_with_backoff",
    "AgentType",
    "TaskStatus",
    "DisasterType",
    "SeverityLevel",
    "AlertStatus",
    "AssetType",
    "TaskNode",
    "TaskGraph",
    "AlertPolygon",
    "SensorReading",
    "SocialMediaDistress",
    "SurvivorRecord",
    "AssetRecord",
    "SOPRecord",
    "AgentState",
    "create_initial_state",
    "ensure_agents_registered",
    "get_agent_class"
]