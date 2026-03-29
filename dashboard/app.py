import streamlit as st
import pandas as pd
import sys
import os
import random
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Fix import paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.database.factory import get_db

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Early-Stage Investment Agent",
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
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #58a6ff, #a371f7, #f778ba);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8b949e;
    margin-top: 5px;
    margin-bottom: 2rem;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #58a6ff;
}
.metric-label {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* Startup cards */
.startup-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.startup-card:hover {
    border-color: #58a6ff;
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(88, 166, 255, 0.15);
}
.startup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
.startup-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e6edf3;
    margin: 0;
}
.startup-meta {
    color: #8b949e;
    font-size: 0.9rem;
    margin-bottom: 12px;
}
.startup-desc {
    color: #c9d1d9;
    line-height: 1.6;
    margin-bottom: 15px;
}
.startup-rationale {
    color: #a371f7;
    font-style: italic;
    font-size: 0.95rem;
    border-left: 3px solid #a371f7;
    padding-left: 15px;
    margin: 15px 0;
}

/* Score badges */
.score-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 30px;
    font-weight: 800;
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
    margin: 6px 0;
}
.score-bar-label {
    width: 100px;
    color: #8b949e;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
}
.score-bar-track {
    flex: 1;
    height: 6px;
    background: #21262d;
    border-radius: 3px;
    overflow: hidden;
    margin: 0 10px;
}
.score-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.8s ease-in-out;
}
.score-bar-value {
    width: 40px;
    text-align: right;
    color: #e6edf3;
    font-size: 0.85rem;
    font-weight: 700;
}

/* Pinned badge */
.pinned-badge {
    background: #f778ba;
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 800;
    vertical-align: middle;
    margin-left: 12px;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# ── Data Layer ───────────────────────────────────────────────
@st.cache_resource
def get_database():
    return get_db()

db = get_database()

# ── Session State Logic ──────────────────────────────────────
if "discovery_ids" not in st.session_state:
    st.session_state.discovery_ids = []
if "saved_ids" not in st.session_state:
    st.session_state.saved_ids = set()

def refresh_discovery_batch(force=False):
    """Picks random startups for the discovery batch."""
    if not st.session_state.discovery_ids or force:
        all_startups = db.get_all_startups()
        # Filter: Must not be already Pinned/Saved or Ignored
        available = [s.get("link") for s in all_startups 
                    if s.get("status", "Pending") == "Pending" 
                    and s.get("link") not in st.session_state.saved_ids]
        
        if not available:
            # Fallback: If no Pending left, show all non-Saved/N/A just to keep it running
            available = [s.get("link") for s in all_startups if s.get("link") not in st.session_state.saved_ids]

        if available:
            # Sampling logic for consistent batch experience
            num_to_pick = min(6, len(available))
            st.session_state.discovery_ids = random.sample(available, num_to_pick)
        else:
            st.session_state.discovery_ids = []

# Initial discovery load
refresh_discovery_batch()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 DISCOVERY")
    if st.button("✨ FIND NEW STARTUPS", key="btn_discovery", use_container_width=True, type="primary"):
        refresh_discovery_batch(force=True)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 FILTERS")
    score_filter = st.slider("Min Quality Score", 0, 100, 40)
    
    all_sources = ["TechCrunch", "EU-Startups", "Sifted", "YCombinator-Blog",
                   "Show-HN-RSS", "HackerNews", "Reddit"]
    
    source_filter = st.multiselect(
        "Sources",
        all_sources,
        default=all_sources
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ SYSTEM")
    if st.button("🔄 Reload Database", key="btn_refresh", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.info("Discovery Mode: Focusing on 6 high-potential startups per session.")

# ── Main Header ──────────────────────────────────────────────
st.markdown('<h1 class="hero-title">Early-Stage Investment Agent</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="hero-subtitle">Currently exploring {len(st.session_state.discovery_ids)} high-potential AI ventures</p>', unsafe_allow_html=True)

# ── Load & Filter Display Data ───────────────────────────────
# Visible = Discovery batch + Pinned (Saved) items
visible_ids = set(st.session_state.discovery_ids) | st.session_state.saved_ids
all_startups = db.get_all_startups()

# Filter for visible IDs and then apply UI sliders
filtered = [s for s in all_startups if s.get("link") in visible_ids]

if score_filter > 0:
    filtered = [s for s in filtered if s.get("confidence_score", 0) >= score_filter]
if source_filter:
    filtered = [s for s in filtered if s.get("source") in source_filter]

# ── Metrics Row ──────────────────────────────────────────────
m1, padding, m2 = st.columns([1, 0.5, 1])
total_db = len(all_startups)
avg_score = sum(s.get("confidence_score", 0) for s in all_startups) / total_db if total_db else 0
in_view = len(filtered)

with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score:.0f}%</div><div class="metric-label">Avg Quality</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{in_view}</div><div class="metric-label">Active Batch</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── UI Layout ───────────────────────────────────────────────
col_main, col_side = st.columns([2.5, 1])

with col_main:
    st.markdown("### 🎯 VENTURE BATCH")
    
    if not filtered:
        st.info("Your discovery queue is empty. Click 'FIND NEW STARTUPS' to load the next batch.")
    else:
        for startup in filtered:
            link = startup.get("link")
            sid = startup.get("_id", link)
            is_pinned = link in st.session_state.saved_ids
            score = int(startup.get("confidence_score", 0))
            badge_class = "score-high" if score >= 70 else "score-mid" if score >= 40 else "score-low"
            
            # Extract data
            name = startup.get("company_name", startup.get("title", "Unknown"))
            industry = startup.get("industry", "N/A")
            stage = startup.get("stage", "N/A")
            source = startup.get("source", "N/A")
            desc = startup.get("description", startup.get("summary", ""))[:300]
            rationale = startup.get("rationale", "No analysis provided.")
            
            # Breakdown
            breakdown = startup.get("score_breakdown", {})
            if isinstance(breakdown, str):
                try: import json; breakdown = json.loads(breakdown)
                except: breakdown = {}

            bars_html = ""
            colors = {"sector": "#58a6ff", "geography": "#3fb950", "funding": "#d29922", "sdg": "#f778ba", "innovation": "#a371f7"}
            for key in ["sector", "geography", "funding", "sdg", "innovation"]:
                val = int(breakdown.get(key, 0))
                pct = (val / 20) * 100
                bars_html += f'''
                <div class="score-bar-container">
                    <div class="score-bar-label">{key}</div>
                    <div class="score-bar-track">
                        <div class="score-bar-fill" style="width: {pct}%; background: {colors.get(key, '#58a6ff')};"></div>
                    </div>
                    <div class="score-bar-value">{val}/20</div>
                </div>'''

            # Styling for pinned card
            border_css = "border-color: #f778ba; box-shadow: 0 0 15px rgba(247, 120, 186, 0.2);" if is_pinned else ""
            pinned_tag = '<span class="pinned-badge">PINNED</span>' if is_pinned else ""

            st.markdown(f'''
            <div class="startup-card" style="{border_css}">
                <div class="startup-header">
                    <h3 class="startup-name">{name}{pinned_tag}</h3>
                    <span class="score-badge {badge_class}">{score}%</span>
                </div>
                <div class="startup-meta">{industry} · {stage} · via {source}</div>
                <div class="startup-desc">{desc}</div>
                <div class="startup-rationale"><strong>The Thesis:</strong> {rationale}</div>
                <div style="margin-top: 20px;">{bars_html}</div>
            </div>
            ''', unsafe_allow_html=True)

            # Interactive Controls
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("🚀 PROGRESS", key=f"p_{sid}", use_container_width=True):
                    db.update_startup_status(link, "Progress")
                    st.session_state.saved_ids.add(link)
                    if link in st.session_state.discovery_ids: st.session_state.discovery_ids.remove(link)
                    st.rerun()
            with c2:
                if not is_pinned:
                    if st.button("💾 SAVE", key=f"s_{sid}", use_container_width=True):
                        db.update_startup_status(link, "Save")
                        st.session_state.saved_ids.add(link)
                        st.rerun()
                else:
                    if st.button("🔓 UNPIN", key=f"u_{sid}", use_container_width=True):
                        st.session_state.saved_ids.remove(link)
                        st.rerun()
            with c3:
                if st.button("❌ IGNORE", key=f"i_{sid}", use_container_width=True):
                    db.update_startup_status(link, "Ignore")
                    if link in st.session_state.discovery_ids: st.session_state.discovery_ids.remove(link)
                    if link in st.session_state.saved_ids: st.session_state.saved_ids.remove(link)
                    st.rerun()
            with c4:
                if st.button("⛔ N/A", key=f"n_{sid}", use_container_width=True):
                    db.update_startup_status(link, "Not Applicable")
                    if link in st.session_state.discovery_ids: st.session_state.discovery_ids.remove(link)
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

with col_side:
    st.markdown("### 📊 INSIGHTS")
    if all_startups:
        # Score Distribution
        fig_score = go.Figure(data=[go.Histogram(x=[int(s.get('confidence_score', 0)) for s in all_startups], nbinsx=10, marker_color='#58a6ff')])
        fig_score.update_layout(title="Quality Distribution", template="plotly_dark", 
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               height=250, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_score, use_container_width=True)

        # Source Breakdown
        src_counts = {}
        for s in all_startups:
            src = s.get("source", "Unknown")
            src_counts[src] = src_counts.get(src, 0) + 1
        
        fig_src = go.Figure(data=[go.Pie(labels=list(src_counts.keys()), values=list(src_counts.values()), hole=0.6)])
        fig_src.update_layout(title="Source Mix", template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)", height=250, 
                            margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig_src, use_container_width=True)

        # Status Summary
        status_map = {"Pending": "⏳", "Save": "💾", "Progress": "🚀", "Ignore": "❌"}
        stats = {}
        for s in all_startups:
            stt = s.get("status", "Pending")
            stats[stt] = stats.get(stt, 0) + 1
        
        st.markdown("#### Database Pulse")
        for stt, count in stats.items():
            st.markdown(f"{status_map.get(stt, '📌')} **{stt}**: {count}")
    else:
        st.info("Ecosystem data arriving soon...")
