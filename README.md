# CrisisMesh - Disaster Management Multi-Agent System

**Open Agent Hackathon 2026 - Track 1: Solving Fragmented Intelligence**

CrisisMesh is a multi-agent disaster management system that addresses 10 real-world disaster failure archetypes through autonomous agent orchestration, sponsor technology integration, and offline-capable execution.

## 🎯 Problem: Fragmented Intelligence in Disaster Response

Recent disasters reveal systemic failures in how intelligence flows during crises:

| # | Failure Archetype | Disaster Example | Key Gap |
|---|-------------------|------------------|---------|
| 1 | Sleeping Supervisor & Manual Approval Bottleneck | Texas Flash Floods 2025 | 4-hour alert delay |
| 2 | Polygon Target Miss & Single-Operator Overload | LA Wildfires 2025 | 10M false alerts, zero alerts to death zone |
| 3 | Forecast-to-Governance Disconnect | Valencia DANA 2024 | 13-hour gap: Red Alert → Phone Alert |
| 4 | Sensor Destruction & Single-Modality Blindness | Nepal Bhote Koshi 2026 | Gauges destroyed in 7 min, relied on water thresholds |
| 5 | Manual PDF-to-CSV Nightmares | Nepal Floods 2026 | 3 incompatible rescued figures |
| 6 | Contradictory Official Messaging | Derna Dam Collapse 2023 | Curfew → "Dams OK" → Evacuation (19 min after collapse) |
| 7 | Unilingual Generic Boilerplate Alerts | Nepal Floods 2026 | Nepali-only alerts on trekking route, 636 foreigners missing |
| 8 | Total Telecom/Power/Road Isolation | Hurricane Helene 2024 | 11 NC counties isolated, landslides block tower access |
| 9 | Social Media Distress Overload | Türkiye Earthquake 2023 | 1.8M tweets/12hr, 4% geocoding hallucinations |
| 10 | High-Tech Dashboards vs Field Equipment | Trishuli Tunnels 2026 | 500 workers trapped, only smartphone flashlights |

## 🏗️ Architecture: Multi-Agent LangGraph Orchestration

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Planner    │───▶│ Format Detector  │───▶│ Ingestion Executor  │
│  Agent      │    │ Agent            │    │ Agent (GPU)         │
└─────────────┘    └──────────────────┘    └──────────┬──────────┘
                                                       │
                         ┌─────────────────────────────┼─────────────────────────────┐
                         ▼                             ▼                             ▼
                  ┌─────────────┐               ┌─────────────┐               ┌─────────────┐
                  │ World Model │               │ Markovian   │               │ H-Mem Store │
                  │ Simulator   │               │ Router      │               │             │
                  └──────┬──────┘               └──────┬──────┘               └──────┬──────┘
                         │                             │                             │
                         └─────────────────────────────┼─────────────────────────────┘
                                                       ▼
                                              ┌─────────────┐
                                              │ Risk        │
                                              │ Dispatch    │
                                              └──────┬──────┘
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │ Evaluator   │
                                              │ Agent       │
                                              └──────┬──────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    ▼                                ▼                                ▼
              ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
              │   Passed    │                 │  Failed <   │                 │  Max Revs   │
              │             │                 │  Max Revs   │                 │  Reached    │
              └──────┬──────┘                 └──────┬──────┘                 └──────┬──────┘
                     │                               │                               │
                     ▼                               ▼                               ▼
              ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
              │  Reporter   │                 │  Planner    │                 │ Risk Dispatch│
              │  (Final)    │                 │  (Revise)   │                 │ (Escalate)  │
              └─────────────┘                 └─────────────┘                 └─────────────┘
```

## 🤖 9 Specialized Agents

| Agent | Purpose | Key Capability |
|-------|---------|----------------|
| **PlannerAgent** | Decompose goals into task graphs | Dynamic routing, deadline-aware |
| **FormatDetectorAgent** | Classify sensor/social/alert formats | Multi-modal, filetype detection |
| **IngestionExecutorAgent** | Normalize & deduplicate data | GPU embeddings, Zetaris USL, SAR join |
| **WorldModelSimulatorAgent** | Simulate hazard propagation | Wind/water vectors, downstream ETAs |
| **MarkovianRouterAgent** | Autonomous alert dispatch | 180s dead-man's switch, state routing |
| **HMemStoreAgent** | Cross-jurisdictional SOPs | Long-term memory, legal basis encoding |
| **RiskDispatchAgent** | Alerts, assets, evacuations | Multilingual, capability-matched |
| **EvaluatorAgent** | Quality gates & contradiction detection | 10 criteria, polygon guardrails |
| **ReporterAgent** | Final report with provenance | Executive summary, lessons learned |

## 🔧 Sponsor Technology Integration

| Sponsor | Integration | CrisisMesh Usage |
|---------|-------------|------------------|
| **Zetaris** | Universal Semantic Layer | Federated disaster data queries, schema registry, lineage tracking |
| **Meterless** | Agent Observability | H-Mem store, Markovian router, World Model simulator traces |
| **NVIDIA** | GPU Acceleration | CUDA embeddings (sentence-transformers), entity resolution, risk reasoning |
| **Cursor** | AI-Native IDE | Space XAI, code generation, debugging |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional, uses SQLite fallback in SAMPLE_MODE)
- Docker (optional, for full stack)

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed (SAMPLE_MODE=true by default)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker (Full Stack)
```bash
docker-compose up -d
```

## 📡 API Endpoints

### Disaster Response
- `POST /api/v1/disaster/respond` - Initiate async disaster response
- `POST /api/v1/disaster/respond/sync` - Synchronous response (testing)
- `GET /api/v1/disaster/respond/{job_id}` - Get job status
- `GET /api/v1/disaster/respond/{job_id}/trace` - Get agent traces

### Scenarios
- `GET /api/v1/scenarios` - List 10 disaster scenarios
- `POST /api/v1/scenarios/{scenario_id}/run` - Run scenario

### Demo Data
- `GET /api/v1/demo/sample-sensor-data` - Sample sensor readings
- `GET /api/v1/demo/sample-social-media` - Sample social posts
- `GET /api/v1/demo/sample-alerts` - Sample official alerts

### Health & Visualization
- `GET /health` - Health check
- `GET /api/v1/graph/visualize` - Mermaid graph diagram

## 🧪 Testing Scenarios

Each scenario maps to a real disaster failure:

```bash
# Run Texas Flash Flood (Dead-Man's Switch test)
curl -X POST http://localhost:8000/api/v1/scenarios/texas_flash_flood_2025/run

# Run LA Wildfires (Polygon Guardrail test)
curl -X POST http://localhost:8000/api/v1/scenarios/la_wildfires_2025/run

# Run Valencia DANA (Forecast-Governance test)
curl -X POST http://localhost:8000/api/v1/scenarios/valencia_dana_2024/run

# Run Nepal Bhote Koshi (Sensor Destruction test)
curl -X POST http://localhost:8000/api/v1/scenarios/nepal_bhote_koshi_2026/run

# Run Derna Dam (Contradiction Detection test)
curl -X POST http://localhost:8000/api/v1/scenarios/derna_dam_2023/run
```

## 📊 Sample Response Output

```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "final_output": {
    "report": {
      "executive_summary": "CrisisMesh executed Flash Flood response at CRITICAL severity. Dispatched 3 alert(s) via multi-system (IPAWS/ES-Alert/Genasys/VHF/Siren). Deployed 2 specialized asset(s) matched to hazard mechanics. Quality assessment: PASSED. Cross-jurisdictional SOPs activated from H-Mem long-term memory.",
      "alert_dispatch": {
        "deadman_switch": { "triggered": true, "supervisor_acknowledged": false, "timeout_seconds": 180 },
        "multilingual_alerts": { "languages": ["en", "es", "hi"], "count": 3 },
        "polygon_management": { "auto_expanded": true, "county_wide_blasts_prevented": true }
      },
      "evacuation_operations": { "total_capacity": 1500, "high_ground_routes": 2 },
      "asset_deployment": { "assets_dispatched": 2, "capability_matched": true },
      "data_ingestion": { "sensor_readings_ingested": 5, "survivor_registry_dedup": { "gpu_accelerated": true } }
    },
    "quality_summary": { "overall_score": 0.92, "passed": true },
    "provenance": { "agent_trace": {...} }
  }
}
```

## 🔑 Environment Variables

```bash
# Application
APP_NAME=CrisisMesh
APP_VERSION=1.0.0
ENVIRONMENT=development
SAMPLE_MODE=true

# Zetaris
ZETARIS_URL=https://api.zetaris.com
ZETARIS_API_KEY=your_key
ZETARIS_ORG_ID=your_org
ZETARIS_WORKSPACE_ID=your_workspace

# Meterless
METERLESS_URL=https://api.meterless.ai
METERLESS_API_KEY=your_key
METERLESS_PROJECT_ID=your_project

# NVIDIA
USE_GPU=true
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=meta-llama/Llama-3-8B-Instruct

# Database
DATABASE_URL=sqlite+aiosqlite:///data/crisismesh.db
REDIS_URL=redis://localhost:6379

# External APIs
NWS_API_URL=https://api.weather.gov
USGS_API_URL=https://earthquake.usgs.gov
SENTINEL_HUB_API_URL=https://services.sentinel-hub.com
HOTOSM_API_URL=https://hotosm.org/api
```

## 📁 Project Structure

```
CrisisMesh/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base.py              # Base agent classes, tracing decorators
│   │   │   ├── state.py             # LangGraph AgentState, types
│   │   │   ├── planner.py           # PlannerAgent
│   │   │   ├── evaluator.py         # EvaluatorAgent
│   │   │   ├── risk_agent.py        # RiskDispatchAgent
│   │   │   ├── reporter.py          # ReporterAgent
│   │   │   ├── domain_agents/
│   │   │   │   ├── format_detector.py
│   │   │   │   ├── ingestion_executor.py
│   │   │   │   ├── markovian_router.py
│   │   │   │   ├── world_model_simulator.py
│   │   │   │   └── hmem_store.py
│   │   │   └── graph.py             # LangGraph orchestration
│   │   ├── integrations/
│   │   │   ├── zetaris_client.py    # Zetaris USL client
│   │   │   └── meterless_client.py  # Meterless observability
│   │   ├── ml/
│   │   │   └── nvidia_inference.py  # GPU embeddings, LLM
│   │   ├── api/routes/              # FastAPI routes
│   │   ├── config.py                # Pydantic settings
│   │   └── main.py                  # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx        # Main dashboard
│   │   │   ├── ScenarioTester.tsx   # Scenario testing UI
│   │   │   ├── JobDetails.tsx       # Job detail with traces
│   │   │   ├── MapView.tsx          # Leaflet map
│   │   │   └── Layout.tsx           # App layout
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios client
│   │   │   └── utils.ts             # Utilities
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🏆 Hackathon Submission

**Track 1: Solving Fragmented Intelligence**
- ✅ Multi-agent architecture with shared memory & feedback loops
- ✅ 10 real-world disaster failure archetypes addressed
- ✅ Sponsor tech: Zetaris, Meterless, NVIDIA, Cursor
- ✅ Offline-capable (SAMPLE_MODE)
- ✅ GPU-accelerated embeddings & entity resolution
- ✅ Deterministic quality gates & contradiction detection
- ✅ Cross-jurisdictional SOP engine
- ✅ Multilingual alert synthesis

**Judging Criteria Alignment:**
| Criteria | Weight | CrisisMesh Approach |
|----------|--------|---------------------|
| Capability | 25% | 9 specialized agents, end-to-end pipeline |
| Sponsor Tech | 25% | All 4 sponsors integrated meaningfully |
| Impact | 20% | Addresses 10 verified disaster failures |
| Agent Architecture | 15% | LangGraph with critique loops, branching |
| Demo Quality | 15% | Interactive dashboard, 10 scenarios |

## 📄 License

MIT License - Built for Open Agent Hackathon 2026

## 🙏 Acknowledgments

- **Zetaris** for Universal Semantic Layer
- **Meterless** for Agent Observability Platform
- **NVIDIA** for GPU Acceleration
- **Cursor** for AI-Native Development Environment
- **Nous Research** for Hermes Agent Framework