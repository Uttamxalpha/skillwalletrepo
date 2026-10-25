"""
Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1 • Generative AI & Real Estate Decision Support
Platform ID: 6ac4c98d1dcde6d7857c1642
Turnkey Production-Ready Streamlit Application
"""

import sys
import os

# Auto-launch Streamlit if executed directly via python app.py
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    _ctx = get_script_run_ctx()
except Exception:
    _ctx = None

if _ctx is None and __name__ == "__main__":
    venv_python = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python3")
    py_exec = venv_python if os.path.exists(venv_python) else sys.executable
    print("=" * 70)
    print("🏗️ CONSTRUCT-AI: Launching Streamlit Web Application...")
    print("👉 Open your browser at: http://localhost:8501")
    print("=" * 70)
    os.execv(py_exec, [py_exec, "-m", "streamlit", "run", __file__])

import streamlit as st
from PIL import Image

# Configuration & Modules
import config
from modules.gemini_client import ConstructionGeminiClient
from modules.ppe_audit import render_ppe_audit_tab
from modules.crack_diagnostics import render_crack_diagnostics_tab
from modules.valuation_planning import render_valuation_planning_tab
from modules.chatbot_assistant import render_weather_and_chatbot_tab

# Page Configuration
st.set_page_config(
    page_title=f"{config.PLATFORM_TITLE} | {config.PLATFORM_ID}",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load Sample Images for 1-Click Evaluation
sample_ppe_path = os.path.join(os.path.dirname(__file__), "assets", "sample_ppe_site.jpg")
sample_crack_path = os.path.join(os.path.dirname(__file__), "assets", "sample_crack_defect.jpg")

sample_ppe_bytes = None
sample_crack_bytes = None
if os.path.exists(sample_ppe_path):
    with open(sample_ppe_path, "rb") as f:
        sample_ppe_bytes = f.read()

if os.path.exists(sample_crack_path):
    with open(sample_crack_path, "rb") as f:
        sample_crack_bytes = f.read()

# Sidebar Implementation (Requirement 1 & Epic 1)
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 12px 0 16px 0;">
            <div style="font-size: 2.8rem; margin-bottom: 4px;">🏗️</div>
            <h2 style="font-size: 1.25rem; margin: 0; color: #F8FAFC; font-weight: 700;">CONSTRUCT-AI</h2>
            <div style="color: #F59E0B; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.05em; margin-top: 4px;">
                PLATFORM ID: {config.PLATFORM_ID}
            </div>
            <div style="color: #94A3B8; font-size: 0.78rem;">Category: Generative AI | Real Estate</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("#### 🔑 Model & API Authentication")

    env_api_key = os.environ.get("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        placeholder="AIzaSy...",
        help="Paste your Google Gemini API key. If empty, the platform automatically engages the high-fidelity Demonstration Mode."
    )

    model_choice = st.selectbox(
        "Vision LLM Engine",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Select multimodal vision reasoning model."
    )

    # Initialize Gemini Client
    effective_key = api_key_input.strip() if api_key_input else env_api_key
    gemini_client = ConstructionGeminiClient(api_key=effective_key, model_name=model_choice)

    # Mode Status Pill
    if gemini_client.is_live:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 8px; padding: 8px 12px; text-align: center; margin-top: 8px;">
                <span style="color: #10B981; font-weight: 700; font-size: 0.88rem;">🟢 Live Gemini Multimodal Active</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; border-radius: 8px; padding: 8px 12px; text-align: center; margin-top: 8px;">
                <span style="color: #F59E0B; font-weight: 700; font-size: 0.88rem;">⚡ Demonstration Mode Active</span>
                <div style="color: #CBD5E1; font-size: 0.75rem; margin-top: 2px;">Offline forensic simulation & zero-crash fallback</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📐 Architecture & Pipeline Overview")
    with st.expander("View Multimodal Pipeline Flow"):
        st.markdown(
            """
            **End-to-End Decision Topology:**
            1. **Vision Ingestion:** High-resolution field photos (JPG/PNG).
            2. **Multimodal LLM:** Gemini Vision structured prompt with zero-shot domain priors.
            3. **Pydantic Contracts:** Schema validation on `PPEAuditResponse` & `CrackDiagnosticResponse`.
            4. **Financial BoQ Engine:** Real Estate CapEx & IS 456 material estimation in INR.
            5. **Dynamic Microclimate:** Live hazard matrix adjusting crane & concrete protocols.
            6. **Generative Renders:** Pollinations / Flux API 3D architectural perspective.
            """
        )

    st.markdown("#### 📋 Kanban Epics Coverage")
    with st.expander("Audit 7 Epics Compliance", expanded=False):
        for epic in config.KANBAN_EPICS:
            st.markdown(f"**{epic['id']}:** {epic['title']}")
            st.caption(f"{epic['desc']}")
            st.markdown("<hr style='margin: 4px 0 8px 0; border-color: #334155;'>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"Construct-AI Core v{config.VERSION} • Zero-DB Cloud Deploy Ready")


# Top Hero Header
st.markdown(
    f"""
    <div class="platform-header">
        <span class="platform-badge">{config.PLATFORM_SUBTITLE}</span>
        <h1 style="color: #F8FAFC; margin: 4px 0 6px 0; font-size: 2.1rem; font-weight: 800;">
            🏗️ {config.PLATFORM_TITLE}
        </h1>
        <p style="color: #94A3B8; font-size: 0.98rem; margin: 0; line-height: 1.5;">
            Intelligent multimodal vision decision-support system auditing PPE safety compliance under OSHA 1926,
            classifying concrete crack defects under IS 456:2000, estimating Indian Real Estate CapEx in INR,
            and automating weather-aware site operations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 4 Core Functional Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 1. Site Safety & PPE Audit",
    "🧱 2. Crack Diagnostics & Integrity",
    "📊 3. Planning & Real Estate Valuation",
    "🌦️ 4. Daily Assistant & Weather Advisory"
])

with tab1:
    render_ppe_audit_tab(gemini_client, sample_image_bytes=sample_ppe_bytes)

with tab2:
    render_crack_diagnostics_tab(gemini_client, sample_image_bytes=sample_crack_bytes)

with tab3:
    render_valuation_planning_tab()

with tab4:
    render_weather_and_chatbot_tab(gemini_client)

# App Footer
st.markdown("---")
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    st.caption("🛡️ **Audited Standards:** OSHA 1926 (Subparts E, M, P) • IS 456:2000 • IS 13415:1992 • NBC 2016")
with f2:
    st.caption(f"📌 **Platform ID:** `{config.PLATFORM_ID}`")
with f3:
    st.caption("🚀 **Deployment:** 1-Click Streamlit Community Cloud")

