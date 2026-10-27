# 🔍 CrisisMesh: The Agent That Can Explain Why

> **Open Agent Hackathon 2026 — Track: The Agent That Can Explain Why**
> *Eliminating Black-Box AI in Life-or-Death Emergency Management*

---

## 🚨 The Core Challenge: Why Explainability is a Matter of Life and Death

During catastrophic disasters (flash floods, wildfires, dam collapses, avalanches), emergency management directors and first responders face life-altering decisions. 

In these moments, **a black-box AI recommendation is worse than useless—it is dangerous.** 

If an AI says:
> *"Evacuate Sector 4 and dispatch 6 boats."*

No incident commander will commit limited rescue personnel without knowing:
1. **WHY** is Sector 4 evacuated when current water depth at the gauge shows only 2 feet?
2. **WHY** override an official curfew order issued by the mayor's office?
3. **WHY** dispatch shallow-draft jet boats instead of standard high-clearance military trucks?
4. **WHY** alert cell towers in a 5km downwind cone rather than the entire county?

**CrisisMesh replaces black-box guessing with Auditable, Mathematically Traceable Causal Provenance.** Every alert, asset route, and polygon has an explicit *Explanation Tree* linking raw sensor data, physics simulations, legal SOP rules, and capability constraints.

---

## 🏛️ The Dual-Layer Explainability Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAW INCOMING SIGNALS                              │
│   River Gauges (34ft crest) • Sentinel-1 SAR Radar • 911 Calls • NOAA Feeds │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 WORLD MODEL SIMULATOR (Physics Engine)                      │
│   Calculates water surge velocity (4.2 ft/min) & Downwind Spread Vectors    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│             H-MEM STORE & MARKOVIAN ROUTER (Policy & Timing)                │
│   Evaluates 180s Dead-Man Timer • Retrieves Inter-Jurisdictional SOPs       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                         Candidate Action Plan
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   EVALUATOR AGENT (The Critique Gate)                       │
│   Mathematically evaluates plan against 10 explicit safety criteria:        │
│   • Polygon Precision (>5x blast check)   • Vulnerable Population Check     │
│   • Contradiction Detection               • Capability Matching Rationale   │
│   REJECTS & EXPLAINS WHY ◄─── If score < threshold (Max 3 Critique Loops)   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ PASSED
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  REPORTER AGENT (The Provenance Engine)                     │
│   Produces Comprehensive Audit Report + Causal Explanation Graph            │
│   "WHY this action was taken, WHY alternatives were rejected, and WHEN"     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ 4 Key "Explain Why" Capabilities

### 1. Explaining the 180-Second Dead-Man Switch Override
- **The Disaster Failure:** In the 2025 Texas Flash Flood, alerts sat in a queue for 4 hours while the river rose 34 feet because the on-duty supervisor was asleep.
- **CrisisMesh Explanation:**
  ```json
  {
    "action": "AUTONOMOUS_BROADCAST_TRIGGERED",
    "why_override": "Human supervisor failed to acknowledge critical alert within 180s SLA window.",
    "causal_justification": {
      "trigger_sensor": "Guadalupe River Gauge #1 (value: 34.2 ft, surge: +12 ft/hr)",
      "hazard_velocity": "Water crest arriving at downstream RV park in 14 minutes",
      "legal_basis": "H-Mem SOP Rule TX-EM-7: Autonomous failover authorized when downstream population > 500 and human latency > 3 minutes."
    }
  }
  ```

### 2. Explaining Contradiction Detection & Curfew Overrides
- **The Disaster Failure:** In Derna, Libya (2023), officials ordered citizens to stay indoors under a curfew while the dam upstream was failing, causing thousands of casualties.
- **CrisisMesh Explanation:**
  ```json
  {
    "action": "OFFICIAL_CURFEW_OVERRIDDEN",
    "why_override": "Official messaging contradicts hydraulic reality.",
    "causal_justification": {
      "official_order": "Stay indoors (curfew enforced by local authority)",
      "satellite_evidence": "Sentinel-1 SAR radar confirmed dam crest breach at 01:14Z",
      "simulation_result": "Inundation depth in curfew zone will exceed 3.5m within 22 minutes",
      "critique_decision": "Shelter-in-place inside single-story buildings is fatal. Forcing immediate uphill evacuation."
    }
  }
  ```

### 3. Explaining Capability-Matched Asset Dispatch
- **The Disaster Failure:** In the 2026 Trishuli Tunnel disaster, generic emergency dispatch sent standard fire trucks that could not enter narrow waterlogged tunnels.
- **CrisisMesh Explanation:**
  ```json
  {
    "action": "DISPATCH_CONFINED_SPACE_DMAT",
    "why_chosen": "Hazard requires specialized subsurface respiratory and LiDAR capabilities.",
    "why_alternatives_rejected": {
      "Standard_Fire_Trucks": "Rejected: Access tunnel width (2.8m) and 1.5m standing water.",
      "High_Clearance_4x4": "Rejected: Toxic gas accumulation (CO2 > 800ppm) requires SCBA-certified squads."
    }
  }
  ```

### 4. Explaining Downwind Polygon Bounding
- **The Disaster Failure:** In the 2025 LA Wildfires, cell broadcast sent screeching alarms to 10 million people in downtown LA while residents in the actual fire canyon received zero warnings.
- **CrisisMesh Explanation:**
  ```json
  {
    "action": "RESTRICTED_POLYGON_CELL_BROADCAST",
    "why_bounded": "Evaluator precision gate enforced 1.8x hazard buffer instead of county blast.",
    "causal_justification": {
      "fire_flank": "Santa Ana wind vectors at 48 knots (240 degrees bearing)",
      "calculated_risk_zone": "Downwind canyon polygon (Area: 14.2 sq km)",
      "rejected_county_blast": "Prevented panic across 10M non-affected residents."
    }
  }
  ```

---

## 📊 The 10 Mathematically Audited Safety Criteria

Before any emergency dispatch is executed, the [`EvaluatorAgent`](file:///C:/Users/venka/Gen%20AI%20Hackathon/CrisisMesh/backend/app/agents/evaluator.py) scores the candidate plan against 10 weighted criteria. If any threshold is breached, the agent **explains why it failed** and generates suggested fixes:

| # | Evaluation Criterion | Weight | Threshold | What the Agent Validates & Explains |
|---|----------------------|--------|-----------|-------------------------------------|
| 1 | `polygon_accuracy` | 20% | 0.80 | Bounds danger zone without over/under coverage |
| 2 | `alert_timeliness` | 20% | 0.80 | Dispatched within 180s dead-man switch SLA |
| 3 | `contradiction_caught` | 20% | 0.95 | Explains why conflicting curfew orders were blocked |
| 4 | `polygon_precision` | 15% | 0.80 | Blocks county-wide blasts >5x actual hazard zone |
| 5 | `vulnerable_coverage` | 15% | 0.90 | Explains prioritization of elderly/schools/ground floors |
| 6 | `dispatch_appropriateness` | 15% | 0.80 | Verifies specialized rescue capabilities against terrain |
| 7 | `route_viability` | 10% | 0.70 | Validates evacuation routes are not submerged |
| 8 | `multilingual_coverage` | 10% | 0.80 | Explains why alerts were synthesized in multiple languages |
| 9 | `asset_match_quality` | 10% | 0.75 | Explains equipment suitability for the physical disaster |
| 10 | `sop_compliance` | 10% | 0.85 | Validates adherence to inter-jurisdictional legal mandates |

---

## 📈 Live Auditable Execution Trace (Meterless Telemetry)

Every execution is traced with millisecond timestamps and intermediate inputs/outputs:

```text
[METERLESS] 🟢 Agent:planner            | Op:execute | Trace:f41b7d5d | EXPLAIN: Decomposed 5 evacuation tasks; 180s timer armed
[METERLESS] 🟢 Agent:format_detector    | Op:execute | Trace:edf58804 | EXPLAIN: Classified river gauge CSV + Sentinel-1 SAR GeoJSON
[METERLESS] 🟢 Agent:ingestion_executor | Op:execute | Trace:aae5c90b | EXPLAIN: Normalized coordinates via Zetaris Universal Semantic Layer
[METERLESS] 🟢 Agent:world_model_sim    | Op:execute | Trace:77b0567e | EXPLAIN: Simulated Guadalupe River surge vector (+12ft/hr, downstream 4.2mph)
[METERLESS] 🟢 Agent:markovian_router   | Op:execute | Trace:19d7c2f8 | EXPLAIN: Supervisor timeout reached; autonomous bypass executed
[METERLESS] 🟢 Agent:risk_dispatch      | Op:execute | Trace:1a065bc3 | EXPLAIN: Synthesized 3 alerts (En/Es/Vi); matched 4 shallow boats
[METERLESS] 🟢 Agent:evaluator          | Op:execute | Trace:c4d37faa | EXPLAIN: Validated against 10 safety criteria; Score: 0.92 (PASS)
[METERLESS] 🟢 Agent:reporter           | Op:execute | Trace:93566604 | EXPLAIN: Generated Causal Provenance Audit Report
```

---

## 🚀 Verifying the Explanation Engine Locally

Run the complete pipeline test in sample mode to inspect the live explanation traces:

```bash
cd backend
.venv\Scripts\python.exe test_pipeline.py
```

The system will execute all 9 agents, run the evaluator critique loop, and output the full causal explanation audit trace.
