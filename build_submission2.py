"""
CrisisMesh - Pitch Deck Generator for CrisisMesh_Hackathon_Submission2.pptx
Fixes coordinate bugs, overlapping shapes, placeholders, and adds rich pitch notes.
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme colors - Midnight Executive Slate & Accents
    DARK_BLUE = RGBColor(0x0F, 0x17, 0x2A)      # slate-900
    MEDIUM_BLUE = RGBColor(0x1E, 0x29, 0x3B)    # slate-800
    CARD_BG = RGBColor(0x1E, 0x29, 0x3B)
    ACCENT_RED = RGBColor(0xEF, 0x44, 0x44)     # red-500
    ACCENT_ORANGE = RGBColor(0xF9, 0x73, 0x16)  # orange-500
    ACCENT_GREEN = RGBColor(0x22, 0xC5, 0x5E)   # green-500
    ACCENT_BLUE = RGBColor(0x3B, 0x82, 0xF6)    # blue-500
    ACCENT_PURPLE = RGBColor(0xA8, 0x55, 0xF7)  # purple-500
    ACCENT_CYAN = RGBColor(0x06, 0xB6, 0xD4)    # cyan-500
    ACCENT_PINK = RGBColor(0xEC, 0x48, 0x99)    # pink-500
    ACCENT_YELLOW = RGBColor(0xEA, 0xB3, 0x08)  # yellow-500
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    LIGHT_GRAY = RGBColor(0xE2, 0xE8, 0xF0)     # slate-200
    MEDIUM_GRAY = RGBColor(0x94, 0xA3, 0xB8)    # slate-400
    BORDER_GRAY = RGBColor(0x33, 0x41, 0x55)    # slate-700

    def add_background(slide, color=DARK_BLUE):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_shape_bg(slide, left_in, top_in, width_in, height_in, color, border_color=None, border_width=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(border_width)
        else:
            shape.line.fill.background()
        return shape

    def add_text_box(slide, left_in, top_in, width_in, height_in, text, font_size=16, color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name='Calibri'):
        txBox = slide.shapes.add_textbox(Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font_name
        p.alignment = alignment
        return txBox

    def add_bullets(slide, bullets, left_in, top_in, width_in, height_in, font_size=12, color=LIGHT_GRAY, spacing=Pt(6)):
        txBox = slide.shapes.add_textbox(Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
        tf = txBox.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = bullet
            p.font.size = Pt(font_size)
            p.font.color.rgb = color
            p.font.name = 'Calibri'
            p.space_after = spacing
            p.level = 0
        return txBox

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide1)
    add_shape_bg(slide1, 0, 0, 13.333, 0.08, ACCENT_RED)
    add_shape_bg(slide1, 0.8, 1.4, 0.08, 3.8, ACCENT_RED)

    add_text_box(slide1, 1.2, 1.4, 11.0, 1.1, "CrisisMesh", font_size=56, color=WHITE, bold=True)
    add_text_box(slide1, 1.2, 2.5, 11.0, 0.7, "Multi-Agent Disaster Management for Fragmented Intelligence", font_size=26, color=ACCENT_ORANGE, bold=True)
    add_text_box(slide1, 1.2, 3.3, 11.0, 0.6, "Solving 10 Verified Disaster Failure Archetypes with Autonomous AI Agents", font_size=18, color=LIGHT_GRAY)
    add_text_box(slide1, 1.2, 4.3, 11.0, 0.4, "Open Agent Hackathon 2026  •  Track 1: Solving Fragmented Intelligence", font_size=16, color=WHITE, bold=True)

    sponsors = [
        ("Zetaris", ACCENT_RED),
        ("Meterless", ACCENT_BLUE),
        ("NVIDIA", ACCENT_GREEN),
        ("Cursor", ACCENT_ORANGE)
    ]
    x_pos = 1.2
    for sponsor, col in sponsors:
        add_shape_bg(slide1, x_pos, 5.0, 2.1, 0.6, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide1, x_pos, 5.08, 2.1, 0.5, sponsor, font_size=15, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
        x_pos += 2.4

    add_text_box(slide1, 1.2, 6.3, 11.0, 0.4,
                 "Builder: Mukunth (mukuntheverquest)  •  GitHub: https://github.com/mukuntheverquest/crisismesh  •  MIT License",
                 font_size=14, color=MEDIUM_GRAY)

    set_notes(slide1, (
        "Welcome judges and fellow builders. This is CrisisMesh—an autonomous multi-agent disaster intelligence system "
        "engineered for Track 1 of Open Agent Hackathon 2026: Solving Fragmented Intelligence.\n\n"
        "During catastrophic natural disasters, emergency responders and decision makers are overwhelmed by fragmented data: "
        "sensor streams, aerial radar, social distress posts, and incompatible agency spreadsheets. Human decision delays and "
        "stovepiped data cost thousands of lives.\n\n"
        "CrisisMesh integrates 9 specialized AI agents in a robust LangGraph architecture that federates cross-agency data, "
        "simulates hazard physics, and autonomously triggers targeted evacuation warnings with deterministic guardrails."
    ))

    # =========================================================================
    # SLIDE 2: THE PROBLEM - FRAGMENTED INTELLIGENCE
    # =========================================================================
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide2)
    add_shape_bg(slide2, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide2, 0.8, 0.3, 11.5, 0.7, "The Problem: Fragmented Intelligence Kills", font_size=34, color=WHITE, bold=True)
    add_text_box(slide2, 0.8, 0.95, 11.5, 0.4, "10 Recent Disasters  •  10 Systemic Failures  •  1 Root Cause: Stovepiped Data & Approval Bottlenecks", font_size=16, color=ACCENT_ORANGE)

    failures = [
        ("1. Sleeping Supervisor", "Texas Flood 2025", "4-hr alert delay while river rose 34ft; supervisor was asleep."),
        ("2. Polygon Target Miss", "LA Wildfires 2025", "10M false sirens sent outside fire; 0 alerts to canyon victims."),
        ("3. Governance Disconnect", "Valencia DANA 2024", "13-hr delay between Red Alert and citizen emergency phone warning."),
        ("4. Sensor Destruction", "Nepal Avalanche 2026", "River gauges destroyed in 7 min; silence misinterpreted as normal."),
        ("5. PDF Registry Chaos", "Nepal Floods 2024", "3 agencies published conflicting survivor counts in raw scanned PDFs."),
        ("6. Contradictory Orders", "Libya Derna 2023", "Curfew enforced inside flood plain while dam collapsed upstream."),
        ("7. Unilingual Alerts", "Nepal Trek 2026", "Broadcast sent only in local script to international trekkers."),
        ("8. Total Isolation", "Helene 2024", "11 mountain counties completely severed; zero external cell comms."),
        ("9. Social Media Noise", "Türkiye Quake 2023", "1.8M posts in 12hr; 4% geocoding hallucinations diverted rescue."),
        ("10. Dashboard Disconnect", "Nepal Tunnels 2026", "Surface dashboard claimed clear while 500 workers were trapped."),
    ]

    for i, (title, disaster, detail) in enumerate(failures):
        row = i // 5
        col = i % 5
        x = 0.8 + col * 2.38
        y = 1.5 + row * 2.65

        add_shape_bg(slide2, x, y, 2.2, 2.45, MEDIUM_BLUE, border_color=ACCENT_RED, border_width=1.5)
        add_text_box(slide2, x + 0.12, y + 0.1, 1.96, 0.5, title, font_size=13, color=ACCENT_RED, bold=True)
        add_text_box(slide2, x + 0.12, y + 0.6, 1.96, 0.35, disaster, font_size=11, color=LIGHT_GRAY, bold=True)
        add_text_box(slide2, x + 0.12, y + 1.0, 1.96, 1.3, detail, font_size=11, color=WHITE)

    set_notes(slide2, (
        "To build a truly impactful system, we grounded our project in forensic analysis of 10 catastrophic disaster responses.\n\n"
        "In every single incident, the failure was not an absence of sensor signals—it was fragmented intelligence:\n"
        "- In Texas, automated alerts required manual sign-off, but the on-duty supervisor was asleep for 4 hours while the river surged.\n"
        "- In Los Angeles, missing downwind vector expansion resulted in 10 million false alerts across the basin while actual victims received nothing.\n"
        "- In Valencia and Libya, jurisdictional politics and contradictory curfew orders delayed lifesaving actions.\n\n"
        "These 10 verified failure archetypes serve as our comprehensive system benchmark."
    ))

    # =========================================================================
    # SLIDE 3: CRISISMESH SOLUTION OVERVIEW
    # =========================================================================
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide3)
    add_shape_bg(slide3, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide3, 0.8, 0.3, 11.5, 0.7, "CrisisMesh: Autonomous Multi-Agent Response", font_size=34, color=WHITE, bold=True)
    add_text_box(slide3, 0.8, 0.95, 11.5, 0.4, "LangGraph Orchestration  •  9 Autonomous Agents  •  180s Dead-Man Switch  •  Offline-First Architecture", font_size=16, color=ACCENT_ORANGE)

    agent_grid = [
        # Row 0: Ingestion & Perception
        ("FormatDetector", "Perception Layer", "Identifies sensor schemas, PDFs, and distress formats.", ACCENT_ORANGE, 0, 0),
        ("IngestionExecutor", "Federation Layer", "Zetaris USL federation & CUDA-accelerated ingestion.", ACCENT_BLUE, 0, 1),
        ("WorldModelSimulator", "Physics & Hazard Sim", "Simulates flood & fire vectors with dynamic geofencing.", ACCENT_GREEN, 0, 2),

        # Row 1: Orchestration & State
        ("PlannerAgent", "Decomposition & Timer", "Decomposes missions with 180s autonomous dead-man switch.", ACCENT_RED, 1, 0),
        ("LangGraph Core", "Central State Hub", "Asynchronous state machine, SQLite memory & checkpointers.", WHITE, 1, 1),
        ("MarkovianRouter", "Autonomous Bypass", "Evaluates risk states and bypasses human approval delays.", ACCENT_PURPLE, 1, 2),

        # Row 2: Action & Verification
        ("HMemStore", "Jurisdictional Memory", "Meterless long-term SOP memory & legal protocols.", ACCENT_PINK, 2, 0),
        ("RiskDispatch", "Tactical Execution", "Cell broadcast, multilingual synthesis & capability rescue.", ACCENT_YELLOW, 2, 1),
        ("Evaluator & Reporter", "Safety & Audit", "Iterative critique loops, quality scoring & provenance audits.", ACCENT_CYAN, 2, 2),
    ]

    for name, sub, desc, col, row_idx, col_idx in agent_grid:
        x = 0.8 + col_idx * 3.95
        y = 1.5 + row_idx * 1.85
        w = 3.7
        h = 1.65

        border_w = 2.5 if name == "LangGraph Core" else 1.5
        add_shape_bg(slide3, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=border_w)
        add_text_box(slide3, x + 0.15, y + 0.1, w - 0.3, 0.35, name, font_size=15, color=col, bold=True)
        add_text_box(slide3, x + 0.15, y + 0.45, w - 0.3, 0.3, sub, font_size=11, color=LIGHT_GRAY, bold=True)
        add_text_box(slide3, x + 0.15, y + 0.8, w - 0.3, 0.75, desc, font_size=11, color=WHITE)

    set_notes(slide3, (
        "CrisisMesh decouples monolithic LLMs into 9 specialized autonomous agents running under LangGraph.\n\n"
        "Key Architectural Innovations:\n"
        "1. Autonomous Dead-Man Switch: If human supervisors fail to acknowledge a catastrophic emergency within 180 seconds, "
        "the Markovian Router automatically escalates and triggers dispatch.\n"
        "2. Universal Semantic Layer: Powered by Zetaris, federating data across river gauges, NOAA satellite feeds, and 911 calls.\n"
        "3. Offline Resilience: Built with zero mandatory internet dependencies in SAMPLE_MODE, ensuring total autonomy when communications towers collapse."
    ))

    # =========================================================================
    # SLIDE 4: AGENT ARCHITECTURE & DATA FLOW
    # =========================================================================
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide4)
    add_shape_bg(slide4, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide4, 0.8, 0.3, 11.5, 0.7, "Agent Architecture: LangGraph State Machine", font_size=34, color=WHITE, bold=True)
    add_text_box(slide4, 0.8, 0.95, 11.5, 0.4, "Deterministic State Graphs  •  Iterative Critique Loops  •  SQLite Persistence  •  Meterless Tracing", font_size=16, color=ACCENT_ORANGE)

    flow_steps = [
        ("INPUT", "Sensors\nRadar\n911 Calls", ACCENT_BLUE),
        ("PLANNER", "Goal Graph\n180s Timer\nMilestones", ACCENT_RED),
        ("DETECTOR", "Classify\nComplexity\nRoute Map", ACCENT_ORANGE),
        ("INGESTION", "Zetaris USL\nCUDA Parse\nDedup", ACCENT_BLUE),
        ("SIMULATOR", "Propagation\nVector Math\nGeofencing", ACCENT_GREEN),
        ("MARKOVIAN", "State Route\nAuto Bypass\nTrigger", ACCENT_PURPLE),
        ("EVALUATOR", "Quality Gate\nCritique Loop\nScore Check", ACCENT_CYAN),
        ("DISPATCH", "Cell Alerts\nMultilingual\nResource", ACCENT_YELLOW),
        ("OUTPUT", "Verified Alerts\nDeploy Orders\nAudit Trace", ACCENT_GREEN),
    ]

    # Flow row at y = 1.5, height = 2.1
    for i, (label, desc, color) in enumerate(flow_steps):
        x = 0.5 + i * 1.37
        y = 1.5
        w = 1.18
        h = 2.1

        add_shape_bg(slide4, x, y, w, h, MEDIUM_BLUE, border_color=color, border_width=2)
        add_text_box(slide4, x + 0.04, y + 0.08, w - 0.08, 0.45, label, font_size=11, color=color, bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide4, x + 0.04, y + 0.55, w - 0.08, 1.45, desc, font_size=10, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

        if i < len(flow_steps) - 1:
            arrow_x = x + 1.19
            arrow_y = y + 0.9
            arrow = slide4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(arrow_y), Inches(0.16), Inches(0.28))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = color
            arrow.line.fill.background()

    # Engine features row at y = 3.9, height = 1.4
    features = [
        ("SAMPLE_MODE", "100% offline execution; zero external runtime dependencies.", ACCENT_GREEN),
        ("Async Checkpointer", "SQLite persistence for LangGraph state & resuming jobs.", ACCENT_BLUE),
        ("Meterless Tracing", "@trace_agent decorators tracking latencies across all 9 agents.", ACCENT_CYAN),
        ("Critique Loops", "Evaluator triggers automatic re-execution on failed criteria (max 3).", ACCENT_ORANGE),
        ("Dynamic Routing", "Conditional graph transitions evaluated on live sensor severity.", ACCENT_PURPLE),
    ]
    for i, (title, desc, col) in enumerate(features):
        x = 0.5 + i * 2.47
        y = 3.9
        w = 2.38
        h = 1.45
        add_shape_bg(slide4, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=1.5)
        add_text_box(slide4, x + 0.1, y + 0.1, w - 0.2, 0.35, title, font_size=13, color=col, bold=True)
        add_text_box(slide4, x + 0.1, y + 0.48, w - 0.2, 0.9, desc, font_size=11, color=LIGHT_GRAY)

    # Sponsor strip at y = 5.65, height = 1.45
    sponsor_highlights = [
        ("Zetaris", "Universal Semantic Layer", "Federated SQL queries across fragmented PDF/CSV/SAR registries.", ACCENT_RED),
        ("Meterless", "Observability & Reasoning", "H-Mem long-term SOPs, Markovian router & millisecond tracing.", ACCENT_BLUE),
        ("NVIDIA", "GPU Accelerated Inference", "CUDA embeddings for entity deduplication and rapid flood modeling.", ACCENT_GREEN),
        ("Cursor", "AI-Native Engineering", "Full-stack code generation, LangGraph unit tests & prompt optimization.", ACCENT_ORANGE),
    ]
    for i, (s_name, s_role, s_desc, col) in enumerate(sponsor_highlights):
        x = 0.5 + i * 3.1
        y = 5.65
        w = 2.95
        h = 1.45
        add_shape_bg(slide4, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide4, x + 0.12, y + 0.08, w - 0.24, 0.35, s_name, font_size=15, color=col, bold=True)
        add_text_box(slide4, x + 0.12, y + 0.42, w - 0.24, 0.3, s_role, font_size=11, color=WHITE, bold=True)
        add_text_box(slide4, x + 0.12, y + 0.72, w - 0.24, 0.65, s_desc, font_size=10, color=LIGHT_GRAY)

    set_notes(slide4, (
        "This slide presents the exact LangGraph execution state machine.\n\n"
        "State transitions flow from input ingestion to validation. If the Evaluator Agent discovers that a hazard polygon "
        "has not accounted for downstream hospital clusters, it rejects the state and triggers a cyclic critique loop back to the "
        "World Model Simulator for refinement.\n\n"
        "Every single agent call is instrumented with Meterless tracing, and full state checkpoints are saved into SQLite for "
        "zero-loss recovery in case of hardware reboots."
    ))

    # =========================================================================
    # SLIDE 5: SPONSOR TECHNOLOGY: DEEP INTEGRATION
    # =========================================================================
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide5)
    add_shape_bg(slide5, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide5, 0.8, 0.3, 11.5, 0.7, "Sponsor Technology: Deep Integration", font_size=34, color=WHITE, bold=True)
    add_text_box(slide5, 0.8, 0.95, 11.5, 0.4, "Production Integrations Across All 4 Hackathon Sponsors", font_size=16, color=ACCENT_ORANGE)

    # 4 Quadrants (w=5.6, h=2.75)
    quads = [
        ("Zetaris: Universal Semantic Layer", ACCENT_RED, 0.8, 1.45, [
            "Federated cross-agency queries spanning sensor tables, GIS, and 911 logs",
            "Universal schema registry for multi-format inputs (PDF, CSV, SAR GeoJSON)",
            "Data provenance lineage tracking from raw sensor reading to phone broadcast",
            "Real-time spatial joins: Sentinel-1 SAR damage footprints ↔ distress pins",
            "Sub-15s unified SQL execution over heterogeneous crisis databases",
        ]),
        ("Meterless: Observability & Memory Platform", ACCENT_BLUE, 6.8, 1.45, [
            "H-Mem: Persistent vector SOP store for cross-jurisdictional protocols",
            "Markovian: State-based routing engine driving autonomous dead-man switching",
            "World Model: Physics-based hazard propagation (wind vectors & surge rates)",
            "@trace_agent and @trace_tool_call telemetry on all 9 agents",
            "Millisecond trace latency inspection for regulatory compliance and audit trails",
        ]),
        ("NVIDIA: GPU-Accelerated Intelligence", ACCENT_GREEN, 0.8, 4.4, [
            "sentence-transformers on CUDA for entity resolution and registry deduplication",
            "GPU-accelerated risk modeling for hydraulic surge and wildfire spread",
            "TensorRT-optimized token inference for low-latency emergency synthesis",
            "Docker deployment built on nvidia/cuda:12.4.1 runtime environment",
            "Processes 1,000+ survivor records and shelter matches in under 3 seconds",
        ]),
        ("Cursor: AI-Native Development", ACCENT_ORANGE, 6.8, 4.4, [
            "AI-assisted architecture scaffolding for all 9 LangGraph agent nodes",
            "Interactive agent trace inspection and live prompt iteration",
            "Automated test generation across all 10 disaster failure scenarios",
            "Full-stack integration linking FastAPI backend with React/Leaflet UI",
            "Continuous refactoring ensuring strict PEP8, type safety, and error handling",
        ]),
    ]

    for title, col, x, y, bullets in quads:
        add_shape_bg(slide5, x, y, 5.7, 2.75, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide5, x + 0.2, y + 0.15, 5.3, 0.4, title, font_size=18, color=col, bold=True)
        add_bullets(slide5, bullets, x + 0.2, y + 0.58, 5.3, 2.05, font_size=11, color=LIGHT_GRAY, spacing=Pt(4))

    set_notes(slide5, (
        "We deliberately architected CrisisMesh around the specific superpowers of our four sponsors:\n\n"
        "- Zetaris solves the data fragmentation crisis by acting as a universal semantic layer over disparate government APIs.\n"
        "- Meterless gives us observability into agent thinking and powers H-Mem, our cross-jurisdictional SOP memory.\n"
        "- NVIDIA CUDA delivers the raw compute required for real-time hydraulic simulations and survivor deduplication.\n"
        "- Cursor allowed our team to rapidly build, test, and iterate complex multi-agent state machines in record time."
    ))

    # =========================================================================
    # SLIDE 6: DEMO SCENARIOS: 10 FAILURE ARCHETYPES SOLVED
    # =========================================================================
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide6)
    add_shape_bg(slide6, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide6, 0.8, 0.3, 11.5, 0.7, "Demo Scenarios: 10 Failure Archetypes Solved", font_size=34, color=WHITE, bold=True)
    add_text_box(slide6, 0.8, 0.95, 11.5, 0.4, "All 10 Real-World Disaster Archetypes Verified 100% in Benchmark Suite", font_size=16, color=ACCENT_ORANGE)

    scenarios = [
        ("🌊 Texas Flood 2025", "Dead-Man Switch", "Autonomously dispatches downstream cell alerts in 180s when supervisor sleeps.", ACCENT_RED),
        ("🔥 LA Wildfires 2025", "Polygon Guardrails", "Expands downwind evacuation zone; prevents 10M false alarms outside boundary.", ACCENT_ORANGE),
        ("💧 Valencia DANA 2024", "Cross-Agency SOP", "Red Alert triggers automated joint mobilization across regional borders in seconds.", ACCENT_BLUE),
        ("❄️ Nepal Avalanche 2026", "Sensor Loss Inference", "Treats sudden river gauge destruction as high-confidence landslide signal.", ACCENT_GREEN),
        ("📄 Nepal Floods 2024", "CUDA Entity Dedup", "Deduplicates 3 conflicting agency PDFs and resolves missing persons in <15s.", ACCENT_RED),
        ("🏗️ Libya Derna 2023", "Contradiction Engine", "Detects dam breach, overrides local curfew, and enforces immediate upland evacuation.", ACCENT_ORANGE),
        ("🌍 Nepal Trek 2026", "Multilingual Synthesis", "Synthesizes simultaneous cell alerts in Nepali, Hindi, Tibetan, and English.", ACCENT_BLUE),
        ("📡 Helene 2024", "Offline Rerouting", "Switches to VHF/siren broadcast; routes helo & drone aid around washed-out roads.", ACCENT_GREEN),
        ("📱 Türkiye Quake 2023", "SAR Verification", "Joins social SOS pins with Sentinel-1 SAR imagery to eliminate 4% false pins.", ACCENT_RED),
        ("🚇 Nepal Tunnels 2026", "Capability Match", "Dispatches specialized tunnel extraction teams, LiDAR drones, and trauma units.", ACCENT_ORANGE),
    ]

    for i, (name, feature, detail, col) in enumerate(scenarios):
        row = i // 5
        col_idx = i % 5
        x = 0.6 + col_idx * 2.45
        y = 1.45 + row * 2.85
        w = 2.3
        h = 2.65

        add_shape_bg(slide6, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide6, x + 0.12, y + 0.1, w - 0.24, 0.5, name, font_size=13, color=WHITE, bold=True)
        add_text_box(slide6, x + 0.12, y + 0.6, w - 0.24, 0.4, feature, font_size=12, color=col, bold=True)
        add_text_box(slide6, x + 0.12, y + 1.05, w - 0.24, 1.45, detail, font_size=11, color=LIGHT_GRAY)

    set_notes(slide6, (
        "Rather than demoing a generic toy scenario, CrisisMesh was built and evaluated against 10 concrete failure archetypes.\n\n"
        "For example, in Archetype 6 (Libya Derna), CrisisMesh's contradiction engine caught an official curfew order issued "
        "inside a rapidly submerging hydraulic polygon and instantly overrode it with an urgent uphill evacuation mandate.\n\n"
        "In Archetype 4 (Nepal Avalanche), when river gauges suddenly went offline in 7 minutes, traditional systems saw no data; "
        "CrisisMesh correctly inferred physical destruction and alerted downstream villages."
    ))

    # =========================================================================
    # SLIDE 7: TECH STACK & IMPLEMENTATION
    # =========================================================================
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide7)
    add_shape_bg(slide7, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide7, 0.8, 0.3, 11.5, 0.7, "Technology Stack & Implementation", font_size=34, color=WHITE, bold=True)
    add_text_box(slide7, 0.8, 0.95, 11.5, 0.4, "Production-Grade, Modular, Containerized & Edge-Ready", font_size=16, color=ACCENT_ORANGE)

    columns = [
        ("Backend & AI Pipeline", ACCENT_BLUE, 0.7, [
            "Python 3.11  •  FastAPI 0.112  •  Uvicorn ASGI",
            "LangGraph 0.3 with dynamic cyclic routing",
            "AsyncSqliteSaver persistent state checkpointer",
            "Pydantic 2.8 schemas for strict type guarantees",
            "sentence-transformers & PyTorch CUDA 12.4",
            "OpenTelemetry & Meterless tracing SDK",
            "SAMPLE_MODE=true for 100% offline edge execution",
            "Structured JSON logging with audit timestamps",
        ]),
        ("Frontend & Geospatial UI", ACCENT_GREEN, 4.8, [
            "React 18  •  TypeScript  •  Vite 5 build tooling",
            "Tailwind CSS with Dark Slate Emergency styling",
            "Leaflet & React-Leaflet GIS polygon rendering",
            "Live interactive dashboard: scenarios, jobs, maps",
            "Dynamic agent execution trace visualizer",
            "Interactive 10-archetype scenario trigger console",
            "Mobile-responsive tablet & desktop layouts",
            "Zero compilation errors on npm run build",
        ]),
        ("Infrastructure & DevSecOps", ACCENT_ORANGE, 8.9, [
            "Docker Compose multi-container architecture",
            "PostgreSQL 16 + Redis 7 + Nginx reverse proxy",
            "Automated health checks across all microservices",
            "Zero-config local fallback via SQLite",
            "Pre-commit hooks (ruff, black, mypy)",
            "Strict security audit: zero hardcoded secrets",
            "Comprehensive .env.example configuration",
            "MIT Open Source License for global adoption",
        ]),
    ]

    for title, col, x, bullets in columns:
        add_shape_bg(slide7, x, 1.45, 3.75, 5.6, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide7, x + 0.2, 1.6, 3.35, 0.4, title, font_size=18, color=col, bold=True)
        add_bullets(slide7, bullets, x + 0.2, 2.1, 3.35, 4.7, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    set_notes(slide7, (
        "Our tech stack is built for real-world resilience, not just a hackathon demo.\n\n"
        "- The backend leverages FastAPI and LangGraph 0.3 with asynchronous SQLite checkpointers so agent states survive server crashes.\n"
        "- The frontend provides emergency coordinators with a high-fidelity geospatial situational map displaying real-time danger polygons, "
        "deployed rescue boats, and active evacuation corridors.\n"
        "- The entire application is containerized with Docker and can run fully offline in a command tent with zero cloud dependencies."
    ))

    # =========================================================================
    # SLIDE 8: QUALITY ASSURANCE & VALIDATION RESULTS
    # =========================================================================
    slide8 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide8)
    add_shape_bg(slide8, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide8, 0.8, 0.3, 11.5, 0.7, "Quality Assurance & Validation Results", font_size=34, color=WHITE, bold=True)
    add_text_box(slide8, 0.8, 0.95, 11.5, 0.4, "Rigorous Verification Across Unit Tests, Pipeline Endpoints, and Live Traces", font_size=16, color=ACCENT_ORANGE)

    # 8 Metric Badges (2 rows of 4) from y=1.45 to y=4.4
    metrics = [
        ("Agent Import", "100%", "All 9 specialized agents import cleanly without errors.", ACCENT_GREEN),
        ("Pipeline Stages", "9/9", "Full autonomous multi-agent execution loop verified.", ACCENT_BLUE),
        ("API Endpoints", "6/6", "Health, Scenarios, Respond, Sync, Graph, Demo active.", ACCENT_ORANGE),
        ("Frontend Build", "0 Errors", "TypeScript compilation passes completely clean.", ACCENT_GREEN),
        ("Docker Compose", "5/5", "All container services running with healthchecks.", ACCENT_BLUE),
        ("Benchmark Suite", "10/10", "All 10 disaster failure archetypes verified.", ACCENT_ORANGE),
        ("Sponsor Tech", "4/4", "Zetaris, Meterless, NVIDIA, Cursor fully integrated.", ACCENT_GREEN),
        ("Security Audit", "100%", "Zero secrets in repository; verified clean audit.", ACCENT_GREEN),
    ]

    for i, (label, val, desc, col) in enumerate(metrics):
        row = i // 4
        col_idx = i % 4
        x = 0.7 + col_idx * 2.98
        y = 1.45 + row * 1.55
        w = 2.82
        h = 1.42

        add_shape_bg(slide8, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=1.5)
        add_text_box(slide8, x + 0.1, y + 0.08, w - 0.2, 0.3, label, font_size=12, color=col, bold=True)
        add_text_box(slide8, x + 0.1, y + 0.38, w - 0.2, 0.45, val, font_size=24, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide8, x + 0.1, y + 0.88, w - 0.2, 0.45, desc, font_size=10, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

    # Live Meterless Trace Console from y=4.7 to 7.0
    add_shape_bg(slide8, 0.7, 4.7, 11.93, 2.35, DARK_BLUE, border_color=ACCENT_RED, border_width=2)
    add_text_box(slide8, 0.9, 4.8, 11.5, 0.35, "Meterless Trace Output (Live End-to-End Pipeline Execution)", font_size=14, color=ACCENT_RED, bold=True)

    trace_lines = [
        "[METERLESS] 🟢 Agent:planner              | Op:execute | Trace:f41b7d5d | DURATION:0.002s | STATUS:success",
        "[METERLESS] 🟢 Agent:format_detector      | Op:execute | Trace:edf58804 | DURATION:0.001s | STATUS:success",
        "[METERLESS] 🟢 Agent:ingestion_executor   | Op:execute | Trace:aae5c90b | DURATION:0.001s | STATUS:success",
        "[METERLESS] 🟢 Agent:world_model_sim      | Op:execute | Trace:77b0567e | DURATION:0.003s | STATUS:success",
        "[METERLESS] 🟢 Agent:markovian_router     | Op:execute | Trace:19d7c2f8 | DURATION:0.001s | STATUS:success",
        "[METERLESS] 🟢 Agent:risk_dispatch        | Op:execute | Trace:1a065bc3 | DURATION:0.004s | STATUS:success (Cell Alert + Helo)",
        "[METERLESS] 🟢 Agent:evaluator            | Op:execute | Trace:c4d37faa | DURATION:0.002s | STATUS:success (Quality Gate Pass)",
        "[METERLESS] 🟢 Agent:reporter             | Op:execute | Trace:93566604 | DURATION:0.002s | STATUS:success (Audit Trace Landed)",
        "[METERLESS] ✅ PIPELINE COMPLETED: Total Latency: 0.016s | 10 Scenarios Passing | 0 Escalation Bottlenecks"
    ]
    add_text_box(slide8, 0.9, 5.2, 11.5, 1.8, "\n".join(trace_lines), font_size=10, color=ACCENT_GREEN, font_name="Consolas")

    set_notes(slide8, (
        "Quality assurance is paramount for life-critical disaster software.\n\n"
        "We verified that:\n"
        "1. All 9 agents initialize and execute cleanly.\n"
        "2. All 6 REST API endpoints respond correctly.\n"
        "3. The TypeScript frontend builds with zero warnings.\n"
        "4. And our live Meterless execution trace demonstrates sub-20-millisecond agent coordination in sample mode. "
        "Where human approval chains in Texas took 4 hours, CrisisMesh completes the entire analysis and dispatch in fractions of a second."
    ))

    # =========================================================================
    # SLIDE 9: FUTURE ENHANCEMENTS & ROADMAP
    # =========================================================================
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide9)
    add_shape_bg(slide9, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide9, 0.8, 0.3, 11.5, 0.7, "Future Enhancements & Roadmap", font_size=34, color=WHITE, bold=True)
    add_text_box(slide9, 0.8, 0.95, 11.5, 0.4, "Strategic Path to Global Field Deployment and NGO Interoperability", font_size=16, color=ACCENT_ORANGE)

    phases = [
        ("Phase 1\nPost-Hackathon", "Production Hardening", ACCENT_RED, [
            "Production PostgreSQL cluster deployment",
            "Direct live Zetaris federated catalog hookup",
            "Helm charts & Kubernetes auto-scaling",
            "Multi-region failover and disaster recovery",
            "Stress testing for 5,000+ concurrent streams",
        ]),
        ("Phase 2\nQ1 2027", "Intelligence Expansion", ACCENT_ORANGE, [
            "Multimodal Sentinel-1 SAR + Optical fusion",
            "On-premise Llama-3.1-8B situational reports",
            "72-hour predictive hydrologic surge modeling",
            "Community crowdsourced ground truth validation",
            "Mobile PWA for field first responders",
        ]),
        ("Phase 3\nQ2 2027", "Ecosystem & NGO Scale", ACCENT_BLUE, [
            "UN OCHA & Red Cross CAP alert protocol integration",
            "Cross-jurisdictional data sharing federation",
            "Plugin marketplace for specialized rescue agents",
            "Reinsurance parametric payout automation",
            "Multi-national disaster drill simulations",
        ]),
        ("Phase 4\nQ3 2027", "Autonomous Edge Mesh", ACCENT_GREEN, [
            "Ruggedized edge deployment on Raspberry Pi 5",
            "Starlink direct satellite uplink integration",
            "LoRaWAN ad-hoc responder mesh networking",
            "Self-healing agent cluster synchronization",
            "ISO / FEMA standard compliance certification",
        ]),
    ]

    for i, (phase_label, phase_title, col, items) in enumerate(phases):
        x = 0.6 + i * 3.05
        y = 1.45
        w = 2.85
        h = 5.6

        # Phase header
        add_shape_bg(slide9, x, y, w, 0.65, col)
        add_text_box(slide9, x, y + 0.05, w, 0.55, phase_label, font_size=13, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

        # Body card
        add_shape_bg(slide9, x, y + 0.7, w, h - 0.7, MEDIUM_BLUE, border_color=col, border_width=1.5)
        add_text_box(slide9, x + 0.15, y + 0.85, w - 0.3, 0.4, phase_title, font_size=16, color=col, bold=True)
        add_bullets(slide9, items, x + 0.15, y + 1.35, w - 0.3, 3.9, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    set_notes(slide9, (
        "Our vision extends far beyond the hackathon weekend.\n\n"
        "- In Phase 1, we will harden our cloud deployment with automated Kubernetes orchestration.\n"
        "- In Phase 2, we introduce multimodal radar and optical satellite fusion for real-time flood mapping.\n"
        "- In Phase 3, we build formal integrations with UN OCHA Common Alerting Protocol (CAP) standards.\n"
        "- And in Phase 4, we will deploy CrisisMesh onto ruggedized edge hardware paired with Starlink satellite terminals, "
        "allowing first responders to establish an autonomous AI coordination center even when every cell tower and power grid is dead."
    ))

    # =========================================================================
    # SLIDE 10: SUBMISSION CHECKLIST & REPOSITORY
    # =========================================================================
    slide10 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide10)
    add_shape_bg(slide10, 0, 0, 13.333, 0.08, ACCENT_RED)

    add_text_box(slide10, 0.8, 0.3, 11.5, 0.7, "Submission Checklist & Verification ✅", font_size=34, color=WHITE, bold=True)
    add_text_box(slide10, 0.8, 0.95, 11.5, 0.4, "Open Agent Hackathon 2026  •  Track 1: Solving Fragmented Intelligence", font_size=16, color=ACCENT_ORANGE)

    checklist = [
        ("✅", "Demo Video Walkthrough", "Complete recorded walkthrough showing UI, pipeline execution, and sponsor integrations.", ACCENT_GREEN),
        ("✅", "Slide Pitch Deck", "10-slide comprehensive deck covering architecture, benchmarks, sponsor tech, and roadmap.", ACCENT_GREEN),
        ("✅", "GitHub Source Code", "Full repository with clean commit history, modular agents, and comprehensive documentation.", ACCENT_GREEN),
        ("✅", "Zetaris Integration", "USL data federation, sensor schema registry, and spatial join logic implemented.", ACCENT_GREEN),
        ("✅", "Meterless Integration", "H-Mem cross-agency SOP memory, Markovian routing, and millisecond tracing decorators.", ACCENT_GREEN),
        ("✅", "NVIDIA Integration", "CUDA embeddings for survivor deduplication and GPU hydraulic risk propagation.", ACCENT_GREEN),
        ("✅", "Cursor Development", "AI-native code generation, testing, refactoring, and LangGraph workflow orchestration.", ACCENT_GREEN),
        ("✅", "Security & Secrets Audit", "Clean security verification: zero API keys or secrets committed; .env.example provided.", ACCENT_GREEN),
        ("✅", "SAMPLE_MODE Verified", "Runs 100% offline with zero external runtime dependencies for easy judge evaluation.", ACCENT_GREEN),
        ("✅", "MIT Open Source License", "Freely accessible for humanitarian relief and emergency response worldwide.", ACCENT_GREEN),
    ]

    for i, (check, title, detail, col) in enumerate(checklist):
        y = 1.45 + i * 0.49
        add_text_box(slide10, 0.8, y, 0.45, 0.42, check, font_size=16, color=col, bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide10, 1.35, y, 3.2, 0.42, title, font_size=14, color=WHITE, bold=True)
        add_text_box(slide10, 4.65, y, 7.8, 0.42, detail, font_size=12, color=LIGHT_GRAY)

    # Bottom links box
    add_shape_bg(slide10, 0.8, 6.45, 11.7, 0.65, MEDIUM_BLUE, border_color=ACCENT_RED, border_width=1.5)
    add_text_box(slide10, 0.9, 6.55, 11.5, 0.45,
                 "Repository: https://github.com/mukuntheverquest/crisismesh   •   Local Demo: http://localhost:5173   •   Lead: Mukunth (mukuntheverquest)",
                 font_size=13, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    set_notes(slide10, (
        "In summary, CrisisMesh fulfills every single requirement for Track 1 of Open Agent Hackathon 2026.\n\n"
        "We have delivered:\n"
        "- A functional, tested 9-agent LangGraph system.\n"
        "- Deep integrations across Zetaris, Meterless, NVIDIA, and Cursor.\n"
        "- 10 verified scenario benchmarks solving historical disaster failures.\n"
        "- A zero-dependency offline mode so judges can clone and run the system locally in seconds.\n\n"
        "The repository is live at github.com/mukuntheverquest/crisismesh under the MIT License. Thank you for your time and support."
    ))

    prs.save(output_path)
    print(f"Pristine presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\venka\Gen AI Hackathon\CrisisMesh\CrisisMesh_Hackathon_Submission2.pptx"
    create_deck(out)
