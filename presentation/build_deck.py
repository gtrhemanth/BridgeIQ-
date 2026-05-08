"""
Generates the BridgeIQ Executive Presentation as a .pptx file
Run: python build_deck.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os

OUT = os.path.join(os.path.dirname(__file__), "BridgeIQ_Executive_Presentation.pptx")

NAVY  = RGBColor(0x1A, 0x3A, 0x5C)
BLUE  = RGBColor(0x4F, 0x8E, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY  = RGBColor(0x5D, 0x6D, 0x7E)
BLACK = RGBColor(0x0D, 0x1B, 0x2A)
RED   = RGBColor(0xE5, 0x3E, 0x3E)
GREEN = RGBColor(0x38, 0xA1, 0x69)
AMBER = RGBColor(0xD6, 0x93, 0x00)
LIGHT = RGBColor(0xF0, 0xF4, 0xFF)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]  # blank

# ── Helpers ───────────────────────────────────────────────────────────────────
def add_slide():
    return prs.slides.add_slide(blank_layout)

def rect(slide, left, top, width, height, fill_color=None, line_color=None):
    shape = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Inches(height))
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def text_box(slide, text, left, top, width, height,
             font_size=18, bold=False, color=None, align=PP_ALIGN.LEFT,
             wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return txBox

def nav_bar(slide, current=1, total=10):
    rect(slide, 0, 7.1, 13.33, 0.4, fill_color=NAVY)
    text_box(slide, f"BridgeIQ — AI-Powered Business Intelligence & Process Transformation",
             0.2, 7.12, 10, 0.35, font_size=9, color=WHITE)
    text_box(slide, f"Slide {current} / {total}  |  Apex Solutions  |  Confidential",
             10, 7.12, 3.1, 0.35, font_size=9, color=RGBColor(0xAA, 0xBB, 0xCC),
             align=PP_ALIGN.RIGHT)

def slide_header(slide, title, subtitle=None):
    rect(slide, 0, 0, 13.33, 1.1, fill_color=NAVY)
    text_box(slide, title, 0.4, 0.12, 12, 0.55, font_size=28, bold=True, color=WHITE)
    if subtitle:
        text_box(slide, subtitle, 0.4, 0.7, 12, 0.38, font_size=13, color=BLUE)

def kpi_card(slide, left, top, label, value, delta=None, delta_good=True):
    rect(slide, left, top, 2.8, 1.4, fill_color=LIGHT, line_color=BLUE)
    text_box(slide, label, left+0.12, top+0.08, 2.56, 0.35, font_size=10, color=GRAY)
    text_box(slide, value, left+0.12, top+0.38, 2.56, 0.6, font_size=22, bold=True, color=NAVY)
    if delta:
        color = GREEN if delta_good else RED
        text_box(slide, delta, left+0.12, top+1.0, 2.56, 0.32, font_size=10, color=color, bold=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s1 = add_slide()
rect(s1, 0, 0, 13.33, 7.5, fill_color=NAVY)
rect(s1, 0, 2.8, 13.33, 0.06, fill_color=BLUE)

text_box(s1, "BRIDGEIQ", 1.5, 1.0, 10.33, 1.5,
         font_size=60, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text_box(s1, "AI-Powered Business Intelligence & Process Transformation",
         1.5, 2.5, 10.33, 0.8,
         font_size=20, color=BLUE, align=PP_ALIGN.CENTER)
text_box(s1, "Apex Solutions · Technical BA Portfolio Project · Sai Hemanth",
         1.5, 3.2, 10.33, 0.6,
         font_size=14, color=WHITE, italic=True, align=PP_ALIGN.CENTER)
text_box(s1, "May 2026", 1.5, 6.6, 10.33, 0.5,
         font_size=12, color=GRAY, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — THE PROBLEM
# ══════════════════════════════════════════════════════════════════════════════
s2 = add_slide()
slide_header(s2, "The Problem", "Apex Solutions is losing customers faster than it's acquiring them")
nav_bar(s2, 2, 10)

problems = [
    ("22%", "Annual Churn Rate", "Industry benchmark: 5-7%. Each 1% = ~$150K ARR lost.", RED),
    ("18%", "Onboarding Failure", "Incomplete onboarding customers churn at 2.4x the rate of completed ones.", AMBER),
    ("28 hrs", "Avg Ticket Resolution", "Critical SLA breach rate exceeds 35%. Support volume growing 18% YoY.", AMBER),
    ("0", "Predictive Signals", "No automated system to identify at-risk customers before they cancel.", RED),
]

for i, (stat, title, desc, color) in enumerate(problems):
    col = i % 2
    row = i // 2
    lft = 0.4 + col * 6.5
    tp  = 1.4 + row * 2.6
    rect(s2, lft, tp, 6.0, 2.2, line_color=color)
    rect(s2, lft, tp, 1.4, 2.2, fill_color=color)
    text_box(s2, stat, lft+0.08, tp+0.5, 1.24, 1.0, font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text_box(s2, title, lft+1.55, tp+0.12, 4.3, 0.45, font_size=14, bold=True, color=NAVY)
    text_box(s2, desc, lft+1.55, tp+0.58, 4.3, 1.4, font_size=11, color=GRAY, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — THE SOLUTION
# ══════════════════════════════════════════════════════════════════════════════
s3 = add_slide()
slide_header(s3, "The Solution", "BridgeIQ — Three integrated capabilities that work together")
nav_bar(s3, 3, 10)

pillars = [
    ("01", "Customer Intelligence Engine", "Composite health scoring from 6 signals. Daily automated computation. At-risk flag with Slack/email alert before customer churns.", NAVY),
    ("02", "Onboarding Transformation", "5-stage structured workflow with SLA tracking, blocker logging, and automated escalation when customers go silent.", BLUE),
    ("03", "AI Feedback & Requirements", "Unstructured feedback analyzed at scale. Pain points ranked by business impact. User stories auto-generated in Agile format.", RGBColor(0x2E, 0x86, 0x5F)),
]

for i, (num, title, desc, color) in enumerate(pillars):
    lft = 0.4 + i * 4.3
    rect(s3, lft, 1.35, 3.9, 3.5, line_color=color)
    rect(s3, lft, 1.35, 3.9, 0.6, fill_color=color)
    text_box(s3, f"{num}  {title}", lft+0.15, 1.38, 3.6, 0.55, font_size=13, bold=True, color=WHITE)
    text_box(s3, desc, lft+0.15, 2.05, 3.6, 2.6, font_size=11, color=GRAY, wrap=True)

text_box(s3, "Underpinned by: 6 data tables | 10+ SQL queries | Live Plotly dashboard | Claude AI API | Python + Streamlit",
         0.4, 5.1, 12.5, 0.5, font_size=11, color=GRAY, italic=True, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — KEY METRICS (CURRENT STATE)
# ══════════════════════════════════════════════════════════════════════════════
s4 = add_slide()
slide_header(s4, "Business Baseline — Current State Analysis", "Data-driven diagnosis from 500 customers, 4K tickets, 8K usage events")
nav_bar(s4, 4, 10)

kpis = [
    ("Active Customers", "390", "of 500 total"),
    ("Total MRR", "$1.24M", "across 3 plan tiers"),
    ("Churn Rate", "22%", "110 customers lost"),
    ("Avg Health Score", "76.2 / 100", "active customers"),
    ("Open Tickets", "1,000+", "unresolved backlog"),
    ("Onboarding Done", "82%", "90 stuck mid-process"),
    ("Avg Resolution", "28 hrs", "Critical SLA: 35% breach"),
    ("At-Risk Customers", "47", "score >= 50, still active"),
]

for i, (label, value, sub) in enumerate(kpis):
    col = i % 4
    row = i // 4
    lft = 0.3 + col * 3.2
    tp  = 1.3 + row * 2.0
    rect(s4, lft, tp, 2.95, 1.7, fill_color=LIGHT, line_color=BLUE)
    text_box(s4, label, lft+0.12, tp+0.1, 2.7, 0.38, font_size=10, color=GRAY)
    text_box(s4, value, lft+0.12, tp+0.45, 2.7, 0.65, font_size=18, bold=True, color=NAVY)
    text_box(s4, sub, lft+0.12, tp+1.15, 2.7, 0.45, font_size=9, color=GRAY, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — PROCESS: AS-IS vs TO-BE
# ══════════════════════════════════════════════════════════════════════════════
s5 = add_slide()
slide_header(s5, "Process Redesign — AS-IS vs TO-BE", "Churn detection & customer health monitoring workflow")
nav_bar(s5, 5, 10)

rect(s5, 0.3, 1.25, 5.9, 5.5, fill_color=RGBColor(0xFF, 0xF0, 0xF0), line_color=RED)
text_box(s5, "AS-IS (Current State)", 0.4, 1.3, 5.7, 0.5, font_size=14, bold=True, color=RED)

as_is_steps = [
    "CSM manually reviews accounts (Mon morning, 4hrs)",
    "Pulls data from 3 separate spreadsheets",
    "No standardized risk criteria — gut feel",
    "Churn risk only noticed after cancel intent",
    "Informal escalation via email chain (no SLA)",
    "No audit trail, no visibility for CS Director",
]
for j, step in enumerate(as_is_steps):
    text_box(s5, f"• {step}", 0.5, 1.9+j*0.65, 5.6, 0.6, font_size=10.5, color=BLACK, wrap=True)

rect(s5, 6.8, 1.25, 6.2, 5.5, fill_color=RGBColor(0xF0, 0xFF, 0xF4), line_color=GREEN)
text_box(s5, "TO-BE (BridgeIQ)", 6.9, 1.3, 6.0, 0.5, font_size=14, bold=True, color=GREEN)

to_be_steps = [
    "Daily automated health score (6 signals, no manual effort)",
    "Single unified dashboard — one source of truth",
    "Rule-based composite risk scoring with thresholds",
    "Proactive Slack alert sent BEFORE customer churns",
    "Structured escalation with SLA timer & audit log",
    "Weekly AI-generated insight report from ticket data",
]
for j, step in enumerate(to_be_steps):
    text_box(s5, f"• {step}", 6.9, 1.9+j*0.65, 6.0, 0.6, font_size=10.5, color=BLACK, wrap=True)

text_box(s5, "→", 6.3, 3.6, 0.6, 0.6, font_size=28, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — USER STORIES SNAPSHOT
# ══════════════════════════════════════════════════════════════════════════════
s6 = add_slide()
slide_header(s6, "Requirements — User Stories Snapshot", "15 sprint-ready stories across 5 epics | Jira-importable")
nav_bar(s6, 6, 10)

epics = [
    ("Customer Health", "US-01 to US-02", "Risk score dashboard, automated Slack alerts", "5 pts", NAVY),
    ("Onboarding", "US-03 to US-04", "Stage tracker, self-service checklist", "13 pts", BLUE),
    ("Support", "US-05 to US-06", "Support dashboard, automated status updates", "11 pts", RGBColor(0x2E, 0x86, 0x5F)),
    ("Analytics", "US-07 to US-10", "Executive report, filter panel, MRR-at-risk", "16 pts", AMBER),
    ("AI Features", "US-08 to US-09", "Feedback analyzer, requirements generator", "16 pts", RGBColor(0x7B, 0x2D, 0x8B)),
]

for i, (epic, ids, desc, pts, color) in enumerate(epics):
    lft = 0.4 + i * 2.56
    rect(s6, lft, 1.4, 2.35, 4.8, line_color=color)
    rect(s6, lft, 1.4, 2.35, 0.5, fill_color=color)
    text_box(s6, epic, lft+0.1, 1.42, 2.15, 0.45, font_size=11, bold=True, color=WHITE)
    text_box(s6, ids, lft+0.1, 2.0, 2.15, 0.4, font_size=10, bold=True, color=color)
    text_box(s6, desc, lft+0.1, 2.45, 2.15, 2.4, font_size=9.5, color=GRAY, wrap=True)
    rect(s6, lft+0.1, 5.55, 2.15, 0.45, fill_color=LIGHT, line_color=color)
    text_box(s6, f"{pts} story pts", lft+0.1, 5.6, 2.15, 0.35, font_size=10, bold=True, color=color, align=PP_ALIGN.CENTER)

text_box(s6, "All user stories include: Acceptance Criteria (Given/When/Then) | MoSCoW Priority | Story Point Estimate | UAT Test Cases",
         0.4, 6.55, 12.5, 0.45, font_size=10, color=GRAY, italic=True, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — TECHNICAL ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
s7 = add_slide()
slide_header(s7, "Technical Architecture", "CS background advantage — bridging data, AI, and business")
nav_bar(s7, 7, 10)

layers = [
    ("Data Layer", "SQLite / PostgreSQL\n6 tables | 15K+ rows\nFaker-generated synthetic data\nERD documented", NAVY),
    ("Analytics Layer", "10 SQL queries\nKPI Overview | Churn Analysis\nRevenue Trends | At-Risk Scoring\nCohort Retention | Usage Analysis", BLUE),
    ("AI Layer", "Claude Haiku API\nFeedback analysis\nRequirements generation\nUser story drafting", RGBColor(0x2E, 0x86, 0x5F)),
    ("Presentation Layer", "Streamlit + Plotly\nExecutive Dashboard\n3-page live app\nDeployed on Streamlit Cloud", AMBER),
]

for i, (title, desc, color) in enumerate(layers):
    lft = 0.4 + i * 3.25
    rect(s7, lft, 1.4, 3.0, 4.0, fill_color=LIGHT, line_color=color)
    rect(s7, lft, 1.4, 3.0, 0.55, fill_color=color)
    text_box(s7, title, lft+0.12, 1.43, 2.76, 0.5, font_size=13, bold=True, color=WHITE)
    text_box(s7, desc, lft+0.12, 2.08, 2.76, 3.2, font_size=10.5, color=GRAY, wrap=True)

text_box(s7, "Tools: Python 3.11 | SQLite | Anthropic SDK | Streamlit | Plotly | python-docx | python-pptx | Faker | Pandas",
         0.4, 5.7, 12.5, 0.55, font_size=10, color=GRAY, italic=True, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — SUCCESS METRICS & ROI
# ══════════════════════════════════════════════════════════════════════════════
s8 = add_slide()
slide_header(s8, "Success Metrics & ROI", "Measurable targets with defined baselines")
nav_bar(s8, 8, 10)

metrics = [
    ("Churn Rate", "22%", "≤ 14%", "-8pts", True),
    ("Onboarding Done", "82%", "≥ 95%", "+13pts", True),
    ("Ticket Resolution", "28 hrs", "≤ 17 hrs", "-39%", True),
    ("SLA Breach (Critical)", "35%", "≤ 10%", "-25pts", True),
    ("At-Risk ID Time", "7-14 days", "< 24 hrs", "Automated", True),
    ("CSM Manual Work", "4 hrs/wk", "< 30 min/wk", "-88%", True),
    ("MRR Protected", "$0 tracked", "+$180K ARR", "New", True),
    ("NPS Score", "6.8", "≥ 8.0", "+1.2", True),
]

for i, (metric, baseline, target, delta, good) in enumerate(metrics):
    col = i % 4
    row = i // 4
    lft = 0.3 + col * 3.25
    tp  = 1.35 + row * 2.5
    rect(s8, lft, tp, 3.0, 2.15, fill_color=LIGHT, line_color=BLUE)
    text_box(s8, metric, lft+0.12, tp+0.1, 2.76, 0.38, font_size=10, color=GRAY, bold=True)
    text_box(s8, baseline, lft+0.12, tp+0.48, 1.3, 0.45, font_size=12, color=RED)
    text_box(s8, "→", lft+1.35, tp+0.5, 0.4, 0.4, font_size=14, bold=True, color=GRAY, align=PP_ALIGN.CENTER)
    text_box(s8, target, lft+1.65, tp+0.48, 1.2, 0.45, font_size=12, bold=True, color=GREEN)
    text_box(s8, delta, lft+0.12, tp+1.6, 2.76, 0.4, font_size=10, color=GREEN, bold=True, italic=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — WHAT THIS DEMONSTRATES (BA SKILLS)
# ══════════════════════════════════════════════════════════════════════════════
s9 = add_slide()
slide_header(s9, "What This Demonstrates", "A Technical BA who bridges both worlds — business and technology")
nav_bar(s9, 9, 10)

skills = [
    ("Business Skills", [
        "Business Requirements Document (BRD) — 11 sections",
        "Stakeholder Analysis & RACI Matrix",
        "Process Mapping — AS-IS / TO-BE",
        "15 Agile User Stories with Acceptance Criteria",
        "Risk Register with mitigation strategies",
        "UAT Test Cases and sign-off framework",
        "Executive-level KPI reporting",
    ], NAVY),
    ("Technical Skills", [
        "Data modeling — 6-table SQLite schema + ERD",
        "10+ SQL queries (window functions, CTEs, cohort analysis)",
        "Python — data generation, doc building, API integration",
        "Claude AI API — NLP, requirements generation",
        "Streamlit — multi-page web application",
        "Plotly — interactive dashboards",
        "Git & GitHub — version-controlled project repo",
    ], BLUE),
    ("AI Literacy", [
        "Prompt engineering — structured AI output formats",
        "AI tool in the workflow — draft → review → refine",
        "AI-generated requirements with human validation",
        "Understanding AI limitations (hallucination, bias)",
        "AI as business process component — not just a tool",
        "Responsible AI output labeling in deliverables",
    ], RGBColor(0x2E, 0x86, 0x5F)),
]

for i, (title, items, color) in enumerate(skills):
    lft = 0.3 + i * 4.35
    rect(s9, lft, 1.35, 4.1, 5.4, line_color=color)
    rect(s9, lft, 1.35, 4.1, 0.5, fill_color=color)
    text_box(s9, title, lft+0.12, 1.38, 3.86, 0.45, font_size=13, bold=True, color=WHITE)
    for j, item in enumerate(items):
        text_box(s9, f"• {item}", lft+0.15, 1.98+j*0.65, 3.8, 0.6, font_size=10, color=GRAY, wrap=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — CALL TO ACTION
# ══════════════════════════════════════════════════════════════════════════════
s10 = add_slide()
rect(s10, 0, 0, 13.33, 7.5, fill_color=NAVY)
rect(s10, 0, 3.0, 13.33, 0.06, fill_color=BLUE)

text_box(s10, "Explore BridgeIQ", 1.5, 0.8, 10.33, 1.2,
         font_size=42, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text_box(s10, "Live app · Full source code · All documentation",
         1.5, 1.9, 10.33, 0.7, font_size=18, color=BLUE, align=PP_ALIGN.CENTER)

links = [
    ("Live Demo", "Streamlit App", "share.streamlit.io/gtrhemanth/bridgeiq"),
    ("Source Code", "GitHub Repo", "github.com/gtrhemanth/BridgeIQ"),
    ("Documentation", "Full BRD + Docs", "github.com/gtrhemanth/BridgeIQ/docs"),
]

for i, (title, sub, url) in enumerate(links):
    lft = 1.5 + i * 3.6
    rect(s10, lft, 3.3, 3.2, 1.8, fill_color=RGBColor(0x2A, 0x4A, 0x7C), line_color=BLUE)
    text_box(s10, title, lft+0.15, 3.4, 2.9, 0.5, font_size=14, bold=True, color=WHITE)
    text_box(s10, sub, lft+0.15, 3.88, 2.9, 0.38, font_size=11, color=BLUE)
    text_box(s10, url, lft+0.15, 4.3, 2.9, 0.6, font_size=9.5, color=GRAY, italic=True)

text_box(s10, "Sai Hemanth  |  gtrhemanth14@gmail.com  |  github.com/gtrhemanth",
         1.5, 5.5, 10.33, 0.6, font_size=13, color=WHITE, align=PP_ALIGN.CENTER)
text_box(s10, "Technical Business Analyst | AI/ML & Data Science | IEEE-Published Researcher",
         1.5, 6.1, 10.33, 0.55, font_size=12, color=BLUE, italic=True, align=PP_ALIGN.CENTER)

nav_bar(s10, 10, 10)

prs.save(OUT)
print(f"Presentation saved: {OUT}")
