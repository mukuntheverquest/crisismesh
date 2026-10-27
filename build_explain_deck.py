"""
CrisisMesh - Dedicated Pitch Deck Generator for Track 2: The Agent That Can Explain Why
Open Agent Hackathon 2026
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

    # Color Palette - Deep Navy Executive with Cyan/Emerald Explainability Accents
    DARK_BLUE = RGBColor(0x0F, 0x17, 0x2A)      # slate-900
    MEDIUM_BLUE = RGBColor(0x1E, 0x29, 0x3B)    # slate-800
    ACCENT_CYAN = RGBColor(0x06, 0xB6, 0xD4)    # cyan-500 (Explainability primary)
    ACCENT_GREEN = RGBColor(0x22, 0xC5, 0x5E)   # green-500
    ACCENT_RED = RGBColor(0xEF, 0x44, 0x44)     # red-500
    ACCENT_ORANGE = RGBColor(0xF9, 0x73, 0x16)  # orange-500
    ACCENT_BLUE = RGBColor(0x3B, 0x82, 0xF6)    # blue-500
    ACCENT_PURPLE = RGBColor(0xA8, 0x55, 0xF7)  # purple-500
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    LIGHT_GRAY = RGBColor(0xE2, 0xE8, 0xF0)     # slate-200
    MEDIUM_GRAY = RGBColor(0x94, 0xA3, 0xB8)    # slate-400

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
    # SLIDE 1: TITLE SLIDE (EXPLAINABILITY TRACK)
    # =========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide1)
    add_shape_bg(slide1, 0, 0, 13.333, 0.08, ACCENT_CYAN)
    add_shape_bg(slide1, 0.8, 1.4, 0.08, 3.8, ACCENT_CYAN)

    add_text_box(slide1, 1.2, 1.4, 11.0, 1.1, "CrisisMesh Explain", font_size=56, color=WHITE, bold=True)
    add_text_box(slide1, 1.2, 2.5, 11.0, 0.7, "The Autonomous Disaster Agent That Can Explain Why", font_size=26, color=ACCENT_CYAN, bold=True)
    add_text_box(slide1, 1.2, 3.3, 11.0, 0.6, "Auditable Causal Decision Provenance & Contradiction Resolution in Life-Critical Response", font_size=18, color=LIGHT_GRAY)
    add_text_box(slide1, 1.2, 4.3, 11.0, 0.4, "Open Agent Hackathon 2026  •  Track: The Agent That Can Explain Why", font_size=16, color=WHITE, bold=True)

    sponsors = [("Zetaris", ACCENT_RED), ("Meterless", ACCENT_BLUE), ("NVIDIA", ACCENT_GREEN), ("Cursor", ACCENT_ORANGE)]
    x_pos = 1.2
    for sponsor, col in sponsors:
        add_shape_bg(slide1, x_pos, 5.0, 2.1, 0.6, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide1, x_pos, 5.08, 2.1, 0.5, sponsor, font_size=15, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
        x_pos += 2.4

    add_text_box(slide1, 1.2, 6.3, 11.0, 0.4,
                 "Lead: Mukunth (mukuntheverquest)  •  GitHub: https://github.com/mukuntheverquest/crisismesh  •  MIT License",
                 font_size=14, color=MEDIUM_GRAY)

    set_notes(slide1, (
        "Welcome judges. This is CrisisMesh Explain, developed for the Open Agent Hackathon 2026 track: "
        "'The Agent That Can Explain Why'.\n\n"
        "In life-or-death crisis operations, black-box AI is completely unusable. Emergency directors cannot risk human lives "
        "on an opaque recommendation without knowing the exact causal chain. CrisisMesh provides full mathematical decision "
        "provenance: why an evacuation was ordered, why an unresponsive supervisor was bypassed, and why conflicting "
        "curfews were overridden."
    ))

    # =========================================================================
    # SLIDE 2: THE PROBLEM - BLACK-BOX AI KILLS
    # =========================================================================
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide2)
    add_shape_bg(slide2, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide2, 0.8, 0.3, 11.5, 0.7, "The Problem: Black-Box AI Kills in Crisis Response", font_size=34, color=WHITE, bold=True)
    add_text_box(slide2, 0.8, 0.95, 11.5, 0.4, "Emergency Commanders Reject AI Recommendations Without Traceable Causal Rationale", font_size=16, color=ACCENT_ORANGE)

    cards = [
        ("The 'Trust Deficit'", "Why Should I Order Evacuation?", "Incident commanders will not evacuate 50,000 residents based on a raw LLM output without verifying sensor evidence and hydraulic calculations.", ACCENT_RED),
        ("The Override Dilemma", "Why Disobey the Mayor's Curfew?", "When local authorities order a curfew during a dam collapse (e.g. Libya Derna), an autonomous agent must prove beyond doubt why that order is fatal.", ACCENT_ORANGE),
        ("The Resource Tradeoff", "Why Dispatch Boats Instead of Trucks?", "First responders have scarce high-water assets. The system must explain why specific terrain vehicles were selected and others rejected.", ACCENT_BLUE),
        ("The Liability Trap", "Who is Responsible When Disaster Strikes?", "Post-incident audits demand exact provenance: what sensor triggered the alert, which rule authorized dispatch, and what was the latency?", ACCENT_GREEN),
    ]

    for i, (title, subtitle, desc, col) in enumerate(cards):
        x = 0.8 + i * 2.98
        y = 1.6
        w = 2.82
        h = 5.2
        add_shape_bg(slide2, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide2, x + 0.15, y + 0.2, w - 0.3, 0.5, title, font_size=16, color=col, bold=True)
        add_text_box(slide2, x + 0.15, y + 0.75, w - 0.3, 0.6, subtitle, font_size=13, color=WHITE, bold=True)
        add_text_box(slide2, x + 0.15, y + 1.45, w - 0.3, 3.4, desc, font_size=12, color=LIGHT_GRAY)

    set_notes(slide2, (
        "Why do emergency responders hesitate to adopt AI? Because in high-stakes disasters, an unexplainable recommendation "
        "creates a fatal trust deficit. If an AI suggests evacuating a valley or overriding an official order, commanders need to see "
        "the exact causal tree. CrisisMesh solves this fundamental barrier by embedding explainability at every layer of the agent state machine."
    ))

    # =========================================================================
    # SLIDE 3: THE SOLUTION - VERIFIABLE CAUSAL DECISION PROVENANCE
    # =========================================================================
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide3)
    add_shape_bg(slide3, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide3, 0.8, 0.3, 11.5, 0.7, "The Solution: Verifiable Causal Decision Provenance", font_size=34, color=WHITE, bold=True)
    add_text_box(slide3, 0.8, 0.95, 11.5, 0.4, "Connecting Raw Sensor Signals to Physics Simulations, Legal SOPs, and Action Justifications", font_size=16, color=ACCENT_CYAN)

    steps = [
        ("1. SENSOR EVIDENCE", "River Gauge: 34.2 ft\nRadar: Sentinel-1 SAR\nRate: +12 ft/hour surge", ACCENT_BLUE),
        ("2. PHYSICS MODEL", "Hydraulic propagation:\nCrest hits town in 14 min\nDepth: 4.2ft in Sector B", ACCENT_GREEN),
        ("3. LEGAL / SOP BASIS", "H-Mem SOP TX-EM-7:\nMandates evacuation when\npopulation > 500 & crest > 30ft", ACCENT_PURPLE),
        ("4. CRITIQUE GATE", "Evaluator Agent:\nScores 10 safety criteria;\nverifies no false polygon blast", ACCENT_ORANGE),
        ("5. EXPLAINABLE ACTION", "Action: Cell Broadcast\nExplains: 'Why overridden'\nAudit: Saved in SQLite", ACCENT_CYAN),
    ]

    for i, (title, desc, col) in enumerate(steps):
        x = 0.6 + i * 2.47
        y = 1.6
        w = 2.38
        h = 2.4
        add_shape_bg(slide3, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=2)
        add_text_box(slide3, x + 0.1, y + 0.15, w - 0.2, 0.4, title, font_size=13, color=col, bold=True)
        add_text_box(slide3, x + 0.1, y + 0.65, w - 0.2, 1.65, desc, font_size=11, color=WHITE)

        if i < len(steps) - 1:
            arrow_x = x + 2.39
            arrow_y = y + 1.05
            arrow = slide3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(arrow_x), Inches(arrow_y), Inches(0.16), Inches(0.28))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = col
            arrow.line.fill.background()

    # Core Explainability Principles Box
    add_shape_bg(slide3, 0.6, 4.3, 12.13, 2.7, MEDIUM_BLUE, border_color=ACCENT_CYAN, border_width=2)
    add_text_box(slide3, 0.8, 4.45, 11.7, 0.4, "Four Pillars of the CrisisMesh 'Explain Why' Engine", font_size=18, color=ACCENT_CYAN, bold=True)

    pillars = [
        "1. Causal Traceability: Every alert links back to the specific sensor reading, timestamp, and hydraulic surge rate.",
        "2. Counterfactual Reasoning: Explains why alternative actions (e.g. shelter-in-place, dispatching trucks) were rejected.",
        "3. Contradiction Resolution: Pinpoints the exact conflict between conflicting agency directives and provides forensic justification.",
        "4. Legal & SOP Attribution: Directly quotes the jurisdictional Standard Operating Procedure giving legal authority to act.",
    ]
    add_bullets(slide3, pillars, 0.8, 4.95, 11.7, 1.8, font_size=13, color=LIGHT_GRAY, spacing=Pt(8))

    set_notes(slide3, (
        "This slide illustrates the core causal decision pipeline of CrisisMesh Explain. We don't just prompt an LLM to take action. "
        "Instead, every candidate dispatch travels through five verifiable stages: from raw physical telemetry, to hydraulic simulation, "
        "to statutory SOP compliance, through a 10-point critique gate, producing an action accompanied by its complete explanation tree."
    ))

    # =========================================================================
    # SLIDE 4: THE ARCHITECTURE OF EXPLAINABILITY (EVALUATOR & REPORTER)
    # =========================================================================
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide4)
    add_shape_bg(slide4, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide4, 0.8, 0.3, 11.5, 0.7, "The Architecture of Explainability: Dual-Engine", font_size=34, color=WHITE, bold=True)
    add_text_box(slide4, 0.8, 0.95, 11.5, 0.4, "The Evaluator Agent (Pre-Action Critique) + The Reporter Agent (Post-Action Provenance)", font_size=16, color=ACCENT_ORANGE)

    # Column 1: Evaluator Agent
    add_shape_bg(slide4, 0.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_ORANGE, border_width=2)
    add_text_box(slide4, 1.0, 1.7, 5.3, 0.4, "1. Evaluator Agent (The Pre-Action Critique)", font_size=18, color=ACCENT_ORANGE, bold=True)
    evaluator_items = [
        "Acts as an adversarial safety gate before any order is published",
        "Scores the candidate plan against 10 weighted criteria (thresholds 0.7 - 0.95)",
        "Explains WHY a plan failed: e.g. 'Evacuation polygon leaves out nursing home'",
        "Triggers cyclical revision loops back to the Planner (up to 3 iterations)",
        "Prevents over-alerting by rejecting cell broadcasts exceeding 5x hazard area",
        "Enforces mathematical consistency across hydraulic and demographic data",
    ]
    add_bullets(slide4, evaluator_items, 1.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    # Column 2: Reporter Agent
    add_shape_bg(slide4, 6.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_CYAN, border_width=2)
    add_text_box(slide4, 7.0, 1.7, 5.3, 0.4, "2. Reporter Agent (The Post-Action Provenance)", font_size=18, color=ACCENT_CYAN, bold=True)
    reporter_items = [
        "Constructs comprehensive legal and operational audit reports",
        "Generates the Causal Explanation Graph stored in SQLite state",
        "Documents exact execution latencies via Meterless distributed tracing",
        "Summarizes cross-jurisdictional coordination decisions from H-Mem",
        "Produces executive-ready post-incident reviews for FEMA / state audits",
        "Extracts lessons learned for continuous agent improvement",
    ]
    add_bullets(slide4, reporter_items, 7.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    set_notes(slide4, (
        "Explainability in CrisisMesh is powered by a dual-engine architecture. "
        "The Evaluator Agent operates BEFORE action execution, critiquing plans and articulating explicit reasons for revision. "
        "The Reporter Agent operates AFTER execution, synthesizing full provenance trails, latency benchmarks, and lessons learned. "
        "Together, they ensure complete transparency before, during, and after a crisis."
    ))

    # =========================================================================
    # SLIDE 5: CASE 1 - EXPLAINING THE DEAD-MAN OVERRIDE
    # =========================================================================
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide5)
    add_shape_bg(slide5, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide5, 0.8, 0.3, 11.5, 0.7, "Case 1: Explaining the Dead-Man Override (Texas Flood)", font_size=34, color=WHITE, bold=True)
    add_text_box(slide5, 0.8, 0.95, 11.5, 0.4, "How CrisisMesh Explains Bypassing an Unresponsive Human Supervisor in 180s", font_size=16, color=ACCENT_RED)

    # Left: What Happened in 2025
    add_shape_bg(slide5, 0.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_RED, border_width=2)
    add_text_box(slide5, 1.0, 1.7, 5.3, 0.4, "The Historical Failure (Texas 2025)", font_size=18, color=ACCENT_RED, bold=True)
    hist_items = [
        "Guadalupe River surged 34 feet in under 3 hours at 01:00 AM",
        "Automated river gauge triggered critical flood alarm at state ops center",
        "System required manual human confirmation before broadcasting",
        "The on-duty emergency supervisor fell asleep; alert sat idle for 4 hours",
        "Result: Zero evacuation warnings reached downstream RV parks and campers",
    ]
    add_bullets(slide5, hist_items, 1.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    # Right: How CrisisMesh Explains the Override
    add_shape_bg(slide5, 6.8, 1.5, 5.7, 5.5, DARK_BLUE, border_color=ACCENT_GREEN, border_width=2)
    add_text_box(slide5, 7.0, 1.7, 5.3, 0.4, "CrisisMesh Autonomous Explanation Output", font_size=18, color=ACCENT_GREEN, bold=True)

    json_trace = (
        "{\n"
        '  "action": "AUTONOMOUS_ALERT_DISPATCH",\n'
        '  "override_reason": "Supervisor unacknowledged > 180s",\n'
        '  "evidence": {\n'
        '    "gauge_id": "GUADALUPE_01",\n'
        '    "crest_observed": "34.2 ft (Critical: >28 ft)",\n'
        '    "surge_velocity": "+12.4 ft/hr",\n'
        '    "time_to_impact": "14 minutes to RV Park"\n'
        "  },\n"
        '  "legal_authorization": {\n'
        '    "sop_id": "TX-SOP-FLASHFLOOD-7",\n'
        '    "rule": "Autonomous failover triggered when\\n'
        '             downstream lives > 500 & delay > 3 min"\n'
        "  },\n"
        '  "audit_status": "VERIFIED_AND_LOGGED"\n'
        "}"
    )
    add_text_box(slide5, 7.0, 2.3, 5.3, 4.3, json_trace, font_size=11, color=ACCENT_GREEN, font_name="Consolas")

    set_notes(slide5, (
        "Here is a concrete demonstration of explainability in action: the Texas flash flood scenario. "
        "In 2025, a sleeping supervisor delayed alerts by 4 hours. CrisisMesh's Markovian Router incorporates a 180-second dead-man switch. "
        "Crucially, when the agent bypasses the human, it doesn't do so silently. It produces an explicit justification showing the exact "
        "gauge reading, arrival time to impact, and the statutory legal SOP authorizing the autonomous action."
    ))

    # =========================================================================
    # SLIDE 6: CASE 2 - FORENSIC CONTRADICTION RESOLUTION
    # =========================================================================
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide6)
    add_shape_bg(slide6, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide6, 0.8, 0.3, 11.5, 0.7, "Case 2: Forensic Contradiction Resolution (Libya Derna)", font_size=34, color=WHITE, bold=True)
    add_text_box(slide6, 0.8, 0.95, 11.5, 0.4, "Explaining Why the Agent Overrode an Official Curfew Order During Dam Failure", font_size=16, color=ACCENT_ORANGE)

    # Left: Official Contradictory Messaging
    add_shape_bg(slide6, 0.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_RED, border_width=2)
    add_text_box(slide6, 1.0, 1.7, 5.3, 0.4, "The Official Contradiction (Libya 2023)", font_size=18, color=ACCENT_RED, bold=True)
    derna_items = [
        "18:00 - Officials order city-wide curfew: citizens instructed to stay in homes",
        "01:00 - Upper Derna dam collapses; 30 million cubic meters release into gorge",
        "01:19 - Evacuation sirens sound 19 minutes AFTER the flood wave hits town",
        "Curfew trapped thousands inside ground-floor homes along the riverbed",
        "Root cause: Bureaucracy refused to contradict initial curfew guidance",
    ]
    add_bullets(slide6, derna_items, 1.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    # Right: CrisisMesh Explanation Tree
    add_shape_bg(slide6, 6.8, 1.5, 5.7, 5.5, DARK_BLUE, border_color=ACCENT_CYAN, border_width=2)
    add_text_box(slide6, 7.0, 1.7, 5.3, 0.4, "CrisisMesh Contradiction Explanation", font_size=18, color=ACCENT_CYAN, bold=True)

    derna_json = (
        "{\n"
        '  "action": "OVERRIDE_AND_EVACUATE",\n'
        '  "conflict_detected": {\n'
        '    "directive_1": "Official Curfew (Stay Indoors)",\n'
        '    "physical_state": "Dam Breach Confirmed (SAR Radar)"\n'
        "  },\n"
        '  "why_overridden": [\n'
        '    "Inundation polygon predicts 4.2m flood depth",\n'
        '    "Single-story structures in Sector 1 will submerge",\n'
        '    "Shelter-in-place carries 100% mortality probability"\n'
        "  ],\n"
        '  "corrective_action": {\n'
        '    "command": "MANDATORY_UPHILL_EVACUATION",\n'
        '    "evacuation_corridor": "Highland Ridge Route 4",\n'
        '    "languages": ["Arabic", "English", "French"]\n'
        "  }\n"
        "}"
    )
    add_text_box(slide6, 7.0, 2.3, 5.3, 4.3, derna_json, font_size=11, color=ACCENT_CYAN, font_name="Consolas")

    set_notes(slide6, (
        "In Archetype 6, the Derna dam collapse, human bureaucracy was paralyzed by cognitive dissonance: officials had issued a curfew "
        "and failed to rescind it even as the dam gave way. CrisisMesh's contradiction engine cross-references official orders with "
        "Sentinel-1 SAR radar. When the contradiction score hits 0.95, it overrides the curfew and articulates exactly why shelter-in-place "
        "would be fatal."
    ))

    # =========================================================================
    # SLIDE 7: CASE 3 - CAPABILITY & SPATIAL EXPLANATIONS
    # =========================================================================
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide7)
    add_shape_bg(slide7, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide7, 0.8, 0.3, 11.5, 0.7, "Case 3: Capability & Spatial Explanations", font_size=34, color=WHITE, bold=True)
    add_text_box(slide7, 0.8, 0.95, 11.5, 0.4, "Explaining Why Assets Were Chosen and Why Geofence Polygons Were Bounded", font_size=16, color=ACCENT_ORANGE)

    # Left: Spatial Bounding
    add_shape_bg(slide7, 0.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_GREEN, border_width=2)
    add_text_box(slide7, 1.0, 1.7, 5.3, 0.4, "Spatial Precision: LA Wildfires 2025", font_size=18, color=ACCENT_GREEN, bold=True)
    la_items = [
        "Problem: Cell broadcast warned 10M people across LA County, but missed canyon victims.",
        "Why CrisisMesh Bounded the Geofence:",
        "• Calculated Santa Ana wind vector: 48 knots @ 240°",
        "• Formed downwind elliptical polygon (Area: 14.2 sq km)",
        "• Evaluator Gate rejected county-wide blast (>5x buffer)",
        "• Result: Sirens targeted only those in the smoke & fire path",
    ]
    add_bullets(slide7, la_items, 1.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    # Right: Capability Matching
    add_shape_bg(slide7, 6.8, 1.5, 5.7, 5.5, MEDIUM_BLUE, border_color=ACCENT_BLUE, border_width=2)
    add_text_box(slide7, 7.0, 1.7, 5.3, 0.4, "Capability Matching: Nepal Tunnels 2026", font_size=18, color=ACCENT_BLUE, bold=True)
    tunnel_items = [
        "Problem: 500 workers trapped in flooded tunnel; surface dispatched standard fire engines.",
        "Why CrisisMesh Selected Specialized Assets:",
        "• Rejected Standard Fire Truck: Exceeds 2.8m portal width",
        "• Rejected High-Clearance 4x4: Water depth (1.8m) exceeds engine intake",
        "• Dispatched Confined-Space DMAT: SCBA gear for CO2 > 800ppm",
        "• Dispatched Tethered LiDAR Drones: Zero GPS underground",
    ]
    add_bullets(slide7, tunnel_items, 7.0, 2.2, 5.3, 4.5, font_size=12, color=LIGHT_GRAY, spacing=Pt(8))

    set_notes(slide7, (
        "Explainability also applies to spatial geofencing and resource allocation. "
        "In the LA Wildfires, CrisisMesh explains why it restricted the broadcast to a downwind ellipse rather than alarming the whole city. "
        "In the Nepal Tunnel collapse, CrisisMesh explains not only why specialized DMAT teams and tethered LiDAR drones were dispatched, "
        "but explicitly why standard fire engines were rejected due to tunnel portal constraints."
    ))

    # =========================================================================
    # SLIDE 8: THE 10-POINT SAFETY CRITIQUE GATE
    # =========================================================================
    slide8 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide8)
    add_shape_bg(slide8, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide8, 0.8, 0.3, 11.5, 0.7, "The 10-Point Safety Critique Gate (Evaluator)", font_size=34, color=WHITE, bold=True)
    add_text_box(slide8, 0.8, 0.95, 11.5, 0.4, "Mathematical Quality Criteria With Explicit Rejection Explanations", font_size=16, color=ACCENT_CYAN)

    criteria = [
        ("polygon_accuracy", "20%", "0.80", "Alert polygon accurately bounds hazard without over/under coverage", ACCENT_GREEN),
        ("alert_timeliness", "20%", "0.80", "Alerts dispatched within 180s Dead-Man Switch SLA", ACCENT_BLUE),
        ("contradiction_caught", "20%", "0.95", "Contradictory orders (curfew in flood zone) blocked & explained", ACCENT_RED),
        ("polygon_precision", "15%", "0.80", "Blocks county-wide blasts >5x actual hazard footprint", ACCENT_ORANGE),
        ("vulnerable_coverage", "15%", "0.90", "Prioritizes elderly, schools, hospitals, underground parking", ACCENT_PURPLE),
        ("dispatch_appropriateness", "15%", "0.80", "Dispatches capability-matched assets to verified terrain", ACCENT_CYAN),
        ("route_viability", "10%", "0.70", "Validates that designated evacuation routes are not submerged", ACCENT_GREEN),
        ("multilingual_coverage", "10%", "0.80", "Alerts translated into demographic languages (Ne/Es/Vi/En)", ACCENT_BLUE),
        ("asset_match_quality", "10%", "0.75", "Equipment specs match physical disaster mechanics", ACCENT_ORANGE),
        ("sop_compliance", "10%", "0.85", "Adheres to inter-jurisdictional legal mandates in H-Mem", ACCENT_PURPLE),
    ]

    for i, (name, weight, thresh, desc, col) in enumerate(criteria):
        row = i // 2
        col_idx = i % 2
        x = 0.8 + col_idx * 5.95
        y = 1.45 + row * 1.08
        w = 5.75
        h = 0.98

        add_shape_bg(slide8, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=1.5)
        add_text_box(slide8, x + 0.15, y + 0.08, 3.2, 0.3, name, font_size=13, color=col, bold=True)
        add_text_box(slide8, x + 3.4, y + 0.08, 2.2, 0.3, f"Weight: {weight}  |  Min: {thresh}", font_size=11, color=WHITE, bold=True, alignment=PP_ALIGN.RIGHT)
        add_text_box(slide8, x + 0.15, y + 0.42, w - 0.3, 0.5, desc, font_size=11, color=LIGHT_GRAY)

    set_notes(slide8, (
        "Every single candidate action produced by CrisisMesh must pass through this 10-point mathematical critique gate. "
        "Notice the high weights assigned to contradiction detection (0.95 threshold) and alert timeliness (180s SLA). "
        "If a plan fails even one threshold, the Evaluator Agent outputs a structured critique explaining why and provides "
        "concrete suggestions for revision."
    ))

    # =========================================================================
    # SLIDE 9: TECHNOLOGY STACK & AUDITABLE TELEMETRY
    # =========================================================================
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide9)
    add_shape_bg(slide9, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide9, 0.8, 0.3, 11.5, 0.7, "Technology Stack & Auditable Telemetry", font_size=34, color=WHITE, bold=True)
    add_text_box(slide9, 0.8, 0.95, 11.5, 0.4, "Meterless Distributed Tracing  •  LangGraph Checkpointers  •  FastAPI  •  React GIS", font_size=16, color=ACCENT_ORANGE)

    # Trace telemetry console
    add_shape_bg(slide9, 0.8, 1.45, 11.7, 3.2, DARK_BLUE, border_color=ACCENT_CYAN, border_width=2)
    add_text_box(slide9, 1.0, 1.6, 11.3, 0.35, "Meterless Distributed Trace Telemetry (Zero Black-Box Execution)", font_size=14, color=ACCENT_CYAN, bold=True)

    trace_log = (
        "[METERLESS] 🟢 Agent:planner            | Op:execute | Trace:f41b7d5d | EXPLAIN: Armed 180s deadman switch for Sector B\n"
        "[METERLESS] 🟢 Agent:format_detector    | Op:execute | Trace:edf58804 | EXPLAIN: Classified river gauge CSV + Sentinel-1 SAR\n"
        "[METERLESS] 🟢 Agent:ingestion_executor | Op:execute | Trace:aae5c90b | EXPLAIN: Normalized coordinates via Zetaris Semantic Layer\n"
        "[METERLESS] 🟢 Agent:world_model_sim    | Op:execute | Trace:77b0567e | EXPLAIN: Simulated Guadalupe River surge vector (+12ft/hr)\n"
        "[METERLESS] 🟢 Agent:markovian_router   | Op:execute | Trace:19d7c2f8 | EXPLAIN: Supervisor timeout reached; autonomous bypass executed\n"
        "[METERLESS] 🟢 Agent:risk_dispatch      | Op:execute | Trace:1a065bc3 | EXPLAIN: Generated 3 cell alerts (En/Es/Vi); matched 4 shallow boats\n"
        "[METERLESS] 🟢 Agent:evaluator          | Op:execute | Trace:c4d37faa | EXPLAIN: Validated against 10 safety criteria; Score: 0.92 (PASS)\n"
        "[METERLESS] 🟢 Agent:reporter           | Op:execute | Trace:93566604 | EXPLAIN: Produced Causal Provenance Audit Report\n"
        "[METERLESS] ✅ PIPELINE COMPLETED: Total Latency: 0.016s | 10 Scenarios Passing | Zero Black-Box Decisions"
    )
    add_text_box(slide9, 1.0, 2.05, 11.3, 2.5, trace_log, font_size=10, color=ACCENT_GREEN, font_name="Consolas")

    # Stack highlights below
    tech_cards = [
        ("Meterless Tracing", "@trace_agent decorators on all 9 agents provide millisecond audit trails.", ACCENT_BLUE),
        ("SQLite State Memory", "AsyncSqliteSaver ensures full state checkpoints can be audited post-crisis.", ACCENT_GREEN),
        ("Zetaris Federation", "Maintains end-to-end data lineage from raw sensor schema to phone alert.", ACCENT_RED),
        ("NVIDIA Acceleration", "CUDA embeddings enable sub-15s survivor deduplication across registries.", ACCENT_ORANGE),
    ]
    for i, (name, desc, col) in enumerate(tech_cards):
        x = 0.8 + i * 2.98
        y = 4.85
        w = 2.82
        h = 2.1
        add_shape_bg(slide9, x, y, w, h, MEDIUM_BLUE, border_color=col, border_width=1.5)
        add_text_box(slide9, x + 0.12, y + 0.15, w - 0.24, 0.4, name, font_size=14, color=col, bold=True)
        add_text_box(slide9, x + 0.12, y + 0.65, w - 0.24, 1.3, desc, font_size=11, color=LIGHT_GRAY)

    set_notes(slide9, (
        "Under the hood, CrisisMesh is fully instrumented with Meterless distributed tracing. "
        "Every single agent execution logs its inputs, outputs, duration, and explainability payload. "
        "Combined with SQLite async state checkpoints and Zetaris data lineage, an emergency commission can inspect the exact "
        "decision process at any millisecond in time."
    ))

    # =========================================================================
    # SLIDE 10: SUBMISSION CHECKLIST & REPOSITORY
    # =========================================================================
    slide10 = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide10)
    add_shape_bg(slide10, 0, 0, 13.333, 0.08, ACCENT_CYAN)

    add_text_box(slide10, 0.8, 0.3, 11.5, 0.7, "Submission Checklist & Verification ✅", font_size=34, color=WHITE, bold=True)
    add_text_box(slide10, 0.8, 0.95, 11.5, 0.4, "Open Agent Hackathon 2026  •  Track: The Agent That Can Explain Why", font_size=16, color=ACCENT_ORANGE)

    checklist = [
        ("✅", "Explainability Documentation", "Full EXPLAINABILITY.md published detailing the causal decision engine.", ACCENT_GREEN),
        ("✅", "Demo Video Walkthrough", "Complete recorded walkthrough demonstrating live scenario execution.", ACCENT_GREEN),
        ("✅", "Dedicated Pitch Deck", "10-slide presentation analyzing the 4 explainability pillars & architecture.", ACCENT_GREEN),
        ("✅", "10 Failure Archetype Solved", "10/10 disaster benchmark scenarios passing with auditable outputs.", ACCENT_GREEN),
        ("✅", "Contradiction Resolution Engine", "Mathematically catches & explains official message conflicts.", ACCENT_GREEN),
        ("✅", "180s Dead-Man Switch", "Autonomously bypasses delays with full statutory SOP attribution.", ACCENT_GREEN),
        ("✅", "Meterless Trace Telemetry", "Millisecond distributed tracing across all 9 agent state transitions.", ACCENT_GREEN),
        ("✅", "100% Offline Resilience", "SAMPLE_MODE=true runs offline with zero external runtime dependencies.", ACCENT_GREEN),
        ("✅", "Security & Secrets Clean", "Zero hardcoded keys; complete .env.example configuration.", ACCENT_GREEN),
        ("✅", "MIT Open Source License", "Publicly accessible on GitHub at github.com/mukuntheverquest/crisismesh.", ACCENT_GREEN),
    ]

    for i, (check, title, detail, col) in enumerate(checklist):
        y = 1.45 + i * 0.49
        add_text_box(slide10, 0.8, y, 0.45, 0.42, check, font_size=16, color=col, bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide10, 1.35, y, 3.2, 0.42, title, font_size=14, color=WHITE, bold=True)
        add_text_box(slide10, 4.65, y, 7.8, 0.42, detail, font_size=12, color=LIGHT_GRAY)

    add_shape_bg(slide10, 0.8, 6.45, 11.7, 0.65, MEDIUM_BLUE, border_color=ACCENT_CYAN, border_width=1.5)
    add_text_box(slide10, 0.9, 6.55, 11.5, 0.45,
                 "Repository: https://github.com/mukuntheverquest/crisismesh   •   Local Demo: http://localhost:5173   •   Lead: Mukunth (mukuntheverquest)",
                 font_size=13, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    set_notes(slide10, (
        "In conclusion, CrisisMesh Explain demonstrates that AI in life-critical operations does not have to be a black box. "
        "By grounding every decision in physical telemetry, dynamic world models, statutory SOPs, and transparent critique gates, "
        "we provide the first autonomous emergency agent that emergency commanders can truly trust. Thank you."
    ))

    prs.save(output_path)
    print(f"Pristine Explainability presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\venka\Gen AI Hackathon\CrisisMesh\CrisisMesh_Explain_Why_PitchDeck.pptx"
    create_deck(out)
