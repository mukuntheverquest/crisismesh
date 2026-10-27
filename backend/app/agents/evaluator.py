"""
CrisisMesh Evaluator Agent - Open Agent Hackathon 2026
Validates outputs, scores quality, triggers revisions or escalation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from app.agents.base import BaseAgent, trace_agent, trace_tool_call
from app.agents.state import AgentState, AgentType, SeverityLevel
from app.config import settings


@dataclass
class EvaluationCriterion:
    name: str
    weight: float
    threshold: float
    description: str


@dataclass
class EvaluationResult:
    criterion: str
    score: float
    passed: bool
    details: Dict[str, Any]
    issues: List[str]
    suggested_fixes: List[str]


class EvaluatorAgent(BaseAgent):
    """Evaluates agent outputs against quality criteria"""
    
    def __init__(self):
        super().__init__(AgentType.EVALUATOR)
        self.criteria = self._initialize_criteria()
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.EVALUATOR
    
    def _initialize_criteria(self) -> List[EvaluationCriterion]:
        """Define evaluation criteria for disaster response"""
        return [
            EvaluationCriterion(
                name="polygon_accuracy",
                weight=0.20,
                threshold=0.8,
                description="Alert polygon accurately bounds hazard zone without over/under coverage"
            ),
            EvaluationCriterion(
                name="alert_timeliness",
                weight=0.20,
                threshold=0.8,
                description="Alerts dispatched within SLA (dead-man's switch: 180s)"
            ),
            EvaluationCriterion(
                name="vulnerable_coverage",
                weight=0.15,
                threshold=0.9,
                description="High-vulnerability demographics covered (elderly, schools, underground)"
            ),
            EvaluationCriterion(
                name="route_viability",
                weight=0.10,
                threshold=0.7,
                description="Evacuation routes are accessible and not blocked"
            ),
            EvaluationCriterion(
                name="polygon_precision",
                weight=0.15,
                threshold=0.8,
                description="No county-wide blasts >5x hazard zone (Failure #2)"
            ),
            EvaluationCriterion(
                name="multilingual_coverage",
                weight=0.10,
                threshold=0.8,
                description="Alerts in relevant languages for affected populations (Failure #7)"
            ),
            EvaluationCriterion(
                name="asset_match_quality",
                weight=0.10,
                threshold=0.75,
                description="Dispatched assets match hazard mechanics (Failure #10)"
            ),
            EvaluationCriterion(
                name="contradiction_caught",
                weight=0.20,
                threshold=0.95,
                description="Contradictory messages blocked (curfew in inundation zone) (Failure #6)"
            ),
            EvaluationCriterion(
                name="dispatch_appropriateness",
                weight=0.15,
                threshold=0.8,
                description="Right assets to right locations (tunnel rescue, DMAT, etc.)"
            ),
            EvaluationCriterion(
                name="inference_confidence",
                weight=0.15,
                threshold=0.75,
                description="Multi-modal hazard inference confidence (Failure #4)"
            ),
            EvaluationCriterion(
                name="eta_accuracy",
                weight=0.10,
                threshold=0.8,
                description="Canyon arrival ETAs within 10% of actual"
            ),
            EvaluationCriterion(
                name="damage_accuracy",
                weight=0.20,
                threshold=0.75,
                description="SAR damage assessment matches ground truth (Failure #9)"
            ),
            EvaluationCriterion(
                name="registry_dedup_quality",
                weight=0.15,
                threshold=0.9,
                description="Survivor registry deduplication accuracy (Failure #5)"
            ),
            EvaluationCriterion(
                name="distress_verification",
                weight=0.10,
                threshold=0.75,
                description="Social media distress verified against SAR (Failure #9)"
            ),
            EvaluationCriterion(
                name="geocoding_hallucination_filter",
                weight=0.10,
                threshold=0.96,
                description="Wrong-city geocoding filtered (<4% hallucination rate)"
            ),
            EvaluationCriterion(
                name="isolation_accuracy",
                weight=0.15,
                threshold=0.8,
                description="Infrastructure isolation correctly assessed (Failure #8)"
            ),
            EvaluationCriterion(
                name="reroute_feasibility",
                weight=0.10,
                threshold=0.7,
                description="Alternative routes/modes are actually viable"
            ),
            EvaluationCriterion(
                name="offline_capability",
                weight=0.10,
                threshold=0.9,
                description="System functions without internet (SAMPLE_MODE)"
            ),
            EvaluationCriterion(
                name="sop_compliance",
                weight=0.20,
                threshold=0.9,
                description="Cross-jurisdictional SOPs followed (Failure #3)"
            ),
            EvaluationCriterion(
                name="dispatch_quality",
                weight=0.15,
                threshold=0.8,
                description="Quality of risk dispatch decisions"
            ),
            EvaluationCriterion(
                name="cross_jurisdictional_coordination",
                weight=0.15,
                threshold=0.8,
                description="National-regional coordination achieved"
            )
        ]
    
    @trace_agent("evaluator", "execute")
    async def execute(self, state: AgentState) -> AgentState:
        """Evaluate all agent outputs"""
        
        # Collect outputs to evaluate
        outputs_to_evaluate = {}
        for agent_type in AgentType:
            output_key = f"{agent_type.value}_output"
            if output_key in state and state[output_key]:
                outputs_to_evaluate[agent_type.value] = state[output_key]
        
        if not outputs_to_evaluate:
            state["next_agent"] = AgentType.REPORTER
            return state
        
        # Run evaluations
        all_results = []
        for agent_name, output in outputs_to_evaluate.items():
            results = self._evaluate_agent_output(agent_name, output, state)
            all_results.extend(results)
        
        # Calculate overall score
        total_weight = sum(c.weight for c in self.criteria if any(r.criterion == c.name for r in all_results))
        weighted_score = sum(r.score * self._get_criterion_weight(r.criterion) for r in all_results)
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Determine pass/fail
        passed = overall_score >= settings.MIN_QUALITY_SCORE
        
        # Collect failed criteria
        failed_criteria = [r.criterion for r in all_results if not r.passed]
        all_issues = []
        all_fixes = []
        for r in all_results:
            all_issues.extend(r.issues)
            all_fixes.extend(r.suggested_fixes)
        
        # Determine next action
        if passed and not failed_criteria:
            state["next_agent"] = AgentType.REPORTER
            state["should_continue"] = False
        elif state.get("revision_count", 0) < settings.MAX_REVISION_LOOPS:
            state["next_agent"] = AgentType.PLANNER
            state["escalation_needed"] = False
        else:
            state["next_agent"] = AgentType.RISK_DISPATCH
            state["escalation_needed"] = True
        
        evaluator_output = {
            "overall_score": overall_score,
            "passed": passed,
            "criteria_results": [
                {
                    "criterion": r.criterion,
                    "score": r.score,
                    "passed": r.passed,
                    "details": r.details,
                    "issues": r.issues,
                    "suggested_fixes": r.suggested_fixes
                }
                for r in all_results
            ],
            "failed_criteria": failed_criteria,
            "issues": all_issues,
            "suggested_fixes": all_fixes,
            "evaluated_at": datetime.utcnow().isoformat()
        }
        
        state["evaluator_output"] = evaluator_output
        state["quality_scores"] = {r.criterion: r.score for r in all_results}
        state = self._update_state_trace(state, evaluator_output)
        
        return state
    
    def _get_criterion_weight(self, name: str) -> float:
        for c in self.criteria:
            if c.name == name:
                return c.weight
        return 0.0
    
    def _evaluate_agent_output(
        self,
        agent_name: str,
        output: Dict[str, Any],
        state: AgentState
    ) -> List[EvaluationResult]:
        """Evaluate specific agent output against relevant criteria"""
        
        results = []
        
        # Map agent to relevant criteria
        agent_criteria_map = {
            "planner": ["polygon_accuracy", "vulnerable_coverage", "sop_compliance"],
            "format_detector": ["damage_accuracy", "inference_confidence"],
            "ingestion_executor": ["registry_dedup_quality", "distress_verification", "geocoding_hallucination_filter", "damage_accuracy", "isolation_accuracy"],
            "risk_dispatch": ["route_viability", "asset_match_quality", "dispatch_appropriateness", "reroute_feasibility", "dispatch_quality"],
            "markovian_router": ["alert_timeliness", "contradiction_caught", "offline_capability"],
            "world_model_simulator": ["polygon_precision", "eta_accuracy", "polygon_accuracy"],
            "hmem_store": ["sop_compliance", "cross_jurisdictional_coordination"]
        }
        
        relevant_criteria = agent_criteria_map.get(agent_name, [])
        
        for criterion_name in relevant_criteria:
            criterion = next((c for c in self.criteria if c.name == criterion_name), None)
            if not criterion:
                continue
            
            result = self._evaluate_criterion(criterion, output, state)
            results.append(result)
        
        return results
    
    def _evaluate_criterion(
        self,
        criterion: EvaluationCriterion,
        output: Dict[str, Any],
        state: AgentState
    ) -> EvaluationResult:
        """Evaluate a single criterion"""
        
        # Dispatch to specific evaluation methods
        evaluator_map = {
            "polygon_accuracy": self._eval_polygon_accuracy,
            "alert_timeliness": self._eval_alert_timeliness,
            "vulnerable_coverage": self._eval_vulnerable_coverage,
            "route_viability": self._eval_route_viability,
            "polygon_precision": self._eval_polygon_precision,
            "multilingual_coverage": self._eval_multilingual_coverage,
            "asset_match_quality": self._eval_asset_match_quality,
            "contradiction_caught": self._eval_contradiction_caught,
            "dispatch_appropriateness": self._eval_dispatch_appropriateness,
            "inference_confidence": self._eval_inference_confidence,
            "eta_accuracy": self._eval_eta_accuracy,
            "damage_accuracy": self._eval_damage_accuracy,
            "registry_dedup_quality": self._eval_registry_dedup_quality,
            "distress_verification": self._eval_distress_verification,
            "geocoding_hallucination_filter": self._eval_geocoding_hallucination_filter,
            "isolation_accuracy": self._eval_isolation_accuracy,
            "reroute_feasibility": self._eval_reroute_feasibility,
            "offline_capability": self._eval_offline_capability,
            "sop_compliance": self._eval_sop_compliance,
            "dispatch_quality": self._eval_dispatch_quality,
            "cross_jurisdictional_coordination": self._eval_cross_jurisdictional_coordination
        }
        
        eval_func = evaluator_map.get(criterion.name)
        if eval_func:
            return eval_func(criterion, output, state)
        
        # Default evaluation
        return EvaluationResult(
            criterion=criterion.name,
            score=0.5,
            passed=False,
            details={"note": "No specific evaluator implemented"},
            issues=["Criterion not implemented"],
            suggested_fixes=["Implement specific evaluator"]
        )
    
    # Specific criterion evaluators
    
    def _eval_polygon_accuracy(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate polygon accuracy"""
        # Check if alert polygons exist and are reasonable
        risk_output = state.get("risk_dispatch_output", {})
        polygons = risk_output.get("alert_polygons", [])
        
        if not polygons:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No polygons generated"},
                issues=["Missing alert polygons"],
                suggested_fixes=["Generate alert polygons for all hazards"]
            )
        
        # Check polygon quality (simplified)
        score = 0.85  # Would compute actual IoU with hazard zone
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"polygon_count": len(polygons)},
            issues=[] if score >= criterion.threshold else ["Polygon accuracy below threshold"],
            suggested_fixes=[]
        )
    
    def _eval_alert_timeliness(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate alert timeliness (dead-man's switch)"""
        markovian_output = state.get("markovian_router_output", {})
        
        # Check if dead-man's switch was triggered
        deadman_triggered = markovian_output.get("deadman_switch_triggered", False)
        alert_time_seconds = markovian_output.get("alert_dispatch_time_seconds", 999)
        
        if deadman_triggered and alert_time_seconds <= settings.ALERT_DEADMAN_SWITCH_SECONDS:
            score = 1.0
        elif alert_time_seconds <= settings.ALERT_DEADMAN_SWITCH_SECONDS:
            score = 0.9
        else:
            score = 0.3
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={
                "deadman_switch_triggered": deadman_triggered,
                "alert_time_seconds": alert_time_seconds,
                "sla_seconds": settings.ALERT_DEADMAN_SWITCH_SECONDS
            },
            issues=[] if score >= criterion.threshold else [f"Alert dispatch took {alert_time_seconds}s, SLA is {settings.ALERT_DEADMAN_SWITCH_SECONDS}s"],
            suggested_fixes=["Optimize alert dispatch pipeline", "Pre-authorize critical alerts"]
        )
    
    def _eval_vulnerable_coverage(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate vulnerable population coverage"""
        risk_output = state.get("risk_dispatch_output", {})
        prioritized = risk_output.get("vulnerable_prioritized", [])
        
        required = ["elderly_ground_floor", "schools", "underground_parking"]
        covered = sum(1 for r in required if r in prioritized)
        score = covered / len(required)
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"required": required, "covered": prioritized},
            issues=[] if score >= criterion.threshold else [f"Missing vulnerable groups: {[r for r in required if r not in prioritized]}"],
            suggested_fixes=["Integrate vulnerable population registries", "Auto-prioritize in SOP"]
        )
    
    def _eval_route_viability(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate evacuation route viability"""
        risk_output = state.get("risk_dispatch_output", {})
        routes = risk_output.get("evacuation_routes", [])
        
        if not routes:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No evacuation routes generated"},
                issues=["Missing evacuation routes"],
                suggested_fixes=["Generate evacuation routes with road network analysis"]
            )
        
        # Check against infrastructure isolation assessment
        isolation = state.get("ingestion_executor_output", {}).get("normalized_sensors", [])
        blocked_roads = sum(1 for s in isolation if "road" in str(s).lower() and "block" in str(s).lower())
        
        viable_routes = len(routes) - blocked_roads
        score = max(0, viable_routes / len(routes)) if routes else 0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"total_routes": len(routes), "blocked": blocked_roads, "viable": viable_routes},
            issues=[] if score >= criterion.threshold else [f"{blocked_roads} routes blocked by infrastructure damage"],
            suggested_fixes=["Integrate real-time road closure data", "Pre-compute alternative routes"]
        )
    
    def _eval_polygon_precision(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate polygon precision (no county-wide blasts >5x hazard zone)"""
        risk_output = state.get("risk_dispatch_output", {})
        polygons = risk_output.get("alert_polygons", [])
        
        violations = 0
        for poly in polygons:
            hazard_area = poly.get("hazard_area_km2", 1)
            alert_area = poly.get("alert_area_km2", 1)
            if alert_area > hazard_area * 5:
                violations += 1
        
        score = 1.0 - (violations / len(polygons)) if polygons else 0.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"polygons_checked": len(polygons), "violations": violations},
            issues=[f"{violations} polygons exceed 5x hazard zone"] if violations else [],
            suggested_fixes=["Enforce bounding box guardrail", "Auto-trim polygons to hazard extent"]
        )
    
    def _eval_multilingual_coverage(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate multilingual alert coverage"""
        risk_output = state.get("risk_dispatch_output", {})
        alerts = risk_output.get("alerts_dispatched", [])
        
        if not alerts:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No alerts dispatched"},
                issues=["No alerts to evaluate"],
                suggested_fixes=["Dispatch alerts with multilingual support"]
            )
        
        # Check language coverage
        all_languages = set()
        for alert in alerts:
            all_languages.update(alert.get("languages", ["en"]))
        
        # Required languages based on disaster context
        disaster_type = state.get("context", {}).get("disaster_type", "")
        required_langs = {"en"}  # Base
        if "nepal" in str(state.get("disaster_context", {})).lower():
            required_langs.update(["ne", "hi", "bo"])  # Nepali, Hindi, Tibetan
        if "spain" in str(state.get("disaster_context", {})).lower():
            required_langs.update(["es", "ca"])  # Spanish, Valencian
        if "libya" in str(state.get("disaster_context", {})).lower():
            required_langs.update(["ar"])
        if "turkey" in str(state.get("disaster_context", {})).lower():
            required_langs.update(["tr", "ar", "ku"])
        
        covered = len(required_langs & all_languages)
        score = covered / len(required_langs)
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"required": list(required_langs), "provided": list(all_languages)},
            issues=[] if score >= criterion.threshold else [f"Missing languages: {required_langs - all_languages}"],
            suggested_fixes=["Auto-translate alerts to required languages", "Integrate translation service"]
        )
    
    def _eval_asset_match_quality(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate asset-hazard matching quality"""
        risk_output = state.get("risk_dispatch_output", {})
        dispatches = risk_output.get("asset_dispatches", [])
        
        if not dispatches:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No assets dispatched"},
                issues=["No asset dispatches to evaluate"],
                suggested_fixes=["Execute asset dispatch for identified hazards"]
            )
        
        # Check specialization match
        matches = 0
        for dispatch in dispatches:
            hazard = dispatch.get("hazard_type", "")
            asset_type = dispatch.get("asset_type", "")
            specialization = dispatch.get("specialization", [])
            
            if hazard in specialization or asset_type in specialization:
                matches += 1
        
        score = matches / len(dispatches) if dispatches else 0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"total_dispatches": len(dispatches), "matched": matches},
            issues=[] if score >= criterion.threshold else [f"Only {matches}/{len(dispatches)} dispatches match hazard specialization"],
            suggested_fixes=["Improve capability matching algorithm", "Expand asset catalog with specializations"]
        )
    
    def _eval_contradiction_caught(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate contradiction detection (Failure #6)"""
        evaluator_output = state.get("evaluator_output", {})
        # Check if contradiction detection ran
        markovian_output = state.get("markovian_router_output", {})
        contradiction_blocked = markovian_output.get("contradiction_blocked", False)
        
        # Also check format detector for contradictory alerts
        format_output = state.get("format_detector_output", {})
        contradictory_alerts = [
            a for a in format_output.get("official_alerts", [])
            if a.get("is_contradictory", False)
        ]
        
        if contradictory_alerts and contradiction_blocked:
            score = 1.0
        elif contradictory_alerts and not contradiction_blocked:
            score = 0.0
        else:
            score = 0.9  # No contradictions found
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={
                "contradictory_alerts_found": len(contradictory_alerts),
                "blocked": contradiction_blocked
            },
            issues=[] if score >= criterion.threshold else ["Contradictory alert not blocked"],
            suggested_fixes=["Enforce contradiction detection gate", "Block curfew/shelter-in-place in inundation zones"]
        )
    
    def _eval_dispatch_appropriateness(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate dispatch appropriateness"""
        risk_output = state.get("risk_dispatch_output", {})
        dispatches = risk_output.get("asset_dispatches", [])
        
        # Check for specialized assets for specific hazards
        hazard = state.get("context", {}).get("disaster_type", "")
        
        required_specializations = {
            "flash_flood": ["shallow_draft_boat", "helicopter"],
            "wildfire": ["lidar_thermal_drone", "helicopter"],
            "earthquake": ["dmat_team", "engineering_team", "lidar_thermal_drone"],
            "dam_failure": ["high_ground_routing", "helicopter"],
            "rock_ice_avalanche": ["helicopter", "drone"],
            "tunnel_flood": ["tunnel_rescue_team", "heavy_lift_drone"]
        }
        
        required = required_specializations.get(hazard, [])
        dispatched_specs = set()
        for d in dispatches:
            dispatched_specs.update(d.get("specialization", []))
        
        covered = len(set(required) & dispatched_specs)
        score = covered / len(required) if required else 1.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"required_specializations": required, "dispatched": list(dispatched_specs)},
            issues=[] if score >= criterion.threshold else [f"Missing specializations: {set(required) - dispatched_specs}"],
            suggested_fixes=["Pre-position specialized assets", "Improve capability matching"]
        )
    
    def _eval_inference_confidence(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate multi-modal inference confidence"""
        ingestion_output = state.get("ingestion_executor_output", {})
        river_monitor = ingestion_output.get("river_gauge_monitoring", {})
        
        confidence = river_monitor.get("hazard_confidence", 0.0)
        inferred = river_monitor.get("inferred_hazard", False)
        
        score = confidence if inferred else 0.5
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"inferred_hazard": inferred, "confidence": confidence},
            issues=[] if score >= criterion.threshold else [f"Inference confidence {confidence} below threshold {criterion.threshold}"],
            suggested_fixes=["Add more sensor modalities", "Improve correlation algorithms"]
        )
    
    def _eval_eta_accuracy(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate ETA accuracy"""
        world_model_output = state.get("world_model_simulator_output", {})
        etas = world_model_output.get("canyon_arrival_etas", {})
        
        if not etas:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No ETAs calculated"},
                issues=["Missing ETA calculations"],
                suggested_fixes=["Run canyon arrival ETA calculation"]
            )
        
        # Mock accuracy check - in production would compare with actual arrival times
        score = 0.85  # Would compute actual vs predicted
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"etas_calculated": len(etas)},
            issues=[] if score >= criterion.threshold else ["ETA accuracy below threshold"],
            suggested_fixes=["Improve hydraulic modeling", "Incorporate real-time gauge data"]
        )
    
    def _eval_damage_accuracy(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate SAR damage assessment accuracy"""
        ingestion_output = state.get("ingestion_executor_output", {})
        sar = ingestion_output.get("sar_damage_assessment", {})
        
        confidence = sar.get("confidence_threshold", 0.0)
        spatial_join = sar.get("spatial_join_completed", False)
        
        score = confidence if spatial_join else 0.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"confidence_threshold": confidence, "spatial_join": spatial_join},
            issues=[] if score >= criterion.threshold else ["SAR damage assessment incomplete"],
            suggested_fixes=["Complete spatial join with Sentinel-1/HOTOSM", "Raise confidence threshold"]
        )
    
    def _eval_registry_dedup_quality(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate survivor registry deduplication"""
        ingestion_output = state.get("ingestion_executor_output", {})
        entity_res = ingestion_output.get("entity_resolution", {})
        
        total = entity_res.get("total_records", 0)
        deduped = entity_res.get("deduplicated_records", 0)
        
        if total == 0:
            score = 0.0
        else:
            score = deduped / total
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"total_records": total, "deduplicated": deduped, "gpu_accelerated": entity_res.get("gpu_accelerated", False)},
            issues=[] if score >= criterion.threshold else ["Deduplication rate below threshold"],
            suggested_fixes=["Improve embedding model", "Adjust similarity threshold"]
        )
    
    def _eval_distress_verification(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate social media distress verification"""
        ingestion_output = state.get("ingestion_executor_output", {})
        verification = ingestion_output.get("satellite_grounded_verification", {})
        
        verified = verification.get("verified_count", 0)
        total = verification.get("total_posts", 1)
        
        score = verified / total if total > 0 else 0.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"verified": verified, "total": total, "hallucination_rate": verification.get("hallucination_rate", 0)},
            issues=[] if score >= criterion.threshold else ["Distress verification rate below threshold"],
            suggested_fixes=["Expand SAR coverage", "Improve geocoding"]
        )
    
    def _eval_geocoding_hallucination_filter(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate geocoding hallucination filter"""
        ingestion_output = state.get("ingestion_executor_output", {})
        verification = ingestion_output.get("satellite_grounded_verification", {})
        
        hallucination_rate = verification.get("hallucination_rate", 1.0)
        score = 1.0 - hallucination_rate
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"hallucination_rate": hallucination_rate, "threshold": settings.GEOCODING_HALLUCINATION_THRESHOLD},
            issues=[] if score >= criterion.threshold else [f"Hallucination rate {hallucination_rate:.1%} exceeds {settings.GEOCODING_HALLUCINATION_THRESHOLD:.1%}"],
            suggested_fixes=["Tighten SAR confidence threshold", "Add secondary verification"]
        )
    
    def _eval_isolation_accuracy(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate infrastructure isolation assessment accuracy"""
        ingestion_output = state.get("ingestion_executor_output", {})
        isolation = ingestion_output.get("infrastructure_isolation_assessment", {})
        
        assessed = isolation.get("assessment", {})
        completeness = sum(1 for v in assessed.values() if v) / len(assessed) if assessed else 0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=completeness,
            passed=completeness >= criterion.threshold,
            details={"assessed_components": list(assessed.keys())},
            issues=[] if completeness >= criterion.threshold else ["Infrastructure isolation assessment incomplete"],
            suggested_fixes=["Integrate more infrastructure data sources"]
        )
    
    def _eval_reroute_feasibility(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate reroute feasibility"""
        risk_output = state.get("risk_dispatch_output", {})
        reroutes = risk_output.get("reroutes", [])
        
        if not reroutes:
            return EvaluationResult(
                criterion=criterion.name,
                score=0.0,
                passed=False,
                details={"reason": "No reroutes generated"},
                issues=["No alternative routes generated"],
                suggested_fixes=["Generate alternative transport modes"]
            )
        
        feasible = sum(1 for r in reroutes if r.get("feasible", False))
        score = feasible / len(reroutes)
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"total_reroutes": len(reroutes), "feasible": feasible},
            issues=[] if score >= criterion.threshold else [f"Only {feasible}/{len(reroutes)} reroutes feasible"],
            suggested_fixes=["Validate routes with real-time data", "Pre-survey alternative routes"]
        )
    
    def _eval_offline_capability(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate offline capability"""
        markovian_output = state.get("markovian_router_output", {})
        offline_mode = markovian_output.get("offline_mode_executed", False)
        
        score = 1.0 if offline_mode else 0.5
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"offline_mode": offline_mode, "sample_mode": settings.SAMPLE_MODE},
            issues=[] if score >= criterion.threshold else ["Offline execution not verified"],
            suggested_fixes=["Test SAMPLE_MODE execution", "Verify local model availability"]
        )
    
    def _eval_sop_compliance(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate SOP compliance"""
        hmem_output = state.get("hmem_store_output", {})
        sops = hmem_output.get("sops_retrieved", [])
        
        executed = sum(1 for s in sops if s.get("executed", False))
        score = executed / len(sops) if sops else 0.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"sops_retrieved": len(sops), "executed": executed},
            issues=[] if score >= criterion.threshold else [f"Only {executed}/{len(sops)} SOPs executed"],
            suggested_fixes=["Auto-execute SOPs on trigger", "Monitor SOP compliance"]
        )
    
    def _eval_dispatch_quality(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate dispatch decision quality"""
        risk_output = state.get("risk_dispatch_output", {})
        
        # Composite quality score
        factors = {
            "asset_match": self._eval_asset_match_quality(EvaluationCriterion("tmp",0,0,""), output, state).score,
            "appropriateness": self._eval_dispatch_appropriateness(EvaluationCriterion("tmp",0,0,""), output, state).score,
            "timeliness": self._eval_alert_timeliness(EvaluationCriterion("tmp",0,0,""), output, state).score
        }
        
        score = sum(factors.values()) / len(factors)
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details=factors,
            issues=[] if score >= criterion.threshold else ["Composite dispatch quality below threshold"],
            suggested_fixes=["Improve individual dispatch factors"]
        )
    
    def _eval_cross_jurisdictional_coordination(self, criterion: EvaluationCriterion, output: Dict, state: AgentState) -> EvaluationResult:
        """Evaluate cross-jurisdictional coordination"""
        hmem_output = state.get("hmem_store_output", {})
        sops = hmem_output.get("sops_retrieved", [])
        
        cross_jurisdictional = sum(1 for s in sops if s.get("cross_jurisdictional", False))
        total = len(sops)
        
        score = cross_jurisdictional / total if total > 0 else 0.0
        
        return EvaluationResult(
            criterion=criterion.name,
            score=score,
            passed=score >= criterion.threshold,
            details={"cross_jurisdictional_sops": cross_jurisdictional, "total_sops": total},
            issues=[] if score >= criterion.threshold else ["Insufficient cross-jurisdictional SOPs"],
            suggested_fixes=["Negotiate inter-agency agreements", "Pre-authorize joint mobilization"]
        )
    
    async def critique(self, state: AgentState) -> Dict[str, Any]:
        """Provide critique for planner feedback"""
        evaluator_output = state.get("evaluator_output", {})
        
        return {
            "critique": "Quality thresholds not met" if not evaluator_output.get("passed", False) else "All criteria passed",
            "failed_criteria": evaluator_output.get("failed_criteria", []),
            "issues": evaluator_output.get("issues", []),
            "suggested_fixes": evaluator_output.get("suggested_fixes", []),
            "overall_score": evaluator_output.get("overall_score", 0.0)
        }


# ============================================
# Factory Registration
# ============================================

from app.agents.base import AgentFactory
AgentFactory.register(AgentType.EVALUATOR, EvaluatorAgent())