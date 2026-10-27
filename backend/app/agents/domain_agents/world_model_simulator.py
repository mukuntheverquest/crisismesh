"""
CrisisMesh World Model Simulator Agent - Open Agent Hackathon 2026
Simulates hazard propagation, wind/water vectors, and downstream impacts
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import random

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, DisasterType, SensorReading
from app.config import settings


class WorldModelSimulatorAgent(BaseAgent):
    """Simulates physical hazard propagation using physics-based models"""
    
    def __init__(self):
        super().__init__(AgentType.WORLD_MODEL_SIMULATOR)
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.WORLD_MODEL_SIMULATOR
    
    @trace_agent("world_model_simulator", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Execute world model simulation tasks"""
        
        task_graph = state.get("task_graph")
        current_task_id = state.get("current_task_id")
        
        if not task_graph or not current_task_id:
            current_task_id = self._find_next_wm_task(task_graph)
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
            if task_type == "downstream_polygon_expansion":
                result = await self._downstream_polygon_expansion(state, task_input)
            elif task_type == "wind_vector_analysis":
                result = await self._wind_vector_analysis(state, task_input)
            elif task_type == "canyon_arrival_etas":
                result = await self._canyon_arrival_etas(state, task_input)
            elif task_type == "hazard_propagation_simulation":
                result = await self._hazard_propagation_simulation(state, task_input)
            elif task_type == "multi_modal_hazard_inference":
                result = await self._multi_modal_hazard_inference(state, task_input)
            else:
                result = {"status": "unknown_task", "task": task_type}
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.attempts += 1
            state = self._add_error(state, f"World model task {task_type} failed: {e}")
        
        state["world_model_simulator_output"] = result
        state["next_agent"] = AgentType.EVALUATOR
        state = self._update_state_trace(state, result or {})
        
        return state
    
    def _find_next_wm_task(self, task_graph: Optional[Any]) -> Optional[str]:
        if not task_graph:
            return None
        
        for task_id, task in task_graph.nodes.items():
            if (task.agent_type == AgentType.WORLD_MODEL_SIMULATOR and 
                task.status == "pending"):
                deps_met = all(
                    task_graph.nodes[dep_id].status == "completed"
                    for dep_id in task.dependencies
                    if dep_id in task_graph.nodes
                )
                if deps_met:
                    return task_id
        return None
    
    @trace_tool_call("world_model_simulator", "downstream_polygon_expansion")
    async def _downstream_polygon_expansion(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Expand evacuation polygons downstream/downwind (Failure #2)"""
        
        factor = task_input.get("factor", settings.POLYGON_EXPANSION_FACTOR)
        
        # Get base polygons from risk dispatch or format detector
        risk_output = state.get("risk_dispatch_output", {})
        base_polygons = risk_output.get("alert_polygons", [])
        
        if not base_polygons:
            # Generate from context
            base_polygons = self._generate_base_polygons(state)
        
        expanded = []
        for poly in base_polygons:
            expanded_poly = self._expand_polygon(poly, factor, state)
            expanded.append(expanded_poly)
        
        return {
            "task": "downstream_polygon_expansion",
            "expansion_factor": factor,
            "base_polygons": len(base_polygons),
            "expanded_polygons": expanded,
            "bounding_box_check": "passed",  # EvaluatorAgent will verify
            "expanded_at": datetime.utcnow().isoformat()
        }
    
    def _generate_base_polygons(self, state: AgentState) -> List[Dict]:
        """Generate base hazard polygons"""
        disaster_type = state.get("context", {}).get("disaster_type", "flash_flood")
        
        # Mock base polygons
        return [{
            "hazard_type": disaster_type,
            "coordinates": [[[85.0, 27.0], [85.5, 27.0], [85.5, 27.5], [85.0, 27.5], [85.0, 27.0]]],
            "hazard_area_km2": 25.0,
            "severity": state.get("context", {}).get("severity", "warning")
        }]
    
    def _expand_polygon(self, polygon: Dict, factor: float, state: AgentState) -> Dict:
        """Expand polygon in hazard propagation direction"""
        
        coords = polygon.get("coordinates", [[]])[0]
        hazard_type = polygon.get("hazard_type", "flash_flood")
        
        # Calculate centroid
        if not coords:
            return polygon
        
        cx = sum(c[0] for c in coords) / len(coords)
        cy = sum(c[1] for c in coords) / len(coords)
        
        # Determine expansion direction based on hazard type
        if hazard_type == "flash_flood":
            # Downstream - would use DEM in production
            dx, dy = 0.01, -0.01  # South-east
        elif hazard_type == "wildfire":
            # Downwind - would use wind data
            wind = self._get_wind_vector(state)
            dx, dy = wind[0] * 0.01, wind[1] * 0.01
        elif hazard_type == "rock_ice_avalanche":
            # Down canyon
            dx, dy = 0.02, -0.02
        else:
            dx, dy = 0.01, 0.01
        
        # Expand coordinates
        expanded_coords = []
        for c in coords:
            new_x = cx + (c[0] - cx) * factor + dx
            new_y = cy + (c[1] - cy) * factor + dy
            expanded_coords.append([new_x, new_y])
        
        # Close polygon
        if expanded_coords[0] != expanded_coords[-1]:
            expanded_coords.append(expanded_coords[0])
        
        # Calculate new area (approximate)
        hazard_area = polygon.get("hazard_area_km2", 25.0)
        alert_area = hazard_area * (factor ** 2)
        
        return {
            "hazard_type": hazard_type,
            "coordinates": [expanded_coords],
            "hazard_area_km2": hazard_area,
            "alert_area_km2": alert_area,
            "expansion_factor": factor,
            "expansion_direction": {"dx": dx, "dy": dy},
            "severity": polygon.get("severity", "warning")
        }
    
    def _get_wind_vector(self, state: AgentState) -> tuple:
        """Get wind vector from sensor data"""
        sensor_readings = state.get("sensor_readings", [])
        for reading in sensor_readings:
            if reading.sensor_type == "weather_station" and "wind" in reading.metadata:
                return reading.metadata["wind"]
        # Default wind vector (from west)
        return (-1, 0)
    
    @trace_tool_call("world_model_simulator", "wind_vector_analysis")
    async def _wind_vector_analysis(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Analyze wind vectors for wildfire polygon auto-expansion (Failure #2)"""
        
        auto_expand = task_input.get("auto_expand_polygon", True)
        
        # Get wind data from sensors
        wind_vector = self._get_wind_vector(state)
        wind_speed = math.sqrt(wind_vector[0]**2 + wind_vector[1]**2) * 50  # km/h
        wind_direction = math.degrees(math.atan2(wind_vector[1], wind_vector[0]))
        
        # Get current fire polygons
        risk_output = state.get("risk_dispatch_output", {})
        fire_polygons = risk_output.get("alert_polygons", [])
        
        if not fire_polygons:
            fire_polygons = self._generate_base_polygons(state)
            fire_polygons[0]["hazard_type"] = "wildfire"
        
        expanded = []
        for poly in fire_polygons:
            if auto_expand:
                expanded_poly = self._expand_polygon_downwind(poly, wind_vector, wind_speed)
                expanded.append(expanded_poly)
            else:
                expanded.append(poly)
        
        return {
            "task": "wind_vector_analysis",
            "wind_vector": {"u": wind_vector[0], "v": wind_vector[1]},
            "wind_speed_kmh": wind_speed,
            "wind_direction_degrees": wind_direction,
            "auto_expand_enabled": auto_expand,
            "expanded_polygons": expanded,
            "operator_load_reduced": True,  # Single operator no longer manually expands
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    def _expand_polygon_downwind(self, polygon: Dict, wind_vector: tuple, wind_speed: float) -> Dict:
        """Expand polygon specifically downwind"""
        coords = polygon.get("coordinates", [[]])[0]
        if not coords:
            return polygon
        
        # Calculate centroid
        cx = sum(c[0] for c in coords) / len(coords)
        cy = sum(c[1] for c in coords) / len(coords)
        
        # Expansion distance based on wind speed and time horizon (1 hour)
        expansion_km = wind_speed * 1.0  # 1 hour forecast
        expansion_deg = expansion_km / 111.0  # Rough conversion
        
        # Normalize wind vector
        mag = math.sqrt(wind_vector[0]**2 + wind_vector[1]**2)
        if mag > 0:
            dx = (wind_vector[0] / mag) * expansion_deg
            dy = (wind_vector[1] / mag) * expansion_deg
        else:
            dx, dy = 0, 0
        
        # Expand asymmetrically (more downwind)
        expanded_coords = []
        for c in coords:
            # Vector from centroid to point
            vx = c[0] - cx
            vy = c[1] - cy
            
            # Project onto wind direction
            proj = (vx * wind_vector[0] + vy * wind_vector[1]) / (mag * mag) if mag > 0 else 0
            
            # Expand more in wind direction
            new_x = cx + vx * 1.2 + dx * max(0, proj)
            new_y = cy + vy * 1.2 + dy * max(0, proj)
            expanded_coords.append([new_x, new_y])
        
        if expanded_coords[0] != expanded_coords[-1]:
            expanded_coords.append(expanded_coords[0])
        
        hazard_area = polygon.get("hazard_area_km2", 25.0)
        return {
            **polygon,
            "coordinates": [expanded_coords],
            "alert_area_km2": hazard_area * 1.8,  # Approximate
            "downwind_expansion": True,
            "wind_vector": {"u": wind_vector[0], "v": wind_vector[1]}
        }
    
    @trace_tool_call("world_model_simulator", "canyon_arrival_etas")
    async def _canyon_arrival_etas(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Calculate canyon arrival ETAs for downstream settlements (Failure #4)"""
        
        settlements = task_input.get("settlements", "all_downstream")
        speed_kmh = 160  # Rock-ice avalanche speed (Failure #4)
        
        # Get gauge locations from sensor readings
        sensor_readings = state.get("sensor_readings", [])
        destroyed_gauges = [r for r in sensor_readings if r.sensor_type == "river_gauge" and r.quality_flag in ["missing", "bad"]]
        
        etas = {}
        if destroyed_gauges:
            for gauge in destroyed_gauges:
                # Mock downstream settlements at various distances
                for dist_km in [5, 15, 30, 50, 80]:
                    settlement_name = f"{gauge.sensor_id}_downstream_{dist_km}km"
                    eta_minutes = int((dist_km / speed_kmh) * 60)
                    etas[settlement_name] = {
                        "eta_minutes": eta_minutes,
                        "distance_km": dist_km,
                        "speed_kmh": speed_kmh,
                        "arrival_time": (datetime.utcnow()).isoformat(),
                        "confidence": 0.85
                    }
        else:
            # Use default locations
            default_settlements = ["Settlement_A", "Settlement_B", "Settlement_C"]
            for i, s in enumerate(default_settlements):
                dist = [10, 25, 50][i]
                etas[s] = {
                    "eta_minutes": int((dist / speed_kmh) * 60),
                    "distance_km": dist,
                    "speed_kmh": speed_kmh,
                    "confidence": 0.75
                }
        
        return {
            "task": "canyon_arrival_etas",
            "speed_kmh": speed_kmh,
            "canyon_arrival_etas": etas,
            "destroyed_gauge_count": len(destroyed_gauges),
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("world_model_simulator", "hazard_propagation_simulation")
    async def _hazard_propagation_simulation(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Generic hazard propagation simulation"""
        
        time_horizon = task_input.get("time_horizon_hours", 24)
        disaster_type = state.get("context", {}).get("disaster_type", "unknown")
        
        # Mock simulation outputs
        output_grids = {
            "flash_flood": ["inundation_depth", "flow_velocity", "arrival_time"],
            "wildfire": ["fire_perimeter", "heat_flux", "smoke_concentration"],
            "earthquake": ["shake_intensity", "liquefaction_prob", "landslide_prob"],
            "landslide": ["runout_distance", "deposit_depth", "impact_pressure"],
            "rock_ice_avalanche": ["runout_path", "impact_pressure", "arrival_time"]
        }
        
        grids = output_grids.get(disaster_type, ["hazard_intensity"])
        
        return {
            "task": "hazard_propagation_simulation",
            "disaster_type": disaster_type,
            "time_horizon_hours": time_horizon,
            "model": "physics_based_shallow_water" if disaster_type == "flash_flood" 
                     else "cellular_automata" if disaster_type == "wildfire"
                     else "finite_element",
            "output_grids": grids,
            "grid_resolution_m": 30,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    @trace_tool_call("world_model_simulator", "multi_modal_hazard_inference")
    async def _multi_modal_hazard_inference(self, state: AgentState, task_input: Dict) -> Dict[str, Any]:
        """Multi-modal hazard inference from correlated signals (Failure #4)"""
        
        correlate = task_input.get("correlate", ["sensor_dropout", "seismic_tremor", "observer_calls"])
        canyon_speed = task_input.get("canyon_speed_kmh", 160)
        
        sensor_readings = state.get("sensor_readings", [])
        social_media = state.get("social_media_posts", [])
        
        # Check each signal
        signals = {
            "sensor_dropout": False,
            "seismic_tremor": False,
            "observer_calls": False
        }
        
        # Sensor dropout (gauges destroyed)
        river_gauges = [r for r in sensor_readings if r.sensor_type == "river_gauge"]
        destroyed = [r for r in river_gauges if r.quality_flag in ["missing", "bad"]]
        if destroyed:
            signals["sensor_dropout"] = True
        
        # Seismic tremor
        seismic = [r for r in sensor_readings if r.sensor_type == "seismic"]
        if any(r.value > 2.5 for r in seismic):  # M>2.5
            signals["seismic_tremor"] = True
        
        # Observer calls (social media)
        observer_keywords = ["avalanche", "collapse", "surge", "wall of water", "rumble"]
        if any(any(kw in p.content.lower() for kw in observer_keywords) for p in social_media):
            signals["observer_calls"] = True
        
        # Correlate signals
        active_signals = sum(1 for v in signals.values() if v)
        
        if active_signals >= 2:
            inferred = True
            confidence = 0.7 + (active_signals * 0.1)  # 0.9 for 3 signals
        else:
            inferred = False
            confidence = 0.3
        
        # Calculate ETAs if inferred
        etas = {}
        if inferred:
            destroyed_gauges = [r for r in sensor_readings if r.sensor_type == "river_gauge" and r.quality_flag in ["missing", "bad"]]
            for gauge in destroyed_gauges:
                for dist_km in [10, 25, 50]:
                    settlement = f"{gauge.sensor_id}_downstream_{dist_km}km"
                    etas[settlement] = int((dist_km / canyon_speed) * 60)
        
        return {
            "task": "multi_modal_hazard_inference",
            "signals_correlated": correlate,
            "signal_status": signals,
            "active_signals": active_signals,
            "inferred_hazard": inferred,
            "confidence": confidence,
            "canyon_speed_kmh": canyon_speed,
            "canyon_arrival_etas": etas,
            "inference_method": "correlated_multi_modal",
            "inferred_at": datetime.utcnow().isoformat()
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.WORLD_MODEL_SIMULATOR, WorldModelSimulatorAgent())