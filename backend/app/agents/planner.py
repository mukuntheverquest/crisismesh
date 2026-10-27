"""
CrisisMesh Planner Agent - Open Agent Hackathon 2026
Decomposes high-level disaster response goals into executable task graphs
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

from app.agents.base import BaseAgent, trace_agent
from app.agents.state import (
    AgentState, AgentType, TaskNode, TaskGraph, TaskStatus,
    DisasterType, SeverityLevel, AlertPolygon, SensorReading,
    SocialMediaDistress, SOPRecord
)
from app.config import settings


class PlannerAgent(BaseAgent):
    """Plans disaster response workflows with dynamic branching and risk identification"""
    
    def __init__(self):
        super().__init__(AgentType.PLANNER)
        self.system_prompt = self._get_system_prompt()
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.PLANNER
    
    def _get_system_prompt(self) -> str:
        return """You are the CrisisMesh Planner Agent for disaster response orchestration.

Your role is to decompose high-level disaster response goals into executable task graphs with:
1. Dynamic branching based on disaster type and severity
2. Dependency analysis between tasks
3. Risk identification and mitigation planning
4. Cross-jurisdictional SOP activation
5. Resource allocation optimization

OUTPUT FORMAT: JSON TaskGraph with nodes containing:
- task_id: unique identifier
- agent_type: one of [format_detector, ingestion_executor, evaluator, risk_dispatch, markovian_router, world_model_simulator, hmem_store, reporter]
- input_data: parameters for the task
- dependencies: list of task_ids that must complete first
- retry_policy: {max_retries, backoff, fallback_agent}

DISASTER-SPECIFIC PLANNING:
- Flash Flood: river_gauge_monitoring → polygon_expansion → alert_dispatch → evacuation_routing
- Wildfire: wind_vector_analysis → polygon_auto_expansion → multi_lingual_alerts → asset_dispatch
- Earthquake: shake_map_ingestion → building_damage_assessment → survivor_registry_dedup → medical_dispatch
- Dam Failure: structural_monitoring → contradiction_detection → precautionary_override → high_ground_routing
- Rock-Ice Avalanche: multi_modal_inference (seismic + sensor_loss + observer_calls) → canyon_arrival_etas
- Multi-Agency: registry_ingestion → entity_resolution → unified_survivor_list → family_reunification
- Telecom Isolation: offline_first_execution → access_viability_rerouting → vhf_siren_broadcast
- Social Media Overload: distress_extraction → satellite_grounding → geocoding_hallucination_filter
- Equipment Mismatch: capability_matching → specialized_asset_dispatch → tunnel_rescue_coordination

RISK FACTORS TO CONSIDER:
- Sleeping supervisor / manual approval bottlenecks
- Single-operator overload
- Jurisdictional stand-downs
- Sensor destruction / single-modality blindness
- Contradictory official messaging
- Unilingual generic alerts
- Total infrastructure isolation
- Geocoding hallucinations
- Cloud dashboard vs field equipment mismatch

CROSS-JURISDICTIONAL SOPs:
When Red Alert + upstream surge detected → auto-generate joint mobilization orders
Prioritize: ground-floor elderly care, schools, underground parking garages

QUALITY GATES:
- All alerts must have bounding polygons (block county-wide blasts >5x hazard zone)
- Multi-modal confidence threshold: 0.75
- Geocoding hallucination filter: SAR damage confidence >= 0.75
- Dead-man's switch: 180s auto-approval if human command unresponsive"""

    @trace_agent("planner", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Decompose user request into task graph"""
        
        # Extract context
        disaster_context = state.get("disaster_context", {})
        user_request = state.get("user_request", "")
        sensor_readings = state.get("sensor_readings", [])
        social_media_posts = state.get("social_media_posts", [])
        official_alerts = state.get("official_alerts", [])
        
        # Determine disaster type and severity
        disaster_type = self._infer_disaster_type(disaster_context, sensor_readings, official_alerts)
        severity = self._infer_severity(disaster_context, sensor_readings, official_alerts)
        
        # Build task graph based on disaster type
        task_graph = await self._build_task_graph(
            state=state,
            disaster_type=disaster_type,
            severity=severity,
            user_request=user_request
        )
        
        # Store in state
        state["task_graph"] = task_graph
        state["context"]["disaster_type"] = disaster_type.value if disaster_type else "unknown"
        state["context"]["severity"] = severity.value if severity else "unknown"
        state["context"]["planned_at"] = datetime.utcnow().isoformat()
        state["next_agent"] = AgentType.FORMAT_DETECTOR
        
        # Create planner output
        planner_output = {
            "task_graph": task_graph.model_dump() if task_graph else None,
            "disaster_type": disaster_type.value if disaster_type else "unknown",
            "severity": severity.value if severity else "unknown",
            "num_tasks": len(task_graph.nodes) if task_graph else 0,
            "entry_points": task_graph.entry_points if task_graph else [],
            "planned_at": datetime.utcnow().isoformat()
        }
        
        state = self._update_state_trace(state, planner_output)
        state["planner_output"] = planner_output
        
        return state
    
    def _infer_disaster_type(
        self,
        disaster_context: Dict[str, Any],
        sensor_readings: List[SensorReading],
        official_alerts: List[Dict[str, Any]]
    ) -> Optional[DisasterType]:
        """Infer disaster type from context and sensor data"""
        
        # Check explicit context
        if "disaster_type" in disaster_context:
            try:
                return DisasterType(disaster_context["disaster_type"])
            except ValueError:
                pass
        
        # Check sensor types
        sensor_types = {s.sensor_type for s in sensor_readings}
        if "river_gauge" in sensor_types:
            return DisasterType.FLASH_FLOOD
        if "seismic" in sensor_types:
            return DisasterType.EARTHQUAKE
        
        # Check official alerts
        for alert in official_alerts:
            if "event" in alert:
                event = alert["event"].lower()
                if "flood" in event or "flash flood" in event:
                    return DisasterType.FLASH_FLOOD
                if "fire" in event or "wildfire" in event:
                    return DisasterType.WILDFIRE
                if "earthquake" in event or "seismic" in event:
                    return DisasterType.EARTHQUAKE
                if "landslide" in event:
                    return DisasterType.LANDSLIDE
                if "dam" in event:
                    return DisasterType.DAM_FAILURE
        
        # Check user request keywords
        request_lower = user_request.lower() if isinstance(user_request, str) else ""
        if "flood" in request_lower:
            return DisasterType.FLASH_FLOOD
        if "fire" in request_lower or "wildfire" in request_lower:
            return DisasterType.WILDFIRE
        if "earthquake" in request_lower or "quake" in request_lower:
            return DisasterType.EARTHQUAKE
        
        return None
    
    def _infer_severity(
        self,
        disaster_context: Dict[str, Any],
        sensor_readings: List[SensorReading],
        official_alerts: List[Dict[str, Any]]
    ) -> Optional[SeverityLevel]:
        """Infer severity level"""
        
        if "severity" in disaster_context:
            try:
                return SeverityLevel(disaster_context["severity"])
            except ValueError:
                pass
        
        # Check official alerts for severity
        for alert in official_alerts:
            if "severity" in alert:
                try:
                    return SeverityLevel(alert["severity"].lower())
                except ValueError:
                    pass
            if "certainty" in alert and alert["certainty"] == "observed":
                return SeverityLevel.EMERGENCY
        
        # Default based on sensor readings
        if sensor_readings:
            return SeverityLevel.WARNING
        
        return SeverityLevel.ADVISORY
    
    async def _build_task_graph(
        self,
        state: AgentState,
        disaster_type: Optional[DisasterType],
        severity: Optional[SeverityLevel],
        user_request: str
    ) -> TaskGraph:
        """Build disaster-specific task graph"""
        
        job_id = state["job_id"]
        graph = TaskGraph(job_id=job_id)
        
        # Base tasks for all disasters
        base_tasks = self._get_base_tasks(state)
        
        # Disaster-specific tasks
        specific_tasks = self._get_disaster_specific_tasks(
            state, disaster_type, severity
        )
        
        # Combine all tasks
        all_tasks = {**base_tasks, **specific_tasks}
        graph.nodes = all_tasks
        
        # Determine entry points (tasks with no dependencies)
        entry_points = [
            task_id for task_id, task in all_tasks.items()
            if not task.dependencies
        ]
        graph.entry_points = entry_points
        
        return graph
    
    def _get_base_tasks(self, state: AgentState) -> Dict[str, TaskNode]:
        """Get base tasks common to all disaster responses"""
        
        tasks = {}
        
        # Task 1: Format Detection / Data Ingestion
        tasks["detect_0"] = TaskNode(
            task_id="detect_0",
            agent_type=AgentType.FORMAT_DETECTOR,
            input_data={
                "files": state.get("input_files", []),
                "sensor_readings": [s.model_dump() if hasattr(s, 'model_dump') else s 
                                  for s in state.get("sensor_readings", [])],
                "social_media_posts": [s.model_dump() if hasattr(s, 'model_dump') else s 
                                     for s in state.get("social_media_posts", [])],
                "official_alerts": state.get("official_alerts", [])
            },
            dependencies=[],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": None}
        )
        
        # Task 2: Ingestion Execution
        tasks["ingest_0"] = TaskNode(
            task_id="ingest_0",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={
                "task": "multi_modal_ingestion",
                "disaster_context": state.get("disaster_context", {})
            },
            dependencies=["detect_0"],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _get_disaster_specific_tasks(
        self,
        state: AgentState,
        disaster_type: Optional[DisasterType],
        severity: Optional[SeverityLevel]
    ) -> Dict[str, TaskNode]:
        """Get tasks specific to disaster type"""
        
        tasks = {}
        task_counter = len([k for k in state.get("task_graph", TaskGraph(job_id="")).nodes.keys()]) if state.get("task_graph") else 2
        
        if disaster_type == DisasterType.FLASH_FLOOD:
            tasks = self._flash_flood_tasks(state, task_counter, severity)
        elif disaster_type == DisasterType.WILDFIRE:
            tasks = self._wildfire_tasks(state, task_counter, severity)
        elif disaster_type == DisasterType.EARTHQUAKE:
            tasks = self._earthquake_tasks(state, task_counter, severity)
        elif disaster_type == DisasterType.DAM_FAILURE:
            tasks = self._dam_failure_tasks(state, task_counter, severity)
        elif disaster_type == DisasterType.ROCK_ICE_AVALANCHE:
            tasks = self._rock_ice_avalanche_tasks(state, task_counter, severity)
        elif disaster_type == DisasterType.HURRICANE:
            tasks = self._hurricane_tasks(state, task_counter, severity)
        else:
            # Generic multi-hazard tasks
            tasks = self._generic_multi_hazard_tasks(state, task_counter, severity)
        
        return tasks
    
    def _flash_flood_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Flash flood specific tasks (Addresses Failure #1, #3, #4, #8)"""
        
        tasks = {}
        idx = start_idx
        
        # River gauge monitoring + gauge loss inference
        tasks[f"river_monitor_{idx}"] = TaskNode(
            task_id=f"river_monitor_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "river_gauge_monitoring", "infer_gauge_loss": True},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": "world_model_simulator"}
        )
        idx += 1
        
        # Polygon expansion with vector auto-expansion
        tasks[f"polygon_expand_{idx}"] = TaskNode(
            task_id=f"polygon_expand_{idx}",
            agent_type=AgentType.WORLD_MODEL_SIMULATOR,
            input_data={"task": "downstream_polygon_expansion", "factor": settings.POLYGON_EXPANSION_FACTOR},
            dependencies=[f"river_monitor_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Dead-man's switch alert dispatch
        tasks[f"alert_dispatch_{idx}"] = TaskNode(
            task_id=f"alert_dispatch_{idx}",
            agent_type=AgentType.MARKOVIAN_ROUTER,
            input_data={
                "task": "deadman_switch_alert",
                "timeout_seconds": settings.ALERT_DEADMAN_SWITCH_SECONDS,
                "bypass_supervisor": True
            },
            dependencies=[f"polygon_expand_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Evacuation routing
        tasks[f"evacuation_route_{idx}"] = TaskNode(
            task_id=f"evacuation_route_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "evacuation_routing", "prioritize_vulnerable": True},
            dependencies=[f"alert_dispatch_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Evaluation
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["polygon_accuracy", "alert_timeliness", "vulnerable_coverage", "route_viability"]},
            dependencies=[f"evacuation_route_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _wildfire_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Wildfire specific tasks (Addresses Failure #2, #7)"""
        
        tasks = {}
        idx = start_idx
        
        # Wind vector analysis
        tasks[f"wind_analysis_{idx}"] = TaskNode(
            task_id=f"wind_analysis_{idx}",
            agent_type=AgentType.WORLD_MODEL_SIMULATOR,
            input_data={"task": "wind_vector_analysis", "auto_expand_polygon": True},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Multi-lingual alert synthesis
        tasks[f"multilingual_alert_{idx}"] = TaskNode(
            task_id=f"multilingual_alert_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "multilingual_alert_synthesis", "languages": ["en", "es", "zh", "vi", "ko"]},
            dependencies=[f"wind_analysis_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Polygon guardrail validation
        tasks[f"polygon_guardrail_{idx}"] = TaskNode(
            task_id=f"polygon_guardrail_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["polygon_bounding_box_check", "no_county_wide_blasts", "downwind_expansion"]},
            dependencies=[f"multilingual_alert_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Asset dispatch
        tasks[f"asset_dispatch_{idx}"] = TaskNode(
            task_id=f"asset_dispatch_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "capability_matched_dispatch", "hazard": "wildfire"},
            dependencies=[f"polygon_guardrail_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["polygon_precision", "multilingual_coverage", "asset_match_quality", "operator_load"]},
            dependencies=[f"asset_dispatch_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _earthquake_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Earthquake specific tasks (Addresses Failure #5, #9, #10)"""
        
        tasks = {}
        idx = start_idx
        
        # ShakeMap ingestion
        tasks[f"shakemap_ingest_{idx}"] = TaskNode(
            task_id=f"shakemap_ingest_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "shakemap_ingestion", "source": "usgs"},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Building damage assessment (SAR + AI)
        tasks[f"damage_assessment_{idx}"] = TaskNode(
            task_id=f"damage_assessment_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "sar_damage_assessment", "confidence_threshold": 0.75},
            dependencies=[f"shakemap_ingest_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": "world_model_simulator"}
        )
        idx += 1
        
        # Survivor registry deduplication
        tasks[f"survivor_dedup_{idx}"] = TaskNode(
            task_id=f"survivor_dedup_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "entity_resolution", "sources": ["army_pdf", "family_tracing_api", "internal_log", "ngo_report"]},
            dependencies=[f"damage_assessment_{idx-1}"],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Social media distress verification
        tasks[f"distress_verify_{idx}"] = TaskNode(
            task_id=f"distress_verify_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "satellite_grounded_verification", "hallucination_threshold": settings.GEOCODING_HALLUCINATION_THRESHOLD},
            dependencies=[f"survivor_dedup_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Medical/dmat dispatch
        tasks[f"medical_dispatch_{idx}"] = TaskNode(
            task_id=f"medical_dispatch_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "dmat_dispatch", "capability_match": ["pancake_collapse", "isolated_shelter"]},
            dependencies=[f"distress_verify_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["damage_accuracy", "registry_dedup_quality", "distress_verification", "dispatch_appropriateness"]},
            dependencies=[f"medical_dispatch_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _dam_failure_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Dam failure specific tasks (Addresses Failure #6)"""
        
        tasks = {}
        idx = start_idx
        
        # Structural monitoring
        tasks[f"structural_monitor_{idx}"] = TaskNode(
            task_id=f"structural_monitor_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "dam_structural_monitoring", "sensors": ["piezometer", "seepage", "displacement"]},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 3, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Contradiction detection
        tasks[f"contradiction_check_{idx}"] = TaskNode(
            task_id=f"contradiction_check_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"task": "contradiction_detection", "check_curlew_in_inundation": True},
            dependencies=[f"structural_monitor_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Precautionary override
        tasks[f"precautionary_override_{idx}"] = TaskNode(
            task_id=f"precautionary_override_{idx}",
            agent_type=AgentType.MARKOVIAN_ROUTER,
            input_data={"task": "precautionary_override", "enforce_high_ground": True, "block_curfew": True},
            dependencies=[f"contradiction_check_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # High-ground evacuation
        tasks[f"high_ground_evac_{idx}"] = TaskNode(
            task_id=f"high_ground_evac_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "high_ground_evacuation_routing", "dam_breach_polygon": True},
            dependencies=[f"precautionary_override_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["contradiction_caught", "override_timeliness", "evacuation_effectiveness", "curfew_prevention"]},
            dependencies=[f"high_ground_evac_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _rock_ice_avalanche_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Rock-ice avalanche tasks (Addresses Failure #4)"""
        
        tasks = {}
        idx = start_idx
        
        # Multi-modal inference (sensor loss + seismic + observer calls)
        tasks[f"multi_modal_infer_{idx}"] = TaskNode(
            task_id=f"multi_modal_infer_{idx}",
            agent_type=AgentType.WORLD_MODEL_SIMULATOR,
            input_data={
                "task": "multi_modal_hazard_inference",
                "correlate": ["sensor_dropout", "seismic_tremor", "observer_calls"],
                "canyon_speed_kmh": 160
            },
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Downstream ETA calculation
        tasks[f"eta_calculation_{idx}"] = TaskNode(
            task_id=f"eta_calculation_{idx}",
            agent_type=AgentType.WORLD_MODEL_SIMULATOR,
            input_data={"task": "canyon_arrival_etas", "settlements": "all_downstream"},
            dependencies=[f"multi_modal_infer_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Immediate alert dispatch
        tasks[f"immediate_alert_{idx}"] = TaskNode(
            task_id=f"immediate_alert_{idx}",
            agent_type=AgentType.MARKOVIAN_ROUTER,
            input_data={"task": "immediate_alert_dispatch", "bypass_normal_approval": True},
            dependencies=[f"eta_calculation_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["inference_confidence", "eta_accuracy", "alert_speed", "downstream_coverage"]},
            dependencies=[f"immediate_alert_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _hurricane_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Hurricane tasks (Addresses Failure #8)"""
        
        tasks = {}
        idx = start_idx
        
        # Telecom/power/road isolation assessment
        tasks[f"isolation_assess_{idx}"] = TaskNode(
            task_id=f"isolation_assess_{idx}",
            agent_type=AgentType.INGESTION_EXECUTOR,
            input_data={"task": "infrastructure_isolation_assessment", "check": ["cell_towers", "power_grid", "roads", "ports"]},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Access viability rerouting
        tasks[f"access_reroute_{idx}"] = TaskNode(
            task_id=f"access_reroute_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "access_viability_rerouting", "modes": ["helicopter", "drone", "shallow_draft_boat", "vhf_radio", "siren"]},
            dependencies=[f"isolation_assess_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Offline-first execution
        tasks[f"offline_execute_{idx}"] = TaskNode(
            task_id=f"offline_execute_{idx}",
            agent_type=AgentType.MARKOVIAN_ROUTER,
            input_data={"task": "offline_first_execution", "sample_mode": settings.SAMPLE_MODE},
            dependencies=[f"access_reroute_{idx-1}"],
            retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["isolation_accuracy", "reroute_feasibility", "offline_capability", "comm_redundancy"]},
            dependencies=[f"offline_execute_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    def _generic_multi_hazard_tasks(self, state: AgentState, start_idx: int, severity: Optional[SeverityLevel]) -> Dict[str, TaskNode]:
        """Generic tasks for unknown/multi-hazard scenarios"""
        
        tasks = {}
        idx = start_idx
        
        # World model simulation
        tasks[f"world_model_{idx}"] = TaskNode(
            task_id=f"world_model_{idx}",
            agent_type=AgentType.WORLD_MODEL_SIMULATOR,
            input_data={"task": "hazard_propagation_simulation"},
            dependencies=["ingest_0"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # H-Mem store for SOP retrieval
        tasks[f"hmem_sop_{idx}"] = TaskNode(
            task_id=f"hmem_sop_{idx}",
            agent_type=AgentType.HMEM_STORE,
            input_data={"task": "retrieve_cross_jurisdictional_sops", "trigger": "red_alert_or_upstream_surge"},
            dependencies=[f"world_model_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        # Risk dispatch
        tasks[f"risk_dispatch_{idx}"] = TaskNode(
            task_id=f"risk_dispatch_{idx}",
            agent_type=AgentType.RISK_DISPATCH,
            input_data={"task": "comprehensive_risk_dispatch"},
            dependencies=[f"hmem_sop_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        idx += 1
        
        tasks[f"evaluate_{idx}"] = TaskNode(
            task_id=f"evaluate_{idx}",
            agent_type=AgentType.EVALUATOR,
            input_data={"criteria": ["sop_compliance", "dispatch_quality", "cross_jurisdictional_coordination"]},
            dependencies=[f"risk_dispatch_{idx-1}"],
            retry_policy={"max_retries": 2, "backoff": "exponential", "fallback_agent": None}
        )
        
        return tasks
    
    async def revise_plan(self, state: AgentState, evaluator_feedback: Dict[str, Any]) -> AgentState:
        """Revise plan based on evaluator feedback"""
        
        # Increment revision count
        state["revision_count"] = state.get("revision_count", 0) + 1
        
        if state["revision_count"] > settings.MAX_REVISION_LOOPS:
            state["errors"].append({
                "agent": "planner",
                "error": f"Max revision loops ({settings.MAX_REVISION_LOOPS}) exceeded",
                "fatal": True,
                "timestamp": datetime.utcnow().isoformat()
            })
            state["should_continue"] = False
            return state
        
        # Get failed tasks from evaluator feedback
        failed_criteria = evaluator_feedback.get("failed_criteria", [])
        issues = evaluator_feedback.get("issues", [])
        
        # Add revision tasks to graph
        task_graph = state.get("task_graph")
        if task_graph:
            revision_idx = len(task_graph.nodes)
            
            for i, criterion in enumerate(failed_criteria):
                task_id = f"revision_{revision_idx}_{i}"
                task_graph.nodes[task_id] = TaskNode(
                    task_id=task_id,
                    agent_type=AgentType.RISK_DISPATCH,
                    input_data={"task": "revision", "criterion": criterion, "issues": issues},
                    dependencies=[list(task_graph.nodes.keys())[-1]] if task_graph.nodes else [],
                    retry_policy={"max_retries": 1, "backoff": "exponential", "fallback_agent": None}
                )
            
            task_graph.updated_at = datetime.utcnow()
        
        state["next_agent"] = AgentType.RISK_DISPATCH
        return state


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.PLANNER, PlannerAgent())