"""
CrisisMesh FastAPI Application - Open Agent Hackathon 2026
Main entry point with disaster response API endpoints
"""
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.agents.state import (
    AgentState, AgentType, DisasterType, SeverityLevel,
    SensorReading, SocialMediaDistress, SurvivorRecord, AssetRecord
)
from app.agents.graph import run_agent_pipeline, get_agent_graph, get_graph_visualization
from app.integrations.zetaris_client import get_zetaris_client, close_zetaris_client
from app.integrations.meterless_client import get_meterless_client, close_meterless_client
from app.ml.nvidia_inference import get_nvidia_inference


# ============================================
# Pydantic Request/Response Models
# ============================================

class SensorReadingRequest(BaseModel):
    sensor_id: str
    sensor_type: str  # river_gauge, rain_gauge, seismic, weather_station
    location: Dict[str, float]  # {"lat": 27.7, "lon": 85.3}
    value: float
    unit: str
    timestamp: str
    quality_flag: str = "good"  # good, suspect, bad, missing


class SocialMediaDistressRequest(BaseModel):
    post_id: str
    platform: str
    author: str
    content: str
    timestamp: str
    location_hint: Optional[str] = None
    language: str = "en"
    engagement: Dict[str, int] = Field(default_factory=dict)


class OfficialAlertRequest(BaseModel):
    alert_id: str
    source: str  # NWS, AEMET, DHM, etc.
    event_type: str
    severity: str
    certainty: str
    urgency: str
    polygon: Optional[Dict[str, Any]] = None
    effective: str
    expires: Optional[str] = None
    description: str
    instruction: Optional[str] = None


class DisasterResponseRequest(BaseModel):
    """Request to initiate disaster response"""
    job_id: Optional[str] = None
    user_request: str
    disaster_type: Optional[DisasterType] = None
    severity: Optional[SeverityLevel] = None
    location: Optional[Dict[str, float]] = None  # lat/lon
    sensor_readings: List[SensorReadingRequest] = Field(default_factory=list)
    social_media_posts: List[SocialMediaDistressRequest] = Field(default_factory=list)
    official_alerts: List[OfficialAlertRequest] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)


class DisasterResponseResponse(BaseModel):
    """Response from disaster response"""
    job_id: str
    status: str
    trace_id: Optional[str] = None
    final_output: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    sample_mode: bool
    services: Dict[str, str]
    timestamp: str


# ============================================
# Global State
# ============================================

_active_jobs: Dict[str, Dict[str, Any]] = {}


# ============================================
# Lifespan
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Sample Mode: {settings.SAMPLE_MODE}")
    print(f"   GPU Enabled: {settings.USE_GPU}")
    
    # Initialize integrations
    await get_zetaris_client()
    await get_meterless_client()
    await get_nvidia_inference()
    
    # Initialize agent graph
    get_agent_graph()
    
    print("✅ Backend ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_zetaris_client()
    await close_meterless_client()
    print("✅ Shutdown complete")


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Disaster Management Multi-Agent System for Open Agent Hackathon 2026",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Endpoints
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        sample_mode=settings.SAMPLE_MODE,
        services={
            "zetaris": "connected" if settings.SAMPLE_MODE else "configured",
            "meterless": "connected" if settings.SAMPLE_MODE else "configured",
            "nvidia": "initialized" if settings.SAMPLE_MODE else "configured",
            "redis": "connected" if settings.SAMPLE_MODE else "configured",
            "postgres": "connected" if settings.SAMPLE_MODE else "configured"
        },
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {"ready": True}


@app.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"alive": True}


# ============================================
# Disaster Response Endpoints
# ============================================

@app.post("/api/v1/disaster/respond", response_model=DisasterResponseResponse)
async def initiate_disaster_response(
    request: DisasterResponseRequest,
    background_tasks: BackgroundTasks
):
    """Initiate disaster response with multi-agent pipeline"""
    
    job_id = request.job_id or f"job_{uuid.uuid4().hex[:12]}"
    started_at = datetime.utcnow().isoformat()
    
    # Store job info
    _active_jobs[job_id] = {
        "status": "running",
        "started_at": started_at,
        "request": request.model_dump()
    }
    
    # Convert request models to internal format
    sensor_readings = [
        SensorReading(
            sensor_id=s.sensor_id,
            sensor_type=s.sensor_type,
            location=s.location,
            value=s.value,
            unit=s.unit,
            timestamp=s.timestamp,
            quality_flag=s.quality_flag
        )
        for s in request.sensor_readings
    ]
    
    social_media_posts = [
        SocialMediaDistress(
            post_id=p.post_id,
            platform=p.platform,
            author=p.author,
            content=p.content,
            timestamp=p.timestamp,
            location_hint=p.location_hint,
            language=p.language,
            engagement=p.engagement
        )
        for p in request.social_media_posts
    ]
    
    official_alerts = [
        OfficialAlertRequest(
            alert_id=a.alert_id,
            source=a.source,
            event_type=a.event_type,
            severity=a.severity,
            certainty=a.certainty,
            urgency=a.urgency,
            polygon=a.polygon,
            effective=a.effective,
            expires=a.expires,
            description=a.description,
            instruction=a.instruction
        )
        for a in request.official_alerts
    ]
    
    # Build disaster context
    disaster_context = {}
    if request.disaster_type:
        disaster_context["disaster_type"] = request.disaster_type.value
    if request.severity:
        disaster_context["severity"] = request.severity.value
    if request.location:
        disaster_context["location"] = request.location
    
    # Run pipeline in background
    async def run_pipeline():
        try:
            final_state = await run_agent_pipeline(
                job_id=job_id,
                input_files=[],  # No file uploads for disaster response
                user_request=request.user_request,
                user_preferences=request.user_preferences,
                sensor_readings=sensor_readings,
                social_media_posts=social_media_posts,
                official_alerts=official_alerts,
                disaster_context=disaster_context
            )
            
            completed_at = datetime.utcnow().isoformat()
            _active_jobs[job_id].update({
                "status": "completed" if final_state.get("final_output") else "failed",
                "completed_at": completed_at,
                "final_output": final_state.get("final_output"),
                "errors": final_state.get("errors", []),
                "trace_id": final_state.get("trace_id")
            })
            
        except Exception as e:
            completed_at = datetime.utcnow().isoformat()
            _active_jobs[job_id].update({
                "status": "failed",
                "completed_at": completed_at,
                "errors": [str(e)]
            })
    
    background_tasks.add_task(run_pipeline)
    
    return DisasterResponseResponse(
        job_id=job_id,
        status="accepted",
        started_at=started_at
    )


@app.post("/api/v1/disaster/respond/sync", response_model=DisasterResponseResponse)
async def initiate_disaster_response_sync(request: DisasterResponseRequest):
    """Initiate disaster response synchronously (for testing)"""
    
    job_id = request.job_id or f"job_{uuid.uuid4().hex[:12]}"
    started_at = datetime.utcnow().isoformat()
    
    # Convert request models
    sensor_readings = [
        SensorReading(
            sensor_id=s.sensor_id,
            sensor_type=s.sensor_type,
            location=[s.location.get("lon", 0), s.location.get("lat", 0)],
            value=s.value,
            unit=s.unit,
            timestamp=datetime.fromisoformat(s.timestamp.replace("Z", "+00:00")) if isinstance(s.timestamp, str) else s.timestamp,
            quality_flag=s.quality_flag
        )
        for s in request.sensor_readings
    ]
    
    social_media_posts = [
        SocialMediaDistress(
            post_id=p.post_id,
            platform=p.platform,
            author=p.author,
            content=p.content,
            timestamp=p.timestamp,
            location_hint=p.location_hint,
            language=p.language,
            engagement=p.engagement
        )
        for p in request.social_media_posts
    ]
    
    official_alerts = [
        OfficialAlertRequest(
            alert_id=a.alert_id,
            source=a.source,
            event_type=a.event_type,
            severity=a.severity,
            certainty=a.certainty,
            urgency=a.urgency,
            polygon=a.polygon,
            effective=a.effective,
            expires=a.expires,
            description=a.description,
            instruction=a.instruction
        )
        for a in request.official_alerts
    ]
    
    disaster_context = {}
    if request.disaster_type:
        disaster_context["disaster_type"] = request.disaster_type.value
    if request.severity:
        disaster_context["severity"] = request.severity.value
    if request.location:
        disaster_context["location"] = request.location
    
    # Run pipeline synchronously
    final_state = await run_agent_pipeline(
        job_id=job_id,
        input_files=[],
        user_request=request.user_request,
        user_preferences=request.user_preferences,
        sensor_readings=sensor_readings,
        social_media_posts=social_media_posts,
        official_alerts=official_alerts,
        disaster_context=disaster_context
    )
    
    completed_at = datetime.utcnow().isoformat()
    duration = (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds()
    
    return DisasterResponseResponse(
        job_id=job_id,
        status="completed" if final_state.get("final_output") else "failed",
        trace_id=final_state.get("trace_id"),
        final_output=final_state.get("final_output"),
        errors=final_state.get("errors", []),
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration
    )


@app.get("/api/v1/disaster/respond/{job_id}", response_model=DisasterResponseResponse)
async def get_disaster_response(job_id: str):
    """Get disaster response job status"""
    
    if job_id not in _active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = _active_jobs[job_id]
    
    response = DisasterResponseResponse(
        job_id=job_id,
        status=job["status"],
        started_at=job["started_at"]
    )
    
    if "completed_at" in job:
        response.completed_at = job["completed_at"]
        response.duration_seconds = (
            datetime.fromisoformat(job["completed_at"]) - 
            datetime.fromisoformat(job["started_at"])
        ).total_seconds()
    
    if "final_output" in job:
        response.final_output = job["final_output"]
    
    if "errors" in job:
        response.errors = job["errors"]
    
    if "trace_id" in job:
        response.trace_id = job["trace_id"]
    
    return response


@app.get("/api/v1/disaster/respond/{job_id}/trace")
async def get_disaster_response_trace(job_id: str):
    """Get detailed trace for a disaster response job"""
    
    if job_id not in _active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = _active_jobs[job_id]
    
    # Get traces from Meterless
    from app.integrations.meterless_client import get_meterless_client
    client = await get_meterless_client()
    traces = client.get_job_traces(job_id)
    
    return {
        "job_id": job_id,
        "traces": [
            {
                "trace_id": t.trace_id,
                "agent_type": t.agent_type,
                "start_time": t.start_time.isoformat(),
                "end_time": t.end_time.isoformat() if t.end_time else None,
                "events": [
                    {
                        "span_id": e.span_id,
                        "agent_name": e.agent_name,
                        "operation": e.operation,
                        "start_time": e.start_time.isoformat(),
                        "end_time": e.end_time.isoformat() if e.end_time else None,
                        "duration_ms": e.duration_ms,
                        "status": e.status,
                        "error": e.error
                    }
                    for e in t.events
                ],
                "state_snapshots": t.state_snapshots
            }
            for t in traces
        ]
    }


# ============================================
# Scenario Testing Endpoints
# ============================================

@app.get("/api/v1/scenarios")
async def list_scenarios():
    """List available disaster scenarios for testing"""
    
    scenarios = [
        {
            "id": "texas_flash_flood_2025",
            "name": "Central Texas Flash Flood (July 2025)",
            "disaster_type": "flash_flood",
            "severity": "critical",
            "failure_archetype": "Sleeping Supervisor & Manual Approval Bottleneck",
            "description": "Overnight flood wall with delayed alert due to supervisor asleep",
            "test_data": {
                "sensor_readings": [
                    {"sensor_id": "guadalupe_001", "sensor_type": "river_gauge", "location": {"lat": 30.0, "lon": -99.5}, "value": 34.0, "unit": "ft", "timestamp": "2025-07-04T04:00:00Z", "quality_flag": "good"}
                ],
                "official_alerts": [
                    {"alert_id": "nws_001", "source": "NWS", "event_type": "Flash Flood Warning", "severity": "Severe", "certainty": "Observed", "urgency": "Immediate", "effective": "2025-07-04T01:14:00Z", "description": "Flash flooding ongoing"}
                ]
            }
        },
        {
            "id": "la_wildfires_2025",
            "name": "Los Angeles Wildfires (Jan 2025)",
            "disaster_type": "wildfire",
            "severity": "critical",
            "failure_archetype": "Polygon Target Miss & Single-Operator Overload",
            "description": "Three simultaneous fires, single operator, unbounded county-wide alerts",
            "test_data": {
                "sensor_readings": [],
                "official_alerts": [
                    {"alert_id": "la_001", "source": "LA_OEM", "event_type": "Wildfire Evacuation", "severity": "Extreme", "certainty": "Observed", "urgency": "Immediate", "effective": "2025-01-08T03:30:00Z", "description": "Eaton Fire approaching West Altadena"}
                ]
            }
        },
        {
            "id": "valencia_dana_2024",
            "name": "Valencia DANA Flash Flood (Oct 2024)",
            "disaster_type": "flash_flood",
            "severity": "critical",
            "failure_archetype": "Forecast-to-Governance Disconnect",
            "description": "Red Alert at 7 AM, phone alert at 8:11 PM - 13 hour gap",
            "test_data": {
                "sensor_readings": [],
                "official_alerts": [
                    {"alert_id": "aemet_001", "source": "AEMET", "event_type": "Red Alert - Heavy Rain", "severity": "Extreme", "certainty": "Observed", "urgency": "Immediate", "effective": "2024-10-29T07:00:00Z", "description": "Extreme rainfall expected"}
                ]
            }
        },
        {
            "id": "nepal_bhote_koshi_2026",
            "name": "Nepal Bhote Koshi Rock-Ice Avalanche (Aug 2026)",
            "disaster_type": "rock_ice_avalanche",
            "severity": "critical",
            "failure_archetype": "Sensor Destruction & Single-Modality Blindness",
            "description": "Gauges destroyed in 7 minutes, reliance on water-level thresholds only",
            "test_data": {
                "sensor_readings": [
                    {"sensor_id": "border_gauge", "sensor_type": "river_gauge", "location": {"lat": 27.9, "lon": 85.8}, "value": 0, "unit": "m", "timestamp": "2026-08-26T09:28:00Z", "quality_flag": "missing"},
                    {"sensor_id": "syabrubesi_gauge", "sensor_type": "river_gauge", "location": {"lat": 28.1, "lon": 85.4}, "value": 0, "unit": "m", "timestamp": "2026-08-26T09:29:00Z", "quality_flag": "missing"}
                ],
                "official_alerts": [
                    {"alert_id": "dhm_001", "source": "DHM", "event_type": "Flash Flood", "severity": "Severe", "certainty": "Possible", "urgency": "Immediate", "effective": "2026-08-26T09:35:00Z", "description": "Flood reported via phone call"}
                ]
            }
        },
        {
            "id": "nepal_floods_2026",
            "name": "Nepal Multi-Agency Registry Divergence (Aug/Sep 2026)",
            "disaster_type": "flash_flood",
            "severity": "high",
            "failure_archetype": "Manual PDF-to-CSV Nightmares & Registry Divergence",
            "description": "Three incompatible rescued figures across competing portals",
            "test_data": {
                "survivor_registries": [
                    {"name": "John Doe", "location": "Kathmandu", "status": "rescued", "source": "Setu Rapid"},
                    {"name": "Jane Smith", "location": "Lalitpur", "status": "rescued", "source": "BIPAD Portal"}
                ]
            }
        },
        {
            "id": "derna_dam_2023",
            "name": "Derna Dam Collapse (Sep 2023)",
            "disaster_type": "dam_failure",
            "severity": "critical",
            "failure_archetype": "Contradictory Official Messaging & Lethal Curfew Traps",
            "description": "Curfew imposed, then reassured dams OK, then evacuation after collapse",
            "test_data": {
                "official_alerts": [
                    {"alert_id": "libya_001", "source": "Water Ministry", "event_type": "Curfew", "severity": "High", "certainty": "Observed", "urgency": "Immediate", "effective": "2023-09-10T20:00:00Z", "description": "Stay at home curfew"},
                    {"alert_id": "libya_002", "source": "Water Ministry", "event_type": "All Clear", "severity": "Low", "certainty": "Observed", "urgency": "Expected", "effective": "2023-09-11T01:12:00Z", "description": "Dams in good condition"},
                    {"alert_id": "libya_003", "source": "Water Ministry", "event_type": "Evacuation", "severity": "Extreme", "certainty": "Observed", "urgency": "Immediate", "effective": "2023-09-11T02:59:00Z", "description": "Evacuate immediately"}
                ]
            }
        },
        {
            "id": "nepal_floods_multilingual_2026",
            "name": "Nepal Floods - Multilingual Gap (Aug 2026)",
            "disaster_type": "flash_flood",
            "severity": "high",
            "failure_archetype": "Unilingual Generic Boilerplate Alerts",
            "description": "Nepali-only alerts on international trekking route with 636 missing foreigners",
            "test_data": {
                "official_alerts": [
                    {"alert_id": "nepal_001", "source": "Nepal NDRRMA", "event_type": "Flood Warning", "severity": "Severe", "certainty": "Observed", "urgency": "Immediate", "effective": "2026-08-15T10:00:00Z", "description": "Remain in a safe location"}
                ]
            }
        },
        {
            "id": "helene_telecom_2024",
            "name": "Hurricane Helene Telecom Isolation (Sep 2024)",
            "disaster_type": "hurricane",
            "severity": "critical",
            "failure_archetype": "Total Telecom, Power & Road Isolation",
            "description": "11 NC counties isolated, landslides block roads to tower generators",
            "test_data": {
                "sensor_readings": [],
                "official_alerts": [
                    {"alert_id": "helene_001", "source": "NWS", "event_type": "Hurricane Warning", "severity": "Extreme", "certainty": "Observed", "urgency": "Immediate", "effective": "2024-09-26T12:00:00Z", "description": "Hurricane Helene approaching"}
                ]
            }
        },
        {
            "id": "turkey_earthquake_2023",
            "name": "Türkiye-Syria Earthquake (Feb 2023)",
            "disaster_type": "earthquake",
            "severity": "critical",
            "failure_archetype": "Social Media Distress Overload & Geocoding Hallucinations",
            "description": "1.8M tweets in 12 hours, 4% geocoded to wrong city",
            "test_data": {
                "social_media_posts": [
                    {"post_id": "tw_001", "platform": "twitter", "author": "user1", "content": "Help! Trapped under rubble at Atatürk Street, Kahramanmaraş", "timestamp": "2023-02-06T04:20:00Z", "language": "tr"},
                    {"post_id": "tw_002", "platform": "twitter", "author": "user2", "content": "My family stuck in Antakya, need rescue!", "timestamp": "2023-02-06T04:25:00Z", "language": "tr"}
                ]
            }
        },
        {
            "id": "trishuli_tunnels_2026",
            "name": "Trishuli Hydropower Tunnel Entrapment (Aug 2026)",
            "disaster_type": "rock_ice_avalanche",
            "severity": "critical",
            "failure_archetype": "High-Tech Dashboards vs Specialized Field Equipment",
            "description": "500 workers trapped in dark tunnels, only smartphone flashlights available",
            "test_data": {
                "sensor_readings": [],
                "official_alerts": [
                    {"alert_id": "trishuli_001", "source": "Nepali Army", "event_type": "Tunnel Flooding", "severity": "Extreme", "certainty": "Observed", "urgency": "Immediate", "effective": "2026-08-26T10:00:00Z", "description": "Workers trapped in Upper Trishuli-1 tunnel"}
                ]
            }
        }
    ]
    
    return {"scenarios": scenarios}


@app.post("/api/v1/scenarios/{scenario_id}/run", response_model=DisasterResponseResponse)
async def run_scenario(scenario_id: str, overrides: Dict[str, Any] = None):
    """Run a predefined disaster scenario"""
    
    # Find scenario
    scenarios_list = (await list_scenarios())["scenarios"]
    scenario = next((s for s in scenarios_list if s["id"] == scenario_id), None)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    test_data = scenario["test_data"]
    
    # Build request
    request = DisasterResponseRequest(
        user_request=f"Execute disaster response for {scenario['name']}",
        disaster_type=DisasterType(scenario["disaster_type"]),
        severity=SeverityLevel(scenario["severity"]),
        sensor_readings=[SensorReadingRequest(**s) for s in test_data.get("sensor_readings", [])],
        social_media_posts=[SocialMediaDistressRequest(**s) for s in test_data.get("social_media_posts", [])],
        official_alerts=[OfficialAlertRequest(**a) for a in test_data.get("official_alerts", [])],
        user_preferences=overrides or {}
    )
    
    # Run synchronously
    return await initiate_disaster_response_sync(request)


# ============================================
# Graph Visualization
# ============================================

@app.get("/api/v1/graph/visualize")
async def visualize_graph():
    """Get graph visualization as Mermaid diagram"""
    return {"mermaid": get_graph_visualization()}


# ============================================
# Demo Data Endpoints
# ============================================

@app.get("/api/v1/demo/sample-sensor-data")
async def get_sample_sensor_data():
    """Get sample sensor data for testing"""
    
    return {
        "river_gauges": [
            {"sensor_id": "guadalupe_kerr", "location": {"lat": 30.0, "lon": -99.5}, "water_level_ft": 34.0, "flood_stage_ft": 22.0, "status": "major_flood"},
            {"sensor_id": "bhote_koshi_border", "location": {"lat": 27.9, "lon": 85.8}, "water_level_m": 0, "status": "destroyed"},
            {"sensor_id": "trishuli_betrawati", "location": {"lat": 27.9, "lon": 85.2}, "water_level_m": 8.5, "flood_stage_m": 6.0, "status": "above_threshold"}
        ],
        "rain_gauges": [
            {"sensor_id": "kerr_county_01", "location": {"lat": 30.1, "lon": -99.3}, "rainfall_inches": 12.5, "duration_hours": 6, "status": "extreme"}
        ],
        "seismic": [
            {"sensor_id": "langtang_seismic", "location": {"lat": 28.2, "lon": 85.6}, "magnitude": 4.2, "depth_km": 10, "timestamp": "2026-08-26T09:25:00Z"}
        ]
    }


@app.get("/api/v1/demo/sample-social-media")
async def get_sample_social_media():
    """Get sample social media distress posts"""
    
    return {
        "posts": [
            {
                "post_id": "tw_nepal_001",
                "platform": "twitter",
                "author": "trekker_john",
                "content": "Flash flood in Langtang valley! Bridge washed away. Group of 12 trekkers at Kyangjin Gompa need evacuation. Coordinates: 28.2, 85.6",
                "timestamp": "2026-08-26T09:30:00Z",
                "location_hint": "Kyangjin Gompa, Langtang",
                "language": "en",
                "engagement": {"retweets": 245, "likes": 189}
            },
            {
                "post_id": "fb_texas_001",
                "platform": "facebook",
                "author": "sarah_miller",
                "content": "Water rising fast at Camp Mystic! Kids in cabins, cars floating away. Guadalupe River out of banks. 911 not answering.",
                "timestamp": "2025-07-04T04:22:00Z",
                "location_hint": "Camp Mystic, Kerr County, TX",
                "language": "en",
                "engagement": {"shares": 1200, "comments": 340}
            }
        ]
    }


@app.get("/api/v1/demo/sample-alerts")
async def get_sample_alerts():
    """Get sample official alerts"""
    
    return {
        "alerts": [
            {
                "alert_id": "nws_tx_001",
                "source": "NWS",
                "event_type": "Flash Flood Warning",
                "severity": "Severe",
                "certainty": "Observed",
                "urgency": "Immediate",
                "polygon": {"type": "Polygon", "coordinates": [[[-99.5, 30.0], [-99.0, 30.0], [-99.0, 30.5], [-99.5, 30.5], [-99.5, 30.0]]]},
                "effective": "2025-07-04T01:14:00Z",
                "expires": "2025-07-04T07:14:00Z",
                "description": "Flash flooding ongoing in Kerr County. Guadalupe River at major flood stage.",
                "instruction": "Move to higher ground immediately. Do not drive through flooded roads."
            },
            {
                "alert_id": "aemet_valencia_001",
                "source": "AEMET",
                "event_type": "Red Alert - Heavy Rain",
                "severity": "Extreme",
                "certainty": "Observed",
                "urgency": "Immediate",
                "polygon": {"type": "Polygon", "coordinates": [[[-0.5, 39.5], [0.0, 39.5], [0.0, 40.0], [-0.5, 40.0], [-0.5, 39.5]]]},
                "effective": "2024-10-29T07:00:00Z",
                "expires": "2024-10-29T20:00:00Z",
                "description": "Extreme rainfall up to 500mm expected in Valencia province",
                "instruction": "Avoid travel. Stay indoors. Move to upper floors."
            }
        ]
    }


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )