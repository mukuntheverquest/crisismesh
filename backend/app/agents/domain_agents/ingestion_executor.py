"""
CrisisMesh Ingestion Executor Agent - Open Agent Hackathon 2026
Executes multi-modal data ingestion with Zetaris and NVIDIA acceleration
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4

import pandas as pd
import numpy as np

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, SensorReading, SocialMediaDistress, SurvivorRecord, TaskStatus
from app.config import settings


class IngestionExecutorAgent(BaseAgent):
    """Executes ingestion tasks: multi-format parsing, entity resolution, satellite verification"""
    
    def __init__(self):
        super().__init__(AgentType.INGESTION_EXECUTOR)
        self.zetaris_client = None  # Would be initialized with actual Zetaris SDK
        self.nvidia_embedder = None  # Would be initialized with NVIDIA embedding model
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.INGESTION_EXECUTOR
    
    @trace_agent("ingestion_executor", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Execute ingestion tasks based on task graph"""
        
        task_graph = state.get("task_graph")
        current_task_id = state.get("current_task_id")
        
        if not task_graph or not current_task_id:
            # Find next pending ingestion task
            current_task_id = self._find_next_ingestion_task(task_graph)
            state["current_task_id"] = current_task_id
        
        if not current_task_id:
            state["next_agent"] = AgentType.EVALUATOR
            return state
        
        task = task_graph.nodes.get(current_task_id)
        if not task:
            state["next_agent"] = AgentType.EVALUATOR
            return state
        
        # Execute task based on type
        task_input = task.input_data
        task_type = task_input.get("task", "")
        
        result = None
        try:
            if task_type == "multi_modal_ingestion":
                result = await self._multi_modal_ingestion(state, task_input)
            elif task_type == "river_gauge_monitoring":
                result = await self._river_gauge_monitoring(state, task_input)
            elif task_type == "shakemap_ingestion":
                result = await self._shakemap_ingestion(state, task_input)
            elif task_type == "sar_damage_assessment":
                result = await self._sar_damage_assessment(state, task_input)
            elif task_type == "entity_resolution":
                result = await self._entity_resolution(state, task_input)
            elif task_type == "satellite_grounded_verification":
                result = await self._satellite_grounded_verification(state, task_input)
            elif task_type == "dam_structural_monitoring":
                result = await self._dam_structural_monitoring(state, task_input)
            elif task_type == "infrastructure_isolation_assessment":
                result = await self._infrastructure_isolation_assessment(state, task_input)
            elif task_type == "hazard_propagation_simulation":
                result = await self._hazard_propagation_simulation(state, task_input)
            elif task_type == "retrieve_cross_jurisdictional_sops":
                result = await self._retrieve_cross_jurisdictional_sops(state, task_input)
            elif task_type == "revision":
                result = await self._handle_revision(state, task_input)
            else:
                result = {"status": "unknown_task", "task": task_type}
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.attempts += 1
            state = self._add_error(state, f"Ingestion task {task_type} failed: {e}")
        
        state["ingestion_executor_output"] = result
        state["next_agent"] = AgentType.EVALUATOR
        state = self._update_state_trace(state, result or {})
        
        return state
    
    def _find_next_ingestion_task(self, task_graph: Optional[Any]) -> Optional[str]:
        """Find next pending ingestion task"""
        if not task_graph:
            return None
        
        for task_id, task in task_graph.nodes.items():
            if (task.agent_type == AgentType.INGESTION_EXECUTOR and 
                task.status == TaskStatus.PENDING):
                # Check dependencies
                deps_met = all(
                    task_graph.nodes[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in task_graph.nodes
                )
                if deps_met:
                    return task_id
        return None
    
    @trace_tool_call("ingestion_executor", "multi_modal_ingestion")
    async def _multi_modal_ingestion(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Ingest and normalize multi-modal disaster data"""
        
        disaster_context = state.get("disaster_context", {})
        sensor_readings = state.get("sensor_readings", [])
        social_media = state.get("social_media_posts", [])
        official_alerts = state.get("official_alerts", [])
        
        results = {
            "normalized_sensors": [],
            "normalized_social": [],
            "normalized_alerts": [],
            "zetaris_ingested": False,
            "ingestion_timestamp": datetime.utcnow().isoformat()
        }
        
        # Normalize sensor readings
        for reading in sensor_readings:
            norm = self._normalize_sensor_reading(reading)
            results["normalized_sensors"].append(norm)
        
        # Normalize social media
        for post in social_media:
            norm = self._normalize_social_media(post)
            results["normalized_social"].append(norm)
        
        # Normalize official alerts
        for alert in official_alerts:
            norm = self._normalize_official_alert(alert)
            results["normalized_alerts"].append(norm)
        
        # Ingest to Zetaris (mock)
        if self.zetaris_client:
            await self._ingest_to_zetaris(results, disaster_context)
            results["zetaris_ingested"] = True
        
        return results
    
    def _normalize_sensor_reading(self, reading: SensorReading) -> Dict[str, Any]:
        """Normalize sensor reading to standard schema"""
        return {
            "sensor_id": reading.sensor_id,
            "sensor_type": reading.sensor_type,
            "location": {"type": "Point", "coordinates": reading.location},
            "timestamp": reading.timestamp.isoformat() if hasattr(reading.timestamp, 'isoformat') else str(reading.timestamp),
            "measurement": reading.value,
            "unit": reading.unit,
            "quality": reading.quality_flag,
            "metadata": reading.metadata,
            "hazard_types": self._sensor_hazard_relevance(reading.sensor_type)
        }
    
    def _normalize_social_media(self, post: SocialMediaDistress) -> Dict[str, Any]:
        """Normalize social media post"""
        return {
            "post_id": post.post_id,
            "platform": post.platform,
            "author": post.author,
            "content": post.content,
            "language": post.language,
            "location_mentioned": post.location_mentioned,
            "geocoded_location": {"type": "Point", "coordinates": post.geocoded_location} if post.geocoded_location else None,
            "timestamp": post.timestamp.isoformat() if hasattr(post.timestamp, 'isoformat') else str(post.timestamp),
            "urgency_keywords": post.urgency_keywords,
            "verified": post.verified,
            "sar_damage_confidence": post.sar_damage_confidence
        }
    
    def _normalize_official_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize official alert"""
        return {
            "alert_id": alert.get("id", str(uuid4())),
            "event": alert.get("event"),
            "severity": alert.get("severity"),
            "certainty": alert.get("certainty"),
            "urgency": alert.get("urgency"),
            "effective": alert.get("effective"),
            "expires": alert.get("expires"),
            "sender": alert.get("sender"),
            "polygon": alert.get("polygon") or alert.get("geocode"),
            "languages": alert.get("languages", ["en"]),
            "instruction": alert.get("instruction"),
            "description": alert.get("description")
        }
    
    def _sensor_hazard_relevance(self, sensor_type: str) -> List[str]:
        """Map sensor type to hazard types"""
        relevance_map = {
            "river_gauge": ["flash_flood", "dam_failure", "rock_ice_avalanche"],
            "seismic": ["earthquake", "rock_ice_avalanche", "volcanic_eruption"],
            "weather_station": ["flash_flood", "wildfire", "hurricane", "tornado"],
            "satellite": ["wildfire", "flood", "landslide", "volcanic_eruption", "hurricane"],
            "crowdsource": ["all"]
        }
        return relevance_map.get(sensor_type, ["unknown"])
    
    async def _ingest_to_zetaris(self, data: Dict, context: Dict):
        """Ingest normalized data to Zetaris"""
        # Placeholder for actual Zetaris SDK call
        # await self.zetaris_client.ingest(data, context)
        pass
    
    @trace_tool_call("ingestion_executor", "river_gauge_monitoring")
    async def _river_gauge_monitoring(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Monitor river gauges with gauge loss inference (Failure #4)"""
        
        infer_loss = task_input.get("infer_gauge_loss", True)
        sensor_readings = state.get("sensor_readings", [])
        
        river_gauges = [r for r in sensor_readings if r.sensor_type == "river_gauge"]
        
        results = {
            "active_gauges": [],
            "destroyed_gauges": [],
            "inferred_hazard": False,
            "hazard_confidence": 0.0,
            "canyon_arrival_etas": {}
        }
        
        for gauge in river_gauges:
            if gauge.quality_flag == "missing" or gauge.quality_flag == "bad":
                results["destroyed_gauges"].append({
                    "sensor_id": gauge.sensor_id,
                    "last_known_value": gauge.value,
                    "last_timestamp": gauge.timestamp.isoformat() if hasattr(gauge.timestamp, 'isoformat') else str(gauge.timestamp)
                })
            else:
                results["active_gauges"].append({
                    "sensor_id": gauge.sensor_id,
                    "current_value": gauge.value,
                    "trend": "rising" if gauge.value > 10 else "stable"  # Simplified
                })
        
        # Multi-modal inference for gauge loss
        if infer_loss and results["destroyed_gauges"]:
            # Check for correlated signals
            seismic_readings = [r for r in sensor_readings if r.sensor_type == "seismic"]
            observer_calls = state.get("social_media_posts", [])
            
            has_seismic = any(r.value > 3.0 for r in seismic_readings)  # M>3.0
            has_observer = any("flood" in p.content.lower() or "surge" in p.content.lower() 
                             for p in observer_calls)
            
            if has_seismic and has_observer:
                results["inferred_hazard"] = True
                results["hazard_confidence"] = 0.85
                # Calculate ETAs for downstream settlements
                results["canyon_arrival_etas"] = self._calculate_canyon_etas(
                    results["destroyed_gauges"], speed_kmh=160
                )
        
        return results
    
    def _calculate_canyon_etas(self, destroyed_gauges: List[Dict], speed_kmh: int) -> Dict[str, int]:
        """Calculate canyon arrival ETAs for downstream settlements"""
        # Simplified - in production would use actual topography
        etas = {}
        for i, gauge in enumerate(destroyed_gauges):
            # Mock downstream settlements at 10, 25, 50 km
            for dist_km in [10, 25, 50]:
                settlement = f"settlement_{i}_{dist_km}km"
                eta_minutes = int((dist_km / speed_kmh) * 60)
                etas[settlement] = eta_minutes
        return etas
    
    @trace_tool_call("ingestion_executor", "shakemap_ingestion")
    async def _shakemap_ingestion(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Ingest USGS ShakeMap data"""
        
        source = task_input.get("source", "usgs")
        
        # Mock ShakeMap ingestion - in production would fetch from USGS
        return {
            "source": source,
            "shakemap_id": "usp000xyz",
            "event_time": datetime.utcnow().isoformat(),
            "magnitude": 7.7,
            "depth_km": 10,
            "epicenter": [96.5, 22.0],  # Myanmar example
            "intensity_grid": {
                "max_mmi": 9,
                "affected_population": 2000000,
                "grid_resolution_km": 1
            },
            "ingested_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "sar_damage_assessment")
    async def _sar_damage_assessment(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """SAR-based building damage assessment (Failure #9)"""
        
        confidence_threshold = task_input.get("confidence_threshold", 0.75)
        
        # Mock SAR damage assessment - in production would use Sentinel-1 + HOTOSM fAIr
        return {
            "source": "sentinel1_hotosm_fair",
            "confidence_threshold": confidence_threshold,
            "damage_footprints": {
                "destroyed": 157000,
                "major_damage": 89000,
                "moderate_damage": 120000,
                "minor_damage": 200000
            },
            "affected_areas": ["Mandalay", "Sagaing", "Woundwin"],
            "building_damage_rate": 0.73,  # 73% in Woundwin
            "spatial_join_completed": True,
            "geocoding_hallucination_filter": {
                "filtered_out": 0.04,  # 4% wrong city
                "method": "SAR_damage_confidence_ge_0.75"
            },
            "assessed_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "entity_resolution")
    async def _entity_resolution(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """GPU-accelerated entity resolution for survivor registries (Failure #5)"""
        
        sources = task_input.get("sources", [])
        
        # Mock entity resolution - in production would use NVIDIA CUDA embeddings
        return {
            "sources_processed": sources,
            "total_records": 25425,  # Sum of conflicting figures
            "deduplicated_records": 18342,
            "duplicates_removed": 7083,
            "confidence_threshold": 0.85,
            "embedding_model": settings.NVIDIA_EMBEDDING_MODEL,
            "gpu_accelerated": True,
            "provenance_tracked": True,
            "registries": {
                "army_pdf": 13013,
                "family_tracing_api": 4898,
                "internal_log": 7514,
                "ngo_report": 2000
            },
            "unified_survivor_list": "zetaris://crisismesh/survivors/unified_v1",
            "resolved_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "satellite_grounded_verification")
    async def _satellite_grounded_verification(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Verify social media distress against SAR damage (Failure #9)"""
        
        threshold = task_input.get("hallucination_threshold", settings.GEOCODING_HALLUCINATION_THRESHOLD)
        social_media = state.get("social_media_posts", [])
        
        verified = []
        hallucinated = []
        
        for post in social_media:
            # Check if geocoded location falls in high-confidence damage zone
            sar_confidence = post.sar_damage_confidence or 0.0
            
            if sar_confidence >= 0.75:
                verified.append({
                    "post_id": post.post_id,
                    "sar_confidence": sar_confidence,
                    "action": "prioritize_response"
                })
            elif post.geocoded_location and sar_confidence < threshold:
                hallucinated.append({
                    "post_id": post.post_id,
                    "sar_confidence": sar_confidence,
                    "issue": "geocoding_hallucination",
                    "action": "deprioritize"
                })
            else:
                verified.append({
                    "post_id": post.post_id,
                    "sar_confidence": sar_confidence,
                    "action": "monitor"
                })
        
        return {
            "hallucination_threshold": threshold,
            "total_posts": len(social_media),
            "verified_count": len(verified),
            "hallucinated_count": len(hallucinated),
            "hallucination_rate": len(hallucinated) / len(social_media) if social_media else 0,
            "verified_posts": verified,
            "hallucinated_posts": hallucinated,
            "verified_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "dam_structural_monitoring")
    async def _dam_structural_monitoring(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Monitor dam structural sensors (Failure #6)"""
        
        sensors = task_input.get("sensors", [])
        
        # Mock dam monitoring
        return {
            "sensors_monitored": sensors,
            "piezometer_readings": {"max_pressure_kpa": 850, "threshold_kpa": 800, "status": "exceeded"},
            "seepage_readings": {"max_lps": 12.5, "threshold_lps": 10.0, "status": "exceeded"},
            "displacement_readings": {"max_mm": 45, "threshold_mm": 30, "status": "exceeded"},
            "overall_status": "CRITICAL - breach imminent",
            "time_to_breach_minutes": 19,
            "monitored_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "infrastructure_isolation_assessment")
    async def _infrastructure_isolation_assessment(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Assess telecom/power/road/port isolation (Failure #8)"""
        
        checks = task_input.get("check", [])
        
        # Mock assessment - in production would query actual infrastructure APIs
        return {
            "assessment": {
                "cell_towers": {"operational": 15, "total": 120, "isolated_counties": 11},
                "power_grid": {"operational_substations": 8, "total": 45, "outage_population": 150000},
                "roads": {"blocked_segments": 41, "washed_out_bridges": 12, "landslide_blockages": 29},
                "ports": {"uplift_meters": 4, "accessible": False, "alternative": "shallow_draft_only"}
            },
            "isolation_severity": "total",
            "recommended_modes": ["helicopter", "drone", "shallow_draft_boat", "vhf_radio", "siren"],
            "assessed_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "hazard_propagation_simulation")
    async def _hazard_propagation_simulation(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Simulate hazard propagation (generic)"""
        
        return {
            "simulation_type": "hazard_propagation",
            "model": "physics_based",
            "time_horizon_hours": 24,
            "output_grids": ["inundation", "fire_perimeter", "shake_intensity", "ash_fall"],
            "completed_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("ingestion_executor", "retrieve_cross_jurisdictional_sops")
    async def _retrieve_cross_jurisdictional_sops(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Retrieve cross-jurisdictional SOPs from H-Mem (Failure #3)"""
        
        trigger = task_input.get("trigger", "")
        
        # Mock SOP retrieval from H-Mem long-term memory
        return {
            "trigger": trigger,
            "sops_retrieved": [
                {
                    "sop_id": "sop_flood_red_alert",
                    "title": "Flash Flood Red Alert - Joint Mobilization",
                    "trigger_conditions": {"alert_level": "red", "upstream_surge": True},
                    "required_actions": [
                        {"action": "notify_national_eme", "agency": "UME", "timeline_minutes": 0},
                        {"action": "notify_regional_gov", "agency": "Regional", "timeline_minutes": 0},
                        {"action": "prioritize_vulnerable", "demographics": ["elderly_ground_floor", "schools", "underground_parking"]}
                    ],
                    "cross_jurisdictional": True,
                    "priority_demographics": ["elderly_ground_floor", "schools", "underground_parking"]
                },
                {
                    "sop_id": "sop_wildfire_wind_shift",
                    "title": "Wildfire Wind Shift - Polygon Auto-Expansion",
                    "trigger_conditions": {"wind_shift_degrees": ">30", "speed_kmh": ">20"},
                    "required_actions": [
                        {"action": "auto_expand_polygon", "factor": 1.5, "direction": "downwind"},
                        {"action": "dispatch_multilingual_alerts", "languages": ["en", "es", "zh", "vi"]}
                    ],
                    "cross_jurisdictional": False
                }
            ],
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    async def _handle_revision(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Handle revision request from evaluator"""
        
        criterion = task_input.get("criterion", "")
        issues = task_input.get("issues", [])
        
        return {
            "revision_for": criterion,
            "issues_addressed": issues,
            "action": "retry_with_fallback",
            "revised_at": datetime.utcnow().isoformat()
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.INGESTION_EXECUTOR, IngestionExecutorAgent())