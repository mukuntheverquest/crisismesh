"""
CrisisMesh Risk Dispatch Agent - Open Agent Hackathon 2026
Handles alert dispatch, asset dispatch, evacuation routing, and multilingual alerts
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import (
    AgentState, AgentType, AlertPolygon, AssetRecord, AssetType,
    DisasterType, SeverityLevel, AlertStatus, SensorReading, TaskStatus
)
from app.config import settings


class RiskDispatchAgent(BaseAgent):
    """Dispatches alerts, assets, and evacuation orders with risk-aware decisions"""
    
    def __init__(self):
        super().__init__(AgentType.RISK_DISPATCH)
        self.asset_catalog: List[AssetRecord] = []
        self._initialize_asset_catalog()
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.RISK_DISPATCH
    
    def _initialize_asset_catalog(self):
        """Initialize mock asset catalog (in production: load from Zetaris)"""
        self.asset_catalog = [
            AssetRecord(
                asset_id="heli_001",
                asset_type=AssetType.HELICOPTER,
                operator="National Air Force",
                capabilities=["hoist", "night_vision", "water_bucket"],
                location=[96.1, 21.9],
                status="available",
                specialization=["wildfire", "flood_rescue", "earthquake"],
                contact_info={"radio": "HELI-001", "phone": "+1-555-0100"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="drone_lidar_001",
                asset_type=AssetType.LI_DAR_THERMAL_DRONE,
                operator="Robotics Association of Nepal",
                capabilities=["lidar", "thermal", "3d_mapping", "night_ops"],
                location=[85.3, 27.7],
                status="available",
                specialization=["earthquake", "landslide", "tunnel_flood"],
                contact_info={"radio": "DRONE-LIDAR-01", "phone": "+977-1-555-0200"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="boat_shallow_001",
                asset_type=AssetType.SHALLOW_DRAFT_BOAT,
                operator="Inland Waterways Authority",
                capabilities=["shallow_water", "patient_transport", "supply_delivery"],
                location=[88.4, 22.6],
                status="available",
                specialization=["flash_flood", "riverine_flood"],
                contact_info={"radio": "BOAT-001", "phone": "+91-555-0300"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="tunnel_rescue_001",
                asset_type=AssetType.TUNNEL_RESCUE_TEAM,
                operator="Nepali Army Engineering Corps",
                capabilities=["breaching", "ventilation", "rope_rescue", "confined_space"],
                location=[85.1, 27.9],
                status="available",
                specialization=["tunnel_flood", "subterranean_rescue"],
                contact_info={"radio": "TUNNEL-01", "phone": "+977-1-555-0400"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="dmat_001",
                asset_type=AssetType.DMAT_TEAM,
                operator="Ministry of Health",
                capabilities=["trauma_care", "infectious_control", "mass_casualty", "field_hospital"],
                location=[85.3, 27.7],
                status="available",
                specialization=["earthquake", "mass_casualty", "pandemic"],
                contact_info={"radio": "DMAT-01", "phone": "+977-1-555-0500"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="heavy_lift_drone_001",
                asset_type=AssetType.HEAVY_LIFT_DRONE,
                operator="Private Contractor",
                capabilities=["100kg_payload", "thermal", "winch", "long_endurance"],
                location=[85.3, 27.7],
                status="available",
                specialization=["tunnel_flood", "high_altitude_rescue", "supply_drop"],
                contact_info={"radio": "HEAVY-DRONE-01", "phone": "+977-1-555-0600"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="vhf_network_001",
                asset_type=AssetType.VHF_RADIO,
                operator="Disaster Management Authority",
                capabilities=["broadcast", "two_way", "siren_activation", "offline"],
                location=[85.3, 27.7],
                status="available",
                specialization=["total_isolation", "offline_communication"],
                contact_info={"frequency": "156.8 MHz", "phone": "+977-1-555-0700"},
                accreditation=True
            ),
            AssetRecord(
                asset_id="siren_system_001",
                asset_type=AssetType.SIREN_SYSTEM,
                operator="Local Government",
                capabilities=["omnidirectional", "voice", "tone_alert", "solar_powered"],
                location=[85.3, 27.7],
                status="available",
                specialization=["flash_flood", "tsunami", "dam_failure", "offline_alert"],
                contact_info={"control": "SIREN-CTRL-01"},
                accreditation=True
            )
        ]
    
    @trace_agent("risk_dispatch", "execute")
    async def execute(self, state: AgentState) -> AgentState:
            """Execute risk dispatch tasks"""

            task_graph = state.get("task_graph")
            current_task_id = state.get("current_task_id")

            if not task_graph or not current_task_id:
                current_task_id = self._find_next_dispatch_task(task_graph)
                state["current_task_id"] = current_task_id

            if not current_task_id:
                # No specific task found - run comprehensive risk dispatch as fallback
                result = await self._comprehensive_risk_dispatch(state, {})
            else:
                task = task_graph.nodes.get(current_task_id)
                if not task:
                    result = await self._comprehensive_risk_dispatch(state, {})
                else:
                    task_input = task.input_data
                    task_type = task_input.get("task", "")

                    result = None
                    try:
                        if task_type == "deadman_switch_alert":
                            result = await self._deadman_switch_alert(state, task_input)
                        elif task_type == "evacuation_routing":
                            result = await self._evacuation_routing(state, task_input)
                        elif task_type == "multilingual_alert_synthesis":
                            result = await self._multilingual_alert_synthesis(state, task_input)
                        elif task_type == "capability_matched_dispatch":
                            result = await self._capability_matched_dispatch(state, task_input)
                        elif task_type == "precautionary_override":
                            result = await self._precautionary_override(state, task_input)
                        elif task_type == "high_ground_evacuation_routing":
                            result = await self._high_ground_evacuation_routing(state, task_input)
                        elif task_type == "dmat_dispatch":
                            result = await self._dmat_dispatch(state, task_input)
                        elif task_type == "access_viability_rerouting":
                            result = await self._access_viability_rerouting(state, task_input)
                        elif task_type == "comprehensive_risk_dispatch":
                            result = await self._comprehensive_risk_dispatch(state, task_input)
                        elif task_type == "revision":
                            result = await self._handle_revision(state, task_input)
                        else:
                            result = await self._comprehensive_risk_dispatch(state, task_input)

                        if task:
                            task.status = TaskStatus.COMPLETED
                            task.result = result
                            task.completed_at = datetime.utcnow()

                    except Exception as e:
                        if task:
                            task.status = TaskStatus.FAILED
                            task.error = str(e)
                            task.attempts += 1
                        state = self._add_error(state, f"Risk dispatch task {task_type} failed: {e}")

            state["risk_dispatch_output"] = result or {}
            state["next_agent"] = AgentType.EVALUATOR
            state = self._update_state_trace(state, result or {})

            return state

                def _find_next_dispatch_task(self, task_graph: Optional[Any]) -> Optional[str]:
                    """Find next pending risk dispatch task"""
                    if not task_graph:
                        return None

                    for task_id, task in task_graph.nodes.items():
                        if (task.agent_type == AgentType.RISK_DISPATCH and
                            task.status == TaskStatus.PENDING):
                            deps_met = all(
                                task_graph.nodes[dep_id].status == TaskStatus.COMPLETED
                                for dep_id in task.dependencies
                                if dep_id in task_graph.nodes
                            )
                            if deps_met:
                                return task_id
                    return None

                @trace_tool_call("risk_dispatch", "deadman_switch_alert")
                async def _deadman_switch_alert(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
                    """Auto-dispatch alerts when human supervisor doesn't respond (Failure #1)"""

                    timeout_seconds = task_input.get("timeout_seconds", settings.ALERT_DEADMAN_SWITCH_SECONDS)
                    bypass_supervisor = task_input.get("bypass_supervisor", True)

            # Get polygons from world model simulator
            world_model_output = state.get("world_model_simulator_output") or {}
            polygons_data = world_model_output.get("expanded_polygons", [])

            if not polygons_data:
                # Generate from context
                polygons_data = self._generate_alert_polygons(state)
        
        alerts_dispatched = []
        for poly_data in polygons_data:
            alert = await self._create_alert(poly_data, bypass_supervisor)
            alerts_dispatched.append(alert)
        
        # Simulate dispatch to IPAWS/ES-Alert/Genasys
        dispatch_results = await self._dispatch_to_systems(alerts_dispatched)
        
        return {
            "task": "deadman_switch_alert",
            "timeout_seconds": timeout_seconds,
            "bypass_supervisor": bypass_supervisor,
            "alerts_created": len(alerts_dispatched),
            "alerts_dispatched": alerts_dispatched,
            "dispatch_results": dispatch_results,
            "deadman_switch_triggered": True,
            "dispatch_time_seconds": timeout_seconds,
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    def _generate_alert_polygons(self, state: AgentState) -> List[Dict]:
        """Generate alert polygons from disaster context"""
        disaster_type = state.get("context", {}).get("disaster_type", "unknown")
        severity = state.get("context", {}).get("severity", "warning")
        
        # Mock polygon generation - in production would use actual hazard modeling
        base_polygons = {
            "flash_flood": [
                {"coordinates": [[[85.0, 27.0], [85.5, 27.0], [85.5, 27.5], [85.0, 27.5], [85.0, 27.0]]],
                 "hazard_type": "flash_flood", "severity": severity}
            ],
            "wildfire": [
                {"coordinates": [[[85.0, 27.0], [85.5, 27.0], [85.5, 27.5], [85.0, 27.5], [85.0, 27.0]]],
                 "hazard_type": "wildfire", "severity": severity}
            ],
            "earthquake": [
                {"coordinates": [[[85.0, 27.0], [85.5, 27.0], [85.5, 27.5], [85.0, 27.5], [85.0, 27.0]]],
                 "hazard_type": "earthquake", "severity": severity}
            ]
        }
        
        return base_polygons.get(disaster_type, base_polygons["flash_flood"])
    
    async def _create_alert(self, poly_data: Dict, bypass_supervisor: bool) -> AlertPolygon:
        """Create alert polygon with all required fields"""
        
        hazard_type_str = poly_data.get("hazard_type", "flash_flood")
        try:
            hazard_type = DisasterType(hazard_type_str)
        except ValueError:
            hazard_type = DisasterType.FLASH_FLOOD
        
        severity_str = poly_data.get("severity", "warning")
        try:
            severity = SeverityLevel(severity_str)
        except ValueError:
            severity = SeverityLevel.WARNING
        
        # Determine languages based on location/hazard
        languages = self._determine_languages(hazard_type, poly_data.get("coordinates"))
        
        # Calculate arrival ETA if available
        arrival_eta = poly_data.get("arrival_eta_minutes")
        
        # Find nearest shelter
        shelter = self._find_nearest_shelter(poly_data.get("coordinates"))
        
        return AlertPolygon(
            coordinates=poly_data.get("coordinates", []),
            properties={
                "hazard_type": hazard_type_str,
                "severity": severity_str,
                "bypass_supervisor": bypass_supervisor,
                "auto_generated": True
            },
            hazard_type=hazard_type,
            severity=severity,
            expires_at=datetime.utcnow() + timedelta(hours=6),
            languages=languages,
            arrival_eta_minutes=arrival_eta,
            shelter_coordinates=shelter,
            community_focal_points=self._get_community_focal_points(poly_data.get("coordinates"))
        )
    
    def _determine_languages(self, hazard_type: DisasterType, coordinates: List) -> List[str]:
        """Determine required languages for alert"""
        # Default to English
        languages = ["en"]
        
        # Add languages based on hazard location (simplified)
        # In production: use geocoding to determine affected languages
        if hazard_type in [DisasterType.FLASH_FLOOD, DisasterType.ROCK_ICE_AVALANCHE]:
            # Nepal context
            languages.extend(["ne", "hi", "bo", "en"])  # Nepali, Hindi, Tibetan, English
        elif hazard_type == DisasterType.WILDFIRE:
            # California/Spain context
            languages.extend(["es", "ca", "en"])  # Spanish, Valencian, English
        elif hazard_type == DisasterType.DAM_FAILURE:
            # Libya context
            languages.extend(["ar", "en"])
        elif hazard_type == DisasterType.EARTHQUAKE:
            # Turkey/Myanmar context
            languages.extend(["tr", "ar", "ku", "my", "en"])
        
        return list(set(languages))
    
    def _find_nearest_shelter(self, coordinates: List) -> Optional[List[float]]:
        """Find nearest shelter coordinates"""
        # Mock shelter locations
        shelters = [
            [85.3, 27.7],  # Kathmandu
            [88.4, 22.6],  # Kolkata
            [96.1, 21.9],  # Mandalay
        ]
        if not coordinates or not coordinates[0]:
            return shelters[0]
        
        # Simple nearest (in production: use proper geospatial)
        poly_center = coordinates[0][0] if coordinates[0] else [85.3, 27.7]
        return min(shelters, key=lambda s: (s[0]-poly_center[0])**2 + (s[1]-poly_center[1])**2)
    
    def _get_community_focal_points(self, coordinates: List) -> List[str]:
        """Get named community focal points"""
        return ["Community Center", "Primary School", "Religious Center", "Market Square"]
    
    async def _dispatch_to_systems(self, alerts: List[AlertPolygon]) -> Dict[str, Any]:
        """Dispatch alerts to multiple alerting systems"""
        
        results = {
            "ipaws": {"status": "dispatched", "alert_ids": []},
            "es_alert": {"status": "dispatched", "alert_ids": []},
            "genasys": {"status": "dispatched", "alert_ids": []},
            "vhf_radio": {"status": "broadcast", "alert_ids": []},
            "siren": {"status": "activated", "alert_ids": []}
        }
        
        for alert in alerts:
            alert_id = f"ALT-{uuid4().hex[:8]}"
            for system in results:
                results[system]["alert_ids"].append(alert_id)
        
        return results
    
    @trace_tool_call("risk_dispatch", "evacuation_routing")
    async def _evacuation_routing(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Generate evacuation routes prioritizing vulnerable populations"""
        
        prioritize_vulnerable = task_input.get("prioritize_vulnerable", True)
        
        # Get polygons from world model
        world_model_output = state.get("world_model_simulator_output", {})
        polygons = world_model_output.get("expanded_polygons", [])
        
        routes = []
        for poly in polygons:
            # Generate routes to high ground / shelters
            shelter = self._find_nearest_shelter(poly.get("coordinates"))
            
            route = {
                "route_id": f"EVAC-{uuid4().hex[:8]}",
                "from_polygon": poly.get("coordinates"),
                "to_shelter": shelter,
                "distance_km": 15.2,  # Mock
                "estimated_time_minutes": 30,
                "capacity": 500,
                "vulnerable_priority": prioritize_vulnerable,
                "road_status": "assumed_clear",  # Would check real-time
                "alternative_routes": 2
            }
            routes.append(route)
        
        return {
            "task": "evacuation_routing",
            "routes_generated": len(routes),
            "evacuation_routes": routes,
            "vulnerable_prioritized": prioritize_vulnerable,
            "total_capacity": sum(r["capacity"] for r in routes),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "multilingual_alert_synthesis")
    async def _multilingual_alert_synthesis(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Generate multilingual alert payloads (Failure #7)"""
        
        languages = task_input.get("languages", ["en", "es", "zh", "vi", "ko"])
        world_model_output = state.get("world_model_simulator_output", {})
        polygons = world_model_output.get("expanded_polygons", [])
        
        alerts = []
        for poly in polygons:
            hazard_type = poly.get("hazard_type", "unknown")
            arrival_eta = poly.get("arrival_eta_minutes", 30)
            shelter = self._find_nearest_shelter(poly.get("coordinates"))
            focal_points = self._get_community_focal_points(poly.get("coordinates"))
            
            for lang in languages:
                alert = self._synthesize_alert(
                    hazard_type=hazard_type,
                    language=lang,
                    arrival_eta=arrival_eta,
                    shelter=shelter,
                    focal_points=focal_points,
                    polygon=poly.get("coordinates")
                )
                alerts.append(alert)
        
        return {
            "task": "multilingual_alert_synthesis",
            "languages": languages,
            "alerts_generated": len(alerts),
            "alerts": alerts,
            "synthesized_at": datetime.utcnow().isoformat()
        }
    
    def _synthesize_alert(
        self,
        hazard_type: str,
        language: str,
        arrival_eta: int,
        shelter: Optional[List[float]],
        focal_points: List[str],
        polygon: List
    ) -> Dict[str, Any]:
        """Synthesize alert in specific language"""
        
        # Templates per language (simplified)
        templates = {
            "en": {
                "headline": "EMERGENCY ALERT: {hazard} Imminent",
                "instruction": "EVACUATE NOW. {hazard} arriving in {eta} minutes. Go to {shelter}. Focal points: {focal}.",
                "hazard_names": {
                    "flash_flood": "Flash Flood",
                    "wildfire": "Wildfire",
                    "earthquake": "Earthquake Aftershock",
                    "dam_failure": "Dam Failure",
                    "rock_ice_avalanche": "Rock-Ice Avalanche"
                }
            },
            "ne": {  # Nepali
                "headline": "आपातकालीन चेतावनी: {hazard} निकट",
                "instruction": "तुरुन्त निस्कनुहोस्। {hazard} {eta} मिनेटमा पुग्छ। {shelter} जानुहोस्। फोकल पोइन्ट: {focal}।",
                "hazard_names": {
                    "flash_flood": "चट्याङ्ग बाढ",
                    "wildfire": "वन अग्नि",
                    "earthquake": "भूकम्पको झड्का",
                    "dam_failure": "बाँध विफलता",
                    "rock_ice_avalanche": "खड्ग-हिम हिमस्खलन"
                }
            },
            "hi": {  # Hindi
                "headline": "आपातकालीन चेतावनी: {hazard} आसन्न",
                "instruction": "तुरंत निकलें। {hazard} {eta} मिनट में आ रहा है। {shelter} जाएं। फोकल पॉइंट: {focal}।",
                "hazard_names": {
                    "flash_flood": "चानक बाढ़",
                    "wildfire": "जंगल की आग",
                    "earthquake": "भूकंप का झटका",
                    "dam_failure": "बांध विफलता",
                    "rock_ice_avalanche": "चट्टान-बर्फ हिमस्खलन"
                }
            },
            "es": {  # Spanish
                "headline": "ALERTA DE EMERGENCIA: {hazard} Inminente",
                "instruction": "EVACÚESE AHORA. {hazard} llega en {eta} minutos. Vaya a {shelter}. Puntos focales: {focal}.",
                "hazard_names": {
                    "flash_flood": "Inundación Relámpago",
                    "wildfire": "Incendio Forestal",
                    "earthquake": "Réplica de Terremoto",
                    "dam_failure": "Falla de Presa",
                    "rock_ice_avalanche": "Avalancha de Roca-Hielo"
                }
            },
            "ca": {  # Valencian/Catalan
                "headline": "ALERTA D'EMERGÈNCIA: {hazard} Imminent",
                "instruction": "EVACUEU ARA. {hazard} arriba en {eta} minuts. Aneu a {shelter}. Punts focals: {focal}.",
                "hazard_names": {
                    "flash_flood": "Inundació Súbita",
                    "wildfire": "Incendi Forestal",
                    "earthquake": "Rèplica de Terratrèmol",
                    "dam_failure": "Falta de Pressa",
                    "rock_ice_avalanche": "Allau de Roca-Gel"
                }
            },
            "tr": {  # Turkish
                "headline": "ACİL UYARI: {hazard} Yaklaşıyor",
                "instruction": "HEMEN TAŞININ. {hazard} {eta} dakika içinde gelecek. {shelter}'e gidin. Odak noktaları: {focal}.",
                "hazard_names": {
                    "flash_flood": "Aniden Sel",
                    "wildfire": "Orman Yangını",
                    "earthquake": "Deprem Artçığı",
                    "dam_failure": "Baraj Arızası",
                    "rock_ice_avalanche": "Kaya-Buz Heyelanı"
                }
            },
            "ar": {  # Arabic
                "headline": "تنبيه طارئ: {hazard} وشيك",
                "instruction": "أخلِ فوراً. {hazard} سيصل خلال {eta} دقيقة. اذهب إلى {shelter}. النقاط المحورية: {focal}.",
                "hazard_names": {
                    "flash_flood": "فيضان مفاجئ",
                    "wildfire": "حريق غابات",
                    "earthquake": "هزة أرضية تالية",
                    "dam_failure": "فشل سد",
                    "rock_ice_avalanche": "انهيار صخري جليدي"
                }
            },
            "ku": {  # Kurdish
                "headline": "HÊJA MARJ: {hazard} Nêzîk e",
                "instruction": "ÊDÎ BERÇAV BIBE. {hazard} li {eta} deqe da dipe. Biçû {shelter}. Nîşanên sereke: {focal}.",
                "hazard_names": {
                    "flash_flood": "Avieriya Têkildar",
                    "wildfire": "Agira Daristanê",
                    "earthquake": "Rêwîya Zîyankirina Zewîyê",
                    "dam_failure": "Kêşeya Bendava",
                    "rock_ice_avalanche": "Derdora Wirî-Buzê"
                }
            }
        }
        
        template = templates.get(language, templates["en"])
        hazard_name = template["hazard_names"].get(hazard_type, hazard_type)
        shelter_str = f"{shelter[1]:.4f}°N, {shelter[0]:.4f}°E" if shelter else "designated shelter"
        focal_str = ", ".join(focal_points[:3])
        
        return {
            "language": language,
            "headline": template["headline"].format(hazard=hazard_name),
            "instruction": template["instruction"].format(
                hazard=hazard_name, eta=arrival_eta, shelter=shelter_str, focal=focal_str
            ),
            "polygon": polygon,
            "arrival_eta_minutes": arrival_eta,
            "shelter_coordinates": shelter,
            "community_focal_points": focal_points,
            "format": "CAP"  # Common Alerting Protocol
        }
    
    @trace_tool_call("risk_dispatch", "capability_matched_dispatch")
    async def _capability_matched_dispatch(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Match assets to hazard mechanics (Failure #10)"""
        
        hazard = task_input.get("hazard", "unknown")
        capability_match = task_input.get("capability_match", [])
        
        # Filter assets by specialization
        matched_assets = []
        for asset in self.asset_catalog:
            if (asset.status == "available" and asset.accreditation and
                (hazard in asset.specialization or any(c in asset.specialization for c in capability_match))):
                matched_assets.append(asset)
        
        # Sort by proximity to hazard (mock)
        dispatch_decisions = []
        for asset in matched_assets[:3]:  # Top 3 matches
            dispatch_decisions.append({
                "asset_id": asset.asset_id,
                "asset_type": asset.asset_type.value,
                "operator": asset.operator,
                "specialization_match": [s for s in asset.specialization if s in capability_match or s == hazard],
                "dispatch_time_estimate_minutes": 15,
                "contact": asset.contact_info
            })
        
        return {
            "task": "capability_matched_dispatch",
            "hazard": hazard,
            "capability_requirements": capability_match,
            "matched_assets": len(matched_assets),
            "asset_dispatches": dispatch_decisions,
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "precautionary_override")
    async def _precautionary_override(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Override contradictory messages (Failure #6)"""
        
        enforce_high_ground = task_input.get("enforce_high_ground", True)
        block_curfew = task_input.get("block_curfew", True)
        
        return {
            "task": "precautionary_override",
            "actions_taken": [
                "BLOCKED: Curfew/shelter-in-place orders in inundation zone",
                "ENFORCED: High-ground evacuation routing",
                "ACTIVATED: Pre-authorized dam breach protocol",
                "NOTIFIED: National military emergency unit (UME)"
            ],
            "enforce_high_ground": enforce_high_ground,
            "block_curfew": block_curfew,
            "override_authority": "Pre-authorized SOP: sop_flood_red_alert",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "high_ground_evacuation_routing")
    async def _high_ground_evacuation_routing(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Route to high ground for dam breach (Failure #6)"""
        
        dam_breach_polygon = task_input.get("dam_breach_polygon", True)
        
        # Find high ground elevation points
        high_ground_points = [
            [85.5, 27.8, 1500],  # lat, lon, elevation_m
            [85.2, 27.9, 1400],
            [85.7, 27.6, 1600]
        ]
        
        routes = []
        for point in high_ground_points:
            routes.append({
                "route_id": f"HGE-{uuid4().hex[:8]}",
                "destination": {"lat": point[1], "lon": point[0], "elevation_m": point[2]},
                "route_type": "high_ground_evacuation",
                "estimated_time_minutes": 45,
                "capacity": 200
            })
        
        return {
            "task": "high_ground_evacuation_routing",
            "dam_breach_polygon": dam_breach_polygon,
            "high_ground_routes": routes,
            "highest_elevation_m": max(p[2] for p in high_ground_points),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "dmat_dispatch")
    async def _dmat_dispatch(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Dispatch DMAT teams for mass casualty (Failure #9, #10)"""
        
        capability_match = task_input.get("capability_match", [])
        
        dmat_assets = [a for a in self.asset_catalog if a.asset_type == AssetType.DMAT_TEAM and a.status == "available"]
        
        dispatches = []
        for asset in dmat_assets:
            if any(c in asset.specialization for c in capability_match):
                dispatches.append({
                    "asset_id": asset.asset_id,
                    "team_type": "DMAT",
                    "capabilities": asset.capabilities,
                    "specialization_match": [c for c in capability_match if c in asset.specialization],
                    "contact": asset.contact_info,
                    "deployment_time_minutes": 30
                })
        
        return {
            "task": "dmat_dispatch",
            "capability_requirements": capability_match,
            "teams_dispatched": len(dispatches),
            "dispatches": dispatches,
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "access_viability_rerouting")
    async def _access_viability_rerouting(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Reroute isolated villages (Failure #8)"""
        
        modes = task_input.get("modes", [])
        isolation = state.get("ingestion_executor_output", {}).get("infrastructure_isolation_assessment", {})
        assessment = isolation.get("assessment", {})
        
        reroutes = []
        for mode in modes:
            feasible = True
            if mode == "ground_vehicle" and assessment.get("roads", {}).get("blocked_segments", 0) > 10:
                feasible = False
            elif mode == "helicopter" and assessment.get("ports", {}).get("accessible", True) == False:
                feasible = True  # Helicopters don't need ports
            
            reroutes.append({
                "mode": mode,
                "feasible": feasible,
                "reason": "Roads blocked" if not feasible else "Available",
                "estimated_coverage": "partial" if not feasible else "full"
            })
        
        return {
            "task": "access_viability_rerouting",
            "isolation_assessment": assessment,
            "requested_modes": modes,
            "reroutes": reroutes,
            "recommended_primary": [r["mode"] for r in reroutes if r["feasible"]][:2],
            "rerouted_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("risk_dispatch", "comprehensive_risk_dispatch")
    async def _comprehensive_risk_dispatch(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Comprehensive dispatch for generic multi-hazard"""
        
        # Combine all dispatch capabilities
        results = {
            "alert_dispatch": await self._deadman_switch_alert(state, {"timeout_seconds": 180, "bypass_supervisor": True}),
            "asset_dispatch": await self._capability_matched_dispatch(state, {"hazard": "multi", "capability_match": ["all"]}),
            "evacuation_routing": await self._evacuation_routing(state, {"prioritize_vulnerable": True}),
            "sop_execution": await self._execute_sops(state)
        }
        
        return {
            "task": "comprehensive_risk_dispatch",
            "sub_tasks": results,
            "dispatched_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_sops(self, state: AgentState) -> Dict[str, Any]:
        """Execute retrieved SOPs"""
        hmem_output = state.get("hmem_store_output", {})
        sops = hmem_output.get("sops_retrieved", [])
        
        executed = []
        for sop in sops:
            executed.append({
                "sop_id": sop.get("sop_id"),
                "status": "executed",
                "actions_completed": len(sop.get("required_actions", []))
            })
        
        return {"sops_executed": len(executed), "details": executed}
    
    async def _handle_revision(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Handle revision from evaluator"""
        return {
            "revision_action": "retry_with_adjusted_parameters",
            "task_input": task_input,
            "revised_at": datetime.utcnow().isoformat()
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.RISK_DISPATCH, RiskDispatchAgent())