import streamlit as st
import pandas as pd
import sys
import os

# Fix import paths: add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.database.factory import get_db
from src.integrations.email_service import EmailService
from src.engine.scoring import ScoringEngine
import plotly.express as px
import plotly.graph_objects as go
import threading
from src.engine.processor import ProcessOrchestrator

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Holocene | Startup Sourcing Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main { background-color: #0a0e1a; }

/* Header */
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #a371f7, #f778ba);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8b949e;
    margin-top: 0;
    margin-bottom: 2rem;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #58a6ff;
}
.metric-label {
    font-size: 0.85rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Startup cards */
.startup-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}
.startup-card:hover {
    border-color: #58a6ff;
    box-shadow: 0 4px 20px rgba(88, 166, 255, 0.1);
}
.startup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.startup-name {
    font-size: 1.3rem;
    font-weight: 600;
    color: #e6edf3;
    margin: 0;
}
.startup-meta {
    color: #8b949e;
    font-size: 0.85rem;
    margin-bottom: 8px;
}
.startup-desc {
    color: #c9d1d9;
    line-height: 1.6;
    margin-bottom: 12px;
}
.startup-rationale {
    color: #a371f7;
    font-style: italic;
    font-size: 0.9rem;
    border-left: 3px solid #a371f7;
    padding-left: 12px;
    margin: 12px 0;
}

/* Score badges */
.score-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 24px;
    font-weight: 700;
    font-size: 1rem;
    color: white;
}
.score-high { background: linear-gradient(135deg, #238636, #2ea043); }
.score-mid  { background: linear-gradient(135deg, #9e6a03, #d29922); }
.score-low  { background: linear-gradient(135deg, #da3633, #f85149); }

/* Score bars */
.score-bar-container {
    display: flex;
    align-items: center;
    margin: 4px 0;
}
.score-bar-label {
    width: 90px;
    color: #8b949e;
    font-size: 0.75rem;
    text-transform: uppercase;
}
.score-bar-track {
    flex: 1;
    height: 8px;
    background: #21262d;
    border-radius: 4px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}
.score-bar-value {
    width: 35px;
    text-align: right;
    color: #e6edf3;
    font-size: 0.8rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ── Data Layer ───────────────────────────────────────────────
@st.cache_resource
def get_database():
    return get_db()

db = get_database()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    score_filter = st.slider("Minimum Confidence Score", 0, 100, 40)
    
    all_sources = ["TechCrunch", "EU-Startups", "Sifted", "YCombinator-Blog",
                   "Show-HN-RSS", "HackerNews", "Reddit"]
    
    source_filter = st.multiselect(
        "Data Sources",
        all_sources,
        default=all_sources
    )
    
    status_filter = st.selectbox("Status", ["All", "Pending", "Save", "Ignore", "Progress"], index=0)
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", key="btn_refresh"):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.info("The agent scans and evaluates startups in a separate background process.")

# ── Header ───────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">Holocene Startup Sourcing Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Discover early-stage startups before they become widely known · AI-Powered Deal Flow</p>', unsafe_allow_html=True)


# ── Load & Filter Data ──────────────────────────────────────
startups = db.get_all_startups()

filtered = startups
if score_filter > 0:
    filtered = [s for s in filtered if s.get("confidence_score", 0) >= score_filter]
if source_filter:
    filtered = [s for s in filtered if s.get("source") in source_filter]
if status_filter != "All":
    filtered = [s for s in filtered if s.get("status", "Pending") == status_filter]


# ── Metrics Row ──────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total = len(startups)
avg_score = sum(s.get("confidence_score", 0) for s in startups) / total if total else 0
high_quality = len([s for s in startups if s.get("confidence_score", 0) >= 70])
pending = len([s for s in startups if s.get("status", "Pending") == "Pending"])

with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Discovered</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score:.0f}%</div><div class="metric-label">Avg Score</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{high_quality}</div><div class="metric-label">High Quality (70+)</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{pending}</div><div class="metric-label">Pending Review</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Main Layout ──────────────────────────────────────────────
col_main, col_side = st.columns([2.5, 1])

with col_main:
    st.markdown("### 🎯 Startup Pipeline")

    if not filtered:
        st.info("No startups match your filters. Try lowering the confidence score or running the agent (`python main.py`).")
    else:
        for startup in filtered:
            sid = startup.get("_id", startup.get("link", "unknown"))
            score = startup.get("confidence_score", 0)
            badge_class = "score-high" if score >= 70 else "score-mid" if score >= 50 else "score-low"
            name = startup.get("company_name", startup.get("title", "Unknown"))
            desc = startup.get("description", startup.get("summary", ""))[:300]
            industry = startup.get("industry", "N/A")
            stage = startup.get("stage", "N/A")
            source = startup.get("source", "N/A")
            rationale = startup.get("rationale", "No rationale provided.")

            # Score breakdown bars
            breakdown = startup.get("score_breakdown", {})
            if isinstance(breakdown, str):
                try:
                    import json
                    breakdown = json.loads(breakdown)
                except:
                    breakdown = {}

            bars_html = ""
            colors = {"sector": "#58a6ff", "geography": "#3fb950", "funding": "#d29922", "sdg": "#f778ba", "innovation": "#a371f7"}
            for key in ["sector", "geography", "funding", "sdg", "innovation"]:
                val = int(breakdown.get(key, 0))
                pct = (val / 20) * 100
                color = colors.get(key, "#58a6ff")
                bars_html += f'''
                <div class="score-bar-container">
                    <div class="score-bar-label">{key}</div>
                    <div class="score-bar-track">
                        <div class="score-bar-fill" style="width: {pct}%; background: {color};"></div>
                    </div>
                    <div class="score-bar-value">{val}/20</div>
                </div>'''

            # Join the HTML without indentation to prevent Streamlit from showing it as a code block
            card_html = (
                f'<div class="startup-card">'
                f'  <div class="startup-header">'
                f'    <h3 class="startup-name">{name}</h3>'
                f'    <span class="score-badge {badge_class}">{score}%</span>'
                f'  </div>'
                f'  <div class="startup-meta">{industry} · {stage} · via {source}</div>'
                f'  <div class="startup-desc">{desc}</div>'
                f'  <div class="startup-rationale"><strong>Rationale:</strong> {rationale}</div>'
                f'  <div style="margin-top: 15px;">{bars_html}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            # Action buttons
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🚀 Progress", key=f"prog_{sid}"):
                    db.update_startup_status(startup.get("link"), "Progress")
                    db.add_feedback(startup.get("link"), "Progress")
                    st.success(f"Progressed: {name}")
                    st.rerun()
            with c2:
                if st.button("💾 Save", key=f"save_{sid}"):
                    db.update_startup_status(startup.get("link"), "Save")
                    db.add_feedback(startup.get("link"), "Save")
                    st.success(f"Saved: {name}")
                    st.rerun()
            with c3:
                if st.button("❌ Ignore", key=f"ign_{sid}"):
                    db.update_startup_status(startup.get("link"), "Ignore")
                    db.add_feedback(startup.get("link"), "Ignore")
                    st.toast(f"Ignored: {name}")
                    st.rerun()
            with c4:
                if st.button("⛔ N/A", key=f"na_{sid}"):
                    db.update_startup_status(startup.get("link"), "Not Applicable")
                    db.add_feedback(startup.get("link"), "Not Applicable")
                    st.toast(f"Marked N/A: {name}")
                    st.rerun()

            st.markdown("---")

with col_side:
    st.markdown("### 📊 Analytics")

    if startups:
        # Score distribution
        scores = [s.get("confidence_score", 0) for s in startups]
        fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=10,
                                            marker_color='#58a6ff',
                                            marker_line_color='#1f6feb',
                                            marker_line_width=1)])
        fig.update_layout(
            title="Score Distribution",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Source breakdown
        sources = {}
        for s in startups:
            src = s.get("source", "Unknown")
            sources[src] = sources.get(src, 0) + 1
        fig2 = go.Figure(data=[go.Pie(
            labels=list(sources.keys()),
            values=list(sources.values()),
            hole=0.5,
            marker_colors=['#58a6ff', '#3fb950', '#d29922', '#f778ba', '#a371f7', '#f0883e', '#8b949e']
        )])
        fig2.update_layout(
            title="By Source",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Status breakdown
        statuses = {}
        for s in startups:
            status = s.get("status", "Pending")
            statuses[status] = statuses.get(status, 0) + 1
        st.markdown("#### Status Overview")
        for status, count in statuses.items():
            emoji = {"Pending": "⏳", "Save": "💾", "Progress": "🚀", "Ignore": "❌"}.get(status, "📌")
            st.markdown(f"{emoji} **{status}**: {count}")
    else:
        st.info("No data yet. Run `python main.py` to start collecting.")
