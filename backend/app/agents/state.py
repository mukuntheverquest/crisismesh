"""
CrisisMesh Agent State - Open Agent Hackathon 2026
Shared state for LangGraph multi-agent orchestration
"""
from typing import Dict, Any, List, Optional, Literal, TypedDict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


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


class DisasterType(str, Enum):
    FLASH_FLOOD = "flash_flood"
    WILDFIRE = "wildfire"
    EARTHQUAKE = "earthquake"
    LANDSLIDE = "landslide"
    DAM_FAILURE = "dam_failure"
    ROCK_ICE_AVALANCHE = "rock_ice_avalanche"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    TSUNAMI = "tsunami"
    VOLCANIC_ERUPTION = "volcanic_eruption"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    PANDEMIC = "pandemic"


class SeverityLevel(str, Enum):
    ADVISORY = "advisory"
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class AlertStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    AUTO_APPROVED = "auto_approved"
    DISPATCHED = "dispatched"
    ACKNOWLEDGED = "acknowledged"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AssetType(str, Enum):
    GROUND_VEHICLE = "ground_vehicle"
    HELICOPTER = "helicopter"
    DRONE = "drone"
    SHALLOW_DRAFT_BOAT = "shallow_draft_boat"
    TUNNEL_RESCUE_TEAM = "tunnel_rescue_team"
    DMAT_TEAM = "dmat_team"
    ENGINEERING_TEAM = "engineering_team"
    LI_DAR_THERMAL_DRONE = "lidar_thermal_drone"
    HEAVY_LIFT_DRONE = "heavy_lift_drone"
    SATELLITE_IMAGERY = "satellite_imagery"
    VHF_RADIO = "vhf_radio"
    SIREN_SYSTEM = "siren_system"


class TaskNode(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: AgentType
    input_data: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 3,
        "backoff": "exponential",
        "fallback_agent": None
    })
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    nodes: Dict[str, TaskNode] = Field(default_factory=dict)
    entry_points: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AlertPolygon(BaseModel):
    """Geographic polygon for alert targeting"""
    coordinates: List[List[List[float]]]  # GeoJSON Polygon
    properties: Dict[str, Any] = Field(default_factory=dict)
    hazard_type: DisasterType
    severity: SeverityLevel
    expires_at: datetime
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    issued_by: str = "crisismesh"
    languages: List[str] = Field(default_factory=lambda: ["en"])
    arrival_eta_minutes: Optional[int] = None
    shelter_coordinates: Optional[List[float]] = None
    community_focal_points: List[str] = Field(default_factory=list)


class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str  # river_gauge, seismic, weather_station, satellite
    location: List[float]  # [lon, lat]
    timestamp: datetime
    value: float
    unit: str
    quality_flag: str = "good"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SocialMediaDistress(BaseModel):
    post_id: str
    platform: str  # twitter, facebook, etc.
    author: str
    content: str
    language: str
    location_mentioned: Optional[List[str]] = None
    geocoded_location: Optional[List[float]] = None
    timestamp: datetime
    urgency_keywords: List[str] = Field(default_factory=list)
    verified: bool = False
    sar_damage_confidence: Optional[float] = None


class SurvivorRecord(BaseModel):
    record_id: str
    source: str  # army_pdf, family_tracing_api, internal_log, ngo_report
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    last_known_location: Optional[List[float]] = None
    status: str  # missing, rescued, deceased, safe
    timestamp: datetime
    source_document_id: str
    embedding: Optional[List[float]] = None


class AssetRecord(BaseModel):
    asset_id: str
    asset_type: AssetType
    operator: str
    capabilities: List[str]
    location: List[float]
    status: str  # available, deployed, maintenance, offline
    specialization: List[str] = Field(default_factory=list)
    contact_info: Dict[str, str] = Field(default_factory=dict)
    accreditation: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SOPRecord(BaseModel):
    sop_id: str
    trigger_conditions: Dict[str, Any]
    required_actions: List[Dict[str, Any]]
    responsible_agencies: List[str]
    cross_jurisdictional: bool = False
    priority_demographics: List[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: Optional[datetime] = None
    version: str = "1.0"


# LangGraph State
class AgentState(TypedDict):
    # Job identification
    job_id: str
    trace_id: str
    correlation_id: str

    # Input data
    input_files: List[Dict[str, Any]]
    sensor_readings: List[SensorReading]
    social_media_posts: List[SocialMediaDistress]
    official_alerts: List[Dict[str, Any]]
    disaster_context: Dict[str, Any]

    # User request
    user_request: str
    user_preferences: Dict[str, Any]

    # Agent outputs
    planner_output: Optional[Dict[str, Any]]
    format_detector_output: Optional[Dict[str, Any]]
    ingestion_executor_output: Optional[Dict[str, Any]]
    evaluator_output: Optional[Dict[str, Any]]
    risk_dispatch_output: Optional[Dict[str, Any]]
    markovian_router_output: Optional[Dict[str, Any]]
    world_model_simulator_output: Optional[Dict[str, Any]]
    hmem_store_output: Optional[Dict[str, Any]]
    reporter_output: Optional[Dict[str, Any]]

    # Task graph
    task_graph: Optional[TaskGraph]
    current_task_id: Optional[str]
    next_agent: Optional[AgentType]

    # Shared memory/context
    context: Dict[str, Any]

    # Quality & validation
    quality_scores: Dict[str, float]
    validation_results: Dict[str, Any]
    revision_count: int

    # Errors & control
    errors: List[Dict[str, Any]]
    should_continue: bool
    escalation_needed: bool

    # Final output
    final_output: Optional[Dict[str, Any]]
    provenance: Dict[str, Any]

    # Metadata
    created_at: str
    updated_at: str


def create_initial_state(
    job_id: str,
    input_files: List[Dict[str, Any]],
    user_request: str,
    user_preferences: Dict[str, Any] = None,
    sensor_readings: List[SensorReading] = None,
    social_media_posts: List[SocialMediaDistress] = None,
    official_alerts: List[Dict[str, Any]] = None,
    disaster_context: Dict[str, Any] = None
) -> AgentState:
    """Create initial state for a new agent pipeline run"""
    from uuid import uuid4
    now = datetime.utcnow().isoformat()

    return AgentState(
        job_id=job_id,
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        input_files=input_files,
        sensor_readings=sensor_readings or [],
        social_media_posts=social_media_posts or [],
        official_alerts=official_alerts or [],
        disaster_context=disaster_context or {},
        user_request=user_request,
        user_preferences=user_preferences or {},
        planner_output=None,
        format_detector_output=None,
        ingestion_executor_output=None,
        evaluator_output=None,
        risk_dispatch_output=None,
        markovian_router_output=None,
        world_model_simulator_output=None,
        hmem_store_output=None,
        reporter_output=None,
        task_graph=None,
        current_task_id=None,
        next_agent=AgentType.PLANNER,
        context={},
        quality_scores={},
        validation_results={},
        revision_count=0,
        errors=[],
        should_continue=True,
        escalation_needed=False,
        final_output=None,
        provenance={
            "job_id": job_id,
            "trace_id": str(uuid4()),
            "correlation_id": str(uuid4()),
            "input_files": input_files,
            "agent_trace": {},
            "started_at": now
        },
        created_at=now,
        updated_at=now
    )


__all__ = [
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
    "create_initial_state"
]