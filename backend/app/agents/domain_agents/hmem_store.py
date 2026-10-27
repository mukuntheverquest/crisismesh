"""
CrisisMesh H-Mem Store Agent - Open Agent Hackathon 2026
Long-term memory for SOPs, cross-jurisdictional protocols, and institutional knowledge
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from uuid import uuid4

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, SOPRecord
from app.config import settings


@dataclass
class HMemEntry:
    """Long-term memory entry"""
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    category: str = ""  # sop, protocol, lesson_learned, asset_spec, contact
    content: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0


class HMemStoreAgent(BaseAgent):
    """H-Mem long-term memory store for cross-jurisdictional SOPs and institutional knowledge"""
    
    def __init__(self):
        super().__init__(AgentType.HMEM_STORE)
        self.memory: Dict[str, HMemEntry] = {}
        self._initialize_base_memory()
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.HMEM_STORE
    
    def _initialize_base_memory(self):
        """Initialize with base SOPs and protocols"""
        
        # Cross-jurisdictional Flood SOP (Failure #3)
        self.store(HMemEntry(
            category="sop",
            content={
                "sop_id": "sop_flood_red_alert",
                "title": "Flash Flood Red Alert - Joint National-Regional Mobilization",
                "version": "1.2",
                "trigger_conditions": {
                    "alert_level": "red",
                    "source": ["AEMET", "NWS", "DHM"],
                    "upstream_surge": True,
                    "river_gauge_threshold_exceeded": True
                },
                "required_actions": [
                    {"action": "notify_national_eme", "agency": "UME", "timeline_minutes": 0, "authority": "pre-authorized"},
                    {"action": "notify_regional_gov", "agency": "Regional", "timeline_minutes": 0, "authority": "pre-authorized"},
                    {"action": "dispatch_alerts", "systems": ["IPAWS", "ES-Alert", "Genasys"], "timeline_minutes": 5},
                    {"action": "prioritize_vulnerable", "demographics": ["elderly_ground_floor", "schools", "underground_parking"], "timeline_minutes": 10},
                    {"action": "mobilize_assets", "types": ["helicopter", "shallow_draft_boat", "high_water_vehicle"], "timeline_minutes": 15}
                ],
                "cross_jurisdictional": True,
                "priority_demographics": ["elderly_ground_floor", "schools", "underground_parking"],
                "legal_basis": "Pre-authorized emergency powers / Civil Protection Law",
                "last_exercised": "2024-10-29",  # Valencia DANA
                "lessons_learned": [
                    "Regional-national jurisdictional gap caused 12-hour delay in Valencia",
                    "University/Embassy warnings preceded official alerts",
                    "Ground-floor elderly most at risk"
                ]
            },
            tags=["flood", "red_alert", "cross_jurisdictional", "valencia", "dana"],
            source="Valencia DANA 2024 After-Action Report"
        ))
        
        # Wildfire Wind Shift SOP (Failure #2)
        self.store(HMemEntry(
            category="sop",
            content={
                "sop_id": "sop_wildfire_wind_shift",
                "title": "Wildfire Wind Shift - Polygon Auto-Expansion & Multilingual Alerts",
                "version": "1.0",
                "trigger_conditions": {
                    "wind_shift_degrees": ">30",
                    "wind_speed_kmh": ">20",
                    "fire_perimeter_growth_rate": ">500_m_per_hour"
                },
                "required_actions": [
                    {"action": "auto_expand_polygon", "factor": 1.5, "direction": "downwind", "timeline_minutes": 0},
                    {"action": "dispatch_multilingual_alerts", "languages": ["en", "es", "zh", "vi", "ko"], "timeline_minutes": 2},
                    {"action": "verify_polygon_bounds", "max_area_multiplier": 5, "timeline_minutes": 1},
                    {"action": "reassign_operator_load", "max_concurrent_fires_per_operator": 1, "timeline_minutes": 5}
                ],
                "cross_jurisdictional": False,
                "priority_demographics": ["tourists", "non-english_speakers", "rural_communities"],
                "legal_basis": "Fire Emergency Powers / Public Alert Act",
                "last_exercised": "2025-01-08",  # LA Wildfires
                "lessons_learned": [
                    "Single operator managing 3 fires caused alert delays",
                    "County-wide blast eroded trust (10M false alarms)",
                    "West Altadena received zero alerts until 3:30 AM - 17 deaths"
                ]
            },
            tags=["wildfire", "wind_shift", "polygon_expansion", "multilingual", "la_wildfires"],
            source="LA Wildfires 2025 After-Action Report"
        ))
        
        # Dam Failure Contradiction Protocol (Failure #6)
        self.store(HMemEntry(
            category="sop",
            content={
                "sop_id": "sop_dam_failure_contradiction",
                "title": "Dam Failure - Contradiction Detection & Precautionary Override",
                "version": "1.1",
                "trigger_conditions": {
                    "structural_risk": "critical",
                    "conflicting_messages_detected": True,
                    "inundation_zone_populated": True
                },
                "required_actions": [
                    {"action": "block_contradictory_messages", "types": ["curfew", "shelter_in_place", "all_clear"], "timeline_minutes": 0},
                    {"action": "enforce_high_ground_evacuation", "timeline_minutes": 0},
                    {"action": "notify_national_military", "agency": "UME/Engineering Corps", "timeline_minutes": 0},
                    {"action": "override_local_authority", "basis": "pre-authorized emergency powers", "timeline_minutes": 0}
                ],
                "cross_jurisdictional": True,
                "priority_demographics": ["downstream_communities", "underground_parking", "low_lying_areas"],
                "legal_basis": "Dam Safety Act / Emergency Powers / Pre-authorized Override",
                "last_exercised": "2023-09-11",  # Derna
                "lessons_learned": [
                    "Authorities issued curfew then evacuation 19 min after collapse",
                    "Water Ministry reassured 'good condition' while dams failing",
                    "4,352+ deaths from contradictory messaging"
                ]
            },
            tags=["dam_failure", "contradiction", "precautionary_override", "derna"],
            source="Derna Dam Collapse 2023 Investigation"
        ))
        
        # Rock-Ice Avalanche Multi-Modal Inference (Failure #4)
        self.store(HMemEntry(
            category="sop",
            content={
                "sop_id": "sop_rock_ice_avalanche_inference",
                "title": "Rock-Ice Avalanche - Multi-Modal Hazard Inference",
                "version": "1.0",
                "trigger_conditions": {
                    "correlated_signals": ["sensor_dropout", "seismic_tremor", "observer_calls"],
                    "min_active_signals": 2,
                    "canyon_topography": True
                },
                "required_actions": [
                    {"action": "infer_hazard_from_correlation", "confidence_threshold": 0.75, "timeline_minutes": 0},
                    {"action": "calculate_canyon_arrival_etas", "speed_kmh": 160, "timeline_minutes": 1},
                    {"action": "dispatch_immediate_alerts", "bypass_normal_approval": True, "timeline_minutes": 2},
                    {"action": "activate_evacuation_routes", "prioritize_downstream": True, "timeline_minutes": 5}
                ],
                "cross_jurisdictional": False,
                "priority_demographics": ["downstream_settlements", "trekking_routes", "hydropower_workers"],
                "legal_basis": "Glacial Hazard Protocol / Emergency Telecommunications",
                "last_exercised": "2026-08-26",  # Nepal Bhote Koshi
                "lessons_learned": [
                    "Gauges destroyed in 7 minutes - single modality blindness",
                    "DHM relied on monsoon thresholds, missed clear-day avalanche",
                    "Phone call was first notification - 19 min before SMS arrived with flood"
                ]
            },
            tags=["rock_ice_avalanche", "multi_modal", "sensor_dropout", "nepal", "bhote_koshi"],
            source="Nepal Bhote Koshi 2026 Investigation"
        ))
        
        # Multi-Agency Registry Deduplication (Failure #5)
        self.store(HMemEntry(
            category="protocol",
            content={
                "protocol_id": "proto_survivor_registry_dedup",
                "title": "Survivor Registry Multi-Source Deduplication",
                "version": "1.0",
                "sources": ["army_pdf", "family_tracing_api", "internal_log", "ngo_report", "red_cross"],
                "process": [
                    "Ingest all sources via Zetaris USL",
                    "GPU-accelerated entity resolution (CUDA sentence-transformers)",
                    "Confidence threshold: 0.85",
                    "Provenance tracking for each match",
                    "Output unified registry with source attribution"
                ],
                "performance": {
                    "records_per_second": 5000,
                    "gpu_utilization": "85%",
                    "deduplication_rate": "92%"
                },
                "last_used": "2026-08",  # Nepal Floods
                "lessons_learned": [
                    "Three incompatible 'rescued' figures published simultaneously",
                    "Civic developer manually converted PDFs at 1-2 AM",
                    "13,013 vs 4,898 vs 7,514 - no single source of truth"
                ]
            },
            tags=["registry", "deduplication", "survivor", "multi_agency", "nepal"],
            source="Nepal Floods 2026 Civic Tech Report"
        ))
        
        # Social Media Verification Protocol (Failure #9)
        self.store(HMemEntry(
            category="protocol",
            content={
                "protocol_id": "proto_social_media_verification",
                "title": "Satellite-Grounded Social Media Distress Verification",
                "version": "1.0",
                "process": [
                    "Extract [PER, CITY, ADDR, STATUS] via GPU NLP",
                    "Spatial join against Sentinel-1 SAR / HOTOSM fAIr damage footprints",
                    "Filter: destroyed/major_damage confidence >= 0.75",
                    "Reject geocoded pins in wrong city (>4% hallucination rate)",
                    "Prioritize verified distress for response"
                ],
                "performance": {
                    "tweets_per_hour": 150000,
                    "geocoding_hallucination_filter": "4% wrong city removed",
                    "mdeberta_f1_addr": 0.7113
                },
                "last_used": "2023-02",  # Türkiye-Syria
                "lessons_learned": [
                    "1.8M tweets in 12 hours overwhelmed manual triage",
                    "~4% geocoded pins landed in wrong city",
                    "SAR grounding essential for verification"
                ]
            },
            tags=["social_media", "verification", "satellite", "geocoding", "turkey_syria"],
            source="Türkiye-Syria Earthquake 2023 NLP Analysis"
        ))
        
        # Capability-Matched Asset Dispatch (Failure #10)
        self.store(HMemEntry(
            category="asset_spec",
            content={
                "spec_id": "asset_capability_matching",
                "title": "Capability-Matched Asset Dispatch for Specialized Hazards",
                "version": "1.0",
                "hazard_asset_map": {
                    "subterranean_tunnel_flood": ["tunnel_rescue_team", "heavy_lift_drone", "lidar_thermal_drone", "breaching_equipment"],
                    "pancake_collapse": ["dmat_team", "engineering_team", "lidar_thermal_drone", "heavy_lift_drone"],
                    "isolated_elderly_shelter": ["shallow_draft_boat", "vhf_radio", "siren_system", "community_health_worker"],
                    "rock_ice_avalanche": ["helicopter", "drone", "sar_dog_team"],
                    "flash_flood": ["shallow_draft_boat", "helicopter", "high_water_vehicle"],
                    "wildfire": ["lidar_thermal_drone", "helicopter", "fire_engine_strike_team"]
                },
                "pre_accredited_ngos": [
                    "Robotics Association of Nepal (LiDAR/thermal drones)",
                    "Red Cross/Red Crescent (DMAT, shelter)",
                    "Engineers Without Borders (structural assessment)",
                    "International Tunnel Rescue Consortium"
                ],
                "drone_requirements": {
                    "min_count": 3,
                    "required_capabilities": ["lidar", "thermal", "night_ops"],
                    "heavy_lift_min_payload_kg": 50
                },
                "lessons_learned": [
                    "500 workers trapped in tunnels, only 4-5 heavy-lift drones nationwide",
                    "Soldiers used smartphone flashlights - no subterranean gear",
                    "AFAD lacked accredited NGO registry, ignored engineering associations"
                ]
            },
            tags=["asset_dispatch", "capability_matching", "tunnel", "drone", "ngo"],
            source="Nepal Floods 2026 & Türkiye 2023 Reports"
        ))
    
    def store(self, entry: HMemEntry) -> str:
        """Store entry in H-Mem"""
        self.memory[entry.entry_id] = entry
        return entry.entry_id
    
    def retrieve(self, entry_id: str) -> Optional[HMemEntry]:
        """Retrieve entry by ID"""
        entry = self.memory.get(entry_id)
        if entry:
            entry.access_count += 1
            entry.updated_at = datetime.utcnow()
        return entry
    
    def query(self, category: str = None, tags: List[str] = None, 
              min_confidence: float = 0.0) -> List[HMemEntry]:
        """Query H-Mem with filters"""
        results = []
        for entry in self.memory.values():
            if category and entry.category != category:
                continue
            if tags and not any(t in entry.tags for t in tags):
                continue
            if entry.confidence < min_confidence:
                continue
            results.append(entry)
        return results
    
    @trace_agent("hmem_store", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Execute H-Mem store tasks"""
        
        task_graph = state.get("task_graph")
        current_task_id = state.get("current_task_id")
        
        if not task_graph or not current_task_id:
            current_task_id = self._find_next_hmem_task(task_graph)
            state["current_task_id"] = current_task_id
        
        if not current_task_id:
            state["next_agent"] = AgentType.EVALUATOR
            return state
        
        task = task_graph.nodes.get(current_task_id)
        if not task:
            state["next_agent"] = AgentType.EVALUATOR
            return state
        
        task_input = task.input_data
        task_type = task_input.get("task", "")
        
        result = None
        try:
            if task_type == "retrieve_cross_jurisdictional_sops":
                result = await self._retrieve_cross_jurisdictional_sops(state, task_input)
            elif task_type == "store_lesson_learned":
                result = await self._store_lesson_learned(state, task_input)
            elif task_type == "query_protocol":
                result = await self._query_protocol(state, task_input)
            else:
                result = {"status": "unknown_task", "task": task_type}
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.attempts += 1
            state = self._add_error(state, f"H-Mem task {task_type} failed: {e}")
        
        state["hmem_store_output"] = result
        state["next_agent"] = AgentType.EVALUATOR
        state = self._update_state_trace(state, result or {})
        
        return state
    
    def _find_next_hmem_task(self, task_graph: Optional[Any]) -> Optional[str]:
        if not task_graph:
            return None
        
        for task_id, task in task_graph.nodes.items():
            if (task.agent_type == AgentType.HMEM_STORE and 
                task.status == "pending"):
                deps_met = all(
                    task_graph.nodes[dep_id].status == "completed"
                    for dep_id in task.dependencies
                    if dep_id in task_graph.nodes
                )
                if deps_met:
                    return task_id
        return None
    
    @trace_tool_call("hmem_store", "retrieve_cross_jurisdictional_sops")
    async def _retrieve_cross_jurisdictional_sops(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Retrieve SOPs for current disaster context (Failure #3)"""
        
        trigger = task_input.get("trigger", "")
        disaster_type = state.get("context", {}).get("disaster_type", "")
        severity = state.get("context", {}).get("severity", "")
        
        # Query for relevant SOPs
        tags = [disaster_type, severity] if disaster_type and severity else []
        sops = self.query(category="sop", tags=tags, min_confidence=0.8)
        
        # Also get protocols
        protocols = self.query(category="protocol", tags=tags, min_confidence=0.8)
        
        # Filter for cross-jurisdictional
        cross_jurisdictional = [s for s in sops if s.content.get("cross_jurisdictional", False)]
        
        # Format for output
        sop_outputs = []
        for sop in sops:
            sop_outputs.append({
                "sop_id": sop.content.get("sop_id"),
                "title": sop.content.get("title"),
                "version": sop.content.get("version"),
                "trigger_conditions": sop.content.get("trigger_conditions"),
                "required_actions": sop.content.get("required_actions"),
                "cross_jurisdictional": sop.content.get("cross_jurisdictional"),
                "priority_demographics": sop.content.get("priority_demographics"),
                "legal_basis": sop.content.get("legal_basis"),
                "lessons_learned": sop.content.get("lessons_learned"),
                "executed": False  # Will be marked by risk dispatch
            })
        
        return {
            "task": "retrieve_cross_jurisdictional_sops",
            "trigger": trigger,
            "disaster_type": disaster_type,
            "severity": severity,
            "sops_retrieved": sop_outputs,
            "cross_jurisdictional_count": len(cross_jurisdictional),
            "total_sops": len(sops),
            "protocols_available": len(protocols),
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("hmem_store", "store_lesson_learned")
    async def _store_lesson_learned(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Store new lesson learned from current operation"""
        
        lesson = task_input.get("lesson", {})
        category = task_input.get("category", "lesson_learned")
        
        entry = HMemEntry(
            category=category,
            content=lesson,
            tags=task_input.get("tags", []),
            source=task_input.get("source", "crisismesh_operation"),
            confidence=task_input.get("confidence", 0.9)
        )
        
        entry_id = self.store(entry)
        
        return {
            "task": "store_lesson_learned",
            "entry_id": entry_id,
            "category": category,
            "stored_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("hmem_store", "query_protocol")
    async def _query_protocol(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Query specific protocol"""
        
        protocol_id = task_input.get("protocol_id", "")
        tags = task_input.get("tags", [])
        
        if protocol_id:
            # Find by ID in content
            for entry in self.memory.values():
                if entry.content.get("protocol_id") == protocol_id or entry.content.get("sop_id") == protocol_id:
                    return {
                        "task": "query_protocol",
                        "found": True,
                        "protocol": {
                            "entry_id": entry.entry_id,
                            "content": entry.content,
                            "tags": entry.tags,
                            "source": entry.source,
                            "confidence": entry.confidence
                        }
                    }
            return {"task": "query_protocol", "found": False, "protocol_id": protocol_id}
        
        # Query by tags
        protocols = self.query(category="protocol", tags=tags)
        sops = self.query(category="sop", tags=tags)
        
        return {
            "task": "query_protocol",
            "tags": tags,
            "protocols_found": len(protocols),
            "sops_found": len(sops),
            "results": [
                {"entry_id": e.entry_id, "content": e.content, "tags": e.tags}
                for e in protocols + sops
            ]
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.HMEM_STORE, HMemStoreAgent())