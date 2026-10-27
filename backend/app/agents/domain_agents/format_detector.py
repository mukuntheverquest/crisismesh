"""
CrisisMesh Format Detector Agent - Open Agent Hackathon 2026
Detects data formats, sensor types, and classifies disaster data complexity
"""
import filetype
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, SensorReading, SocialMediaDistress
from app.config import settings


class FormatDetectorAgent(BaseAgent):
    """Detects and classifies incoming disaster data formats and sources"""

    def __init__(self):
        super().__init__(AgentType.FORMAT_DETECTOR)

    @property
    def agent_type(self) -> AgentType:
        return AgentType.FORMAT_DETECTOR
    
    @trace_agent("format_detector", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Detect formats for all input data"""
        
        results = {
            "files": [],
            "sensor_readings": [],
            "social_media_posts": [],
            "official_alerts": [],
            "disaster_classification": {}
        }
        
        # Detect file formats
        for file_info in state.get("input_files", []):
            file_result = await self._detect_file_format(file_info)
            results["files"].append(file_result)
        
        # Classify sensor readings
        for reading in state.get("sensor_readings", []):
            sensor_result = self._classify_sensor_reading(reading)
            results["sensor_readings"].append(sensor_result)
        
        # Classify social media posts
        for post in state.get("social_media_posts", []):
            post_result = self._classify_social_media_post(post)
            results["social_media_posts"].append(post_result)
        
        # Classify official alerts
        for alert in state.get("official_alerts", []):
            alert_result = self._classify_official_alert(alert)
            results["official_alerts"].append(alert_result)
        
        # Overall disaster classification
        results["disaster_classification"] = self._classify_disaster_context(
            results["sensor_readings"],
            results["official_alerts"],
            state.get("disaster_context", {})
        )
        
        state["format_detector_output"] = results
        state["next_agent"] = AgentType.INGESTION_EXECUTOR
        state = self._update_state_trace(state, results)
        
        return state
    
    @trace_tool_call("format_detector", "detect_file_format")
    async def _detect_file_format(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect file MIME type and format details"""
        
        file_path = file_info.get("path", "")
        file_name = file_info.get("filename", "")
        mime_type = file_info.get("mime_type", "")
        
        result = {
            "file_path": file_path,
            "file_name": file_name,
            "provided_mime": mime_type,
            "detected_mime": None,
            "format_category": "unknown",
            "format_details": {},
            "conversion_complexity": "unknown",
            "confidence": 0.0
        }
        
        try:
            # Use filetype for detection
            kind = filetype.guess(file_path)
            if kind:
                result["detected_mime"] = kind.mime
                result["format_category"] = self._categorize_mime(kind.mime)
                result["format_details"] = {
                    "extension": kind.extension,
                    "mime": kind.mime
                }
                result["confidence"] = 0.95
            elif mime_type:
                result["detected_mime"] = mime_type
                result["format_category"] = self._categorize_mime(mime_type)
                result["confidence"] = 0.7
            else:
                # No filetype detection available
                result["detected_mime"] = "application/octet-stream"
                result["format_category"] = "unknown"
                result["confidence"] = 0.3
            
            # Assess conversion complexity
            result["conversion_complexity"] = self._assess_complexity(result["format_category"], file_path)
            
        except Exception as e:
            result["error"] = str(e)
            result["confidence"] = 0.0
        
        return result
    
    def _categorize_mime(self, mime: str) -> str:
        """Categorize MIME type into disaster-relevant categories"""
        mime = mime.lower()
        
        if mime.startswith("application/pdf"):
            return "pdf_document"
        elif mime.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml"):
            return "excel_spreadsheet"
        elif mime.startswith("application/vnd.ms-excel"):
            return "excel_spreadsheet_legacy"
        elif mime.startswith("text/csv"):
            return "csv_data"
        elif mime.startswith("application/json"):
            return "json_data"
        elif mime.startswith("application/geo+json") or mime.startswith("application/vnd.geo+json"):
            return "geojson"
        elif mime.startswith("image/"):
            return "image"
        elif mime.startswith("video/"):
            return "video"
        elif mime.startswith("application/x-netcdf") or "netcdf" in mime:
            return "netcdf_weather"
        elif mime.startswith("application/x-hdf") or "hdf" in mime:
            return "hdf5_satellite"
        elif "grib" in mime:
            return "grib_weather"
        elif "shapefile" in mime or "zip" in mime:
            return "shapefile_gis"
        elif mime.startswith("text/"):
            return "text_document"
        elif mime.startswith("application/xml") or mime.startswith("text/xml"):
            return "xml_data"
        else:
            return "unknown"
    
    def _assess_complexity(self, category: str, file_path: str) -> str:
        """Assess conversion/processing complexity"""
        complexity_map = {
            "pdf_document": "complex",  # May need OCR, table extraction
            "excel_spreadsheet": "standard",
            "excel_spreadsheet_legacy": "complex",
            "csv_data": "trivial",
            "json_data": "trivial",
            "geojson": "standard",
            "image": "complex",  # Needs OCR, orientation detection
            "video": "complex",
            "netcdf_weather": "complex",  # Multi-dimensional, needs xarray
            "hdf5_satellite": "complex",
            "grib_weather": "complex",
            "shapefile_gis": "standard",
            "text_document": "trivial",
            "xml_data": "standard",
            "unknown": "unknown"
        }
        return complexity_map.get(category, "unknown")
    
    def _classify_sensor_reading(self, reading: SensorReading) -> Dict[str, Any]:
        """Classify sensor reading type and reliability"""
        
        return {
            "sensor_id": reading.sensor_id,
            "sensor_type": reading.sensor_type,
            "location": reading.location,
            "timestamp": reading.timestamp.isoformat() if hasattr(reading.timestamp, 'isoformat') else str(reading.timestamp),
            "value": reading.value,
            "unit": reading.unit,
            "quality_flag": reading.quality_flag,
            "reliability_score": self._sensor_reliability_score(reading),
            "hazard_relevance": self._sensor_hazard_relevance(reading.sensor_type)
        }
    
    def _sensor_reliability_score(self, reading: SensorReading) -> float:
        """Score sensor reliability based on quality flag and type"""
        quality_scores = {"good": 1.0, "suspect": 0.5, "bad": 0.1, "missing": 0.0}
        base_score = quality_scores.get(reading.quality_flag, 0.5)
        
        # Sensor type reliability
        type_reliability = {
            "river_gauge": 0.95,
            "seismic": 0.98,
            "weather_station": 0.90,
            "satellite": 0.85,
            "crowdsource": 0.60
        }
        type_score = type_reliability.get(reading.sensor_type, 0.7)
        
        return (base_score + type_score) / 2
    
    def _sensor_hazard_relevance(self, sensor_type: str) -> List[str]:
        """Map sensor type to relevant hazards"""
        relevance_map = {
            "river_gauge": ["flash_flood", "dam_failure", "rock_ice_avalanche"],
            "seismic": ["earthquake", "rock_ice_avalanche", "volcanic_eruption"],
            "weather_station": ["flash_flood", "wildfire", "hurricane", "tornado"],
            "satellite": ["wildfire", "flood", "landslide", "volcanic_eruption", "hurricane"],
            "crowdsource": ["all"]
        }
        return relevance_map.get(sensor_type, ["unknown"])
    
    def _classify_social_media_post(self, post: SocialMediaDistress) -> Dict[str, Any]:
        """Classify social media distress post"""
        
        return {
            "post_id": post.post_id,
            "platform": post.platform,
            "language": post.language,
            "has_location_mention": bool(post.location_mentioned),
            "has_geocoded_location": bool(post.geocoded_location),
            "urgency_keywords": post.urgency_keywords,
            "urgency_score": self._calculate_urgency_score(post),
            "verification_status": "verified" if post.verified else "unverified",
            "sar_damage_confidence": post.sar_damage_confidence,
            "needs_satellite_verification": post.sar_damage_confidence is None or post.sar_damage_confidence < 0.75
        }
    
    def _calculate_urgency_score(self, post: SocialMediaDistress) -> float:
        """Calculate urgency score from keywords and context"""
        high_urgency = ["trapped", "buried", "dying", "help", "emergency", "urgent", "sos", "mayday"]
        medium_urgency = ["flooded", "collapsed", "damaged", "injured", "missing", "stranded"]
        low_urgency = ["rain", "wind", "shaking", "smoke", "ash"]
        
        content_lower = post.content.lower()
        score = 0.0
        
        for kw in high_urgency:
            if kw in content_lower:
                score += 0.3
        for kw in medium_urgency:
            if kw in content_lower:
                score += 0.15
        for kw in low_urgency:
            if kw in content_lower:
                score += 0.05
        
        if post.urgency_keywords:
            score += 0.2
        
        return min(score, 1.0)
    
    def _classify_official_alert(self, alert: Any) -> Dict[str, Any]:
        """Classify official alert - handle Pydantic models and dicts"""
        # Convert to dict properly
        if hasattr(alert, "model_dump"):
            alert_dict = alert.model_dump()
        elif hasattr(alert, "dict"):
            alert_dict = alert.dict()
        elif isinstance(alert, dict):
            alert_dict = alert
        else:
            # Fallback: try to extract attributes
            alert_dict = {}
            for attr in ["alert_id", "id", "event_type", "event", "severity", "certainty", "urgency", "polygon", "geocode", "polygon_area_km2", "languages"]:
                if hasattr(alert, attr):
                    alert_dict[attr] = getattr(alert, attr)
        
        return {
            "alert_id": alert_dict.get("alert_id") or alert_dict.get("id", "unknown"),
            "event": alert_dict.get("event_type") or alert_dict.get("event", "unknown"),
            "severity": alert_dict.get("severity", "unknown"),
            "certainty": alert_dict.get("certainty", "unknown"),
            "urgency": alert_dict.get("urgency", "unknown"),
            "has_polygon": "polygon" in alert_dict or "geocode" in alert_dict,
            "polygon_area_km2": alert_dict.get("polygon_area_km2"),
            "languages": alert_dict.get("languages", ["en"]),
            "is_contradictory": self._check_contradiction(alert_dict),
            "deadman_switch_eligible": self._check_deadman_eligibility(alert_dict)
        }
    
    def _check_contradiction(self, alert: Dict[str, Any]) -> bool:
        """Check if alert contradicts known hazard state"""
        # Simplified check - in production would query Zetaris for active hazards
        event = alert.get("event", "").lower()
        severity = alert.get("severity", "").lower()
        
        contradictory_patterns = [
            ("curfew", "flood"),
            ("shelter-in-place", "dam"),
            ("all-clear", "emergency"),
            ("good condition", "collapse")
        ]
        
        for pattern, hazard in contradictory_patterns:
            if pattern in event and hazard in event:
                return True
        return False
    
    def _check_deadman_eligibility(self, alert: Dict[str, Any]) -> bool:
        """Check if alert qualifies for dead-man's switch auto-approval"""
        severity = alert.get("severity", "").lower()
        urgency = alert.get("urgency", "").lower()
        certainty = alert.get("certainty", "").lower()
        
        return (severity in ["emergency", "catastrophic", "severe"] or
                urgency == "immediate" or
                certainty == "observed")
    
    def _classify_disaster_context(
        self,
        sensor_results: List[Dict],
        alert_results: List[Dict],
        disaster_context: Dict
    ) -> Dict[str, Any]:
        """Overall disaster classification from all inputs"""
        
        # Collect hazard indicators
        hazard_votes = {}
        
        for sensor in sensor_results:
            for hazard in sensor.get("hazard_relevance", []):
                hazard_votes[hazard] = hazard_votes.get(hazard, 0) + sensor.get("reliability_score", 0.5)
        
        for alert in alert_results:
            event = alert.get("event", "").lower()
            for hazard_type in ["flood", "fire", "earthquake", "landslide", "dam", "avalanche", "hurricane", "tornado"]:
                if hazard_type in event:
                    hazard_votes[hazard_type] = hazard_votes.get(hazard_type, 0) + 1.0
        
        # Determine primary disaster type
        primary_hazard = max(hazard_votes.items(), key=lambda x: x[1])[0] if hazard_votes else "unknown"
        
        # Confidence based on vote spread
        total_votes = sum(hazard_votes.values())
        confidence = hazard_votes.get(primary_hazard, 0) / total_votes if total_votes > 0 else 0
        
        return {
            "primary_disaster_type": primary_hazard,
            "confidence": confidence,
            "all_hazards": hazard_votes,
            "sensor_count": len(sensor_results),
            "alert_count": len(alert_results),
            "has_multi_modal": len(sensor_results) > 1 and len(alert_results) > 0,
            "recommendation": self._get_recommendation(primary_hazard, confidence)
        }
    
    def _get_recommendation(self, hazard: str, confidence: float) -> str:
        """Get planning recommendation"""
        if confidence > 0.8:
            return f"High confidence {hazard} - proceed with specific protocol"
        elif confidence > 0.5:
            return f"Moderate confidence {hazard} - activate multi-hazard protocol"
        else:
            return "Low confidence - activate general disaster protocol with broad monitoring"


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.FORMAT_DETECTOR, FormatDetectorAgent())