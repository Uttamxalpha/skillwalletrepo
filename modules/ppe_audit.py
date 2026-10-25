"""
Site Safety & PPE Audit UI Component (Tab 1 - Epic 2)
Platform ID: 6ac4c98d1dcde6d7857c1642
Audits construction site worker PPE compliance under OSHA 1926 & IS 13415 / IS 456 standards.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import json
from PIL import Image
import io
import plotly.graph_objects as go
from modules.gemini_client import ConstructionGeminiClient

def render_ppe_audit_tab(gemini_client: ConstructionGeminiClient, sample_image_bytes: bytes = None):
    st.markdown("## 🦺 Site Safety & PPE Compliance Audit")
    st.caption("AI-Powered Vision Audit for OSHA 1926 & IS 13415 / IS 456 Regulatory Compliance")

    # Legal & Safety Inspection Disclaimer Banner
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid #38BDF8; border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.84rem; color: #94A3B8;">
            🛡️ <b>Legal & Safety Notice:</b> This automated visual assessment is an assistive decision-support tool. It does <b>not</b> guarantee legal compliance under OSHA 1926 or IS 13415 and cannot replace in-person physical inspections by qualified site safety engineers.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_upload, col_preview = st.columns([1, 1], gap="medium")

    with col_upload:
        st.markdown("#### 1. Upload or Select Site Image")
        uploaded_file = st.file_uploader(
            "Upload Construction Site Photo (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            key="ppe_uploader",
            help="High-resolution aerial or ground photos of active construction workers."
        )

        sample_btn = st.button("📸 Load Sample High-Rise Site Photo", key="btn_ppe_sample", use_container_width=True)
        if sample_btn:
            st.session_state["ppe_use_sample"] = True
            st.session_state["ppe_active_image"] = sample_image_bytes
            st.session_state["ppe_image_name"] = "sample_highrise_site_ppe.jpg"

        if uploaded_file is not None:
            st.session_state["ppe_use_sample"] = False
            st.session_state["ppe_active_image"] = uploaded_file.getvalue()
            st.session_state["ppe_image_name"] = uploaded_file.name

        active_img_bytes = st.session_state.get("ppe_active_image", None)
        active_img_name = st.session_state.get("ppe_image_name", "None")

        st.info(f"**Selected Image:** {active_img_name}")

        analyze_disabled = active_img_bytes is None
        analyze_btn = st.button(
            "🚀 Run AI Safety Compliance Audit",
            type="primary",
            disabled=analyze_disabled,
            use_container_width=True,
            key="btn_run_ppe_audit"
        )

    with col_preview:
        st.markdown("#### 2. Site Image Preview")
        if active_img_bytes:
            try:
                image = Image.open(io.BytesIO(active_img_bytes))
                st.image(image, caption=f"Active Site Capture: {active_img_name}", use_container_width=True)
            except Exception as e:
                st.error(f"Unable to render image: {str(e)}")
        else:
            st.markdown(
                """
                <div style="border: 2px dashed #475569; border-radius: 12px; padding: 50px 20px; text-align: center; color: #94A3B8; background: rgba(30, 41, 59, 0.4);">
                    <div style="font-size: 3rem; margin-bottom: 10px;">🏗️</div>
                    <p style="font-size: 1.05rem; font-weight: 500; margin: 0;">Upload a site photo or click <b>Load Sample High-Rise Site Photo</b></p>
                    <p style="font-size: 0.85rem; color: #64748B;">Supported: JPEG, PNG • Analyzes helmets, vests, boots, harnesses, and open hazards</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Execution & Results
    if analyze_btn and active_img_bytes:
        with st.spinner("Analyzing worker PPE adherence, identifying safety anomalies, and validating against OSHA 1926..."):
            audit_result, is_mock = gemini_client.analyze_ppe_compliance(active_img_bytes, active_img_name)
            st.session_state["ppe_audit_result"] = audit_result
            st.session_state["ppe_is_mock"] = is_mock

    # Render results if present in state
    if "ppe_audit_result" in st.session_state:
        res = st.session_state["ppe_audit_result"]
        is_mock = st.session_state.get("ppe_is_mock", False) or res.get("is_demonstration_mode", False)

        st.markdown("---")
        st.markdown("### 📋 Safety Audit Diagnostics & Findings")

        if is_mock:
            st.warning(
                "⚡ **DEMONSTRATION MODE ACTIVE:** Google Gemini API credentials are not active. "
                "The findings displayed below are **pre-configured baseline demonstration scenario data** "
                "and do NOT represent an AI analysis of the uploaded image."
            )

        # Top Metric Cards
        score = res.get("safety_score", 0)
        overall_status = res.get("overall_status", "Unknown")
        worker_count = res.get("worker_count_detected", 0)
        compliant_workers = res.get("fully_compliant_workers", 0)

        status_color = "#10B981" if score >= 85 else ("#F59E0B" if score >= 70 else "#EF4444")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Overall Safety Score", value=f"{score} / 100", delta="OSHA Benchmark" if score >= 80 else "-Action Required")
        with m2:
            st.metric(label="Compliance Status", value=overall_status)
        with m3:
            st.metric(label="Workers Monitored", value=f"{worker_count} Personnel")
        with m4:
            compliance_pct = int((compliant_workers / worker_count * 100)) if worker_count > 0 else 0
            st.metric(label="Fully Compliant", value=f"{compliant_workers} ({compliance_pct}%)")

        st.info(f"**Executive Observation Summary:** {res.get('summary', 'No summary provided.')}")

        # Gauge Chart + Checklist
        c_chart, c_checklist = st.columns([1, 1], gap="medium")

        with c_chart:
            st.markdown("##### 🎯 Safety Score Benchmark Gauge")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Safety Compliance Rating (0-100)", 'font': {'size': 16, 'color': '#F8FAFC'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': status_color},
                    'bgcolor': "#1E293B",
                    'borderwidth': 1,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 50], 'color': '#7F1D1D'},
                        {'range': [50, 75], 'color': '#78350F'},
                        {'range': [75, 100], 'color': '#064E3B'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 3},
                        'thickness': 0.8,
                        'value': 85
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#F8FAFC'},
                height=260,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with c_checklist:
            st.markdown("##### ✅ Mandatory PPE Detection Checklist")
            checklist = res.get("ppe_checklist", [])
            for item in checklist:
                c_status = item.get("compliance_status", "Uncertain / Not Visible")
                if c_status in ["Present", "Compliant"]:
                    icon = "🟢"
                    badge_bg = "rgba(16, 185, 129, 0.2)"
                    badge_color = "#10B981"
                elif c_status in ["Missing", "Violation"]:
                    icon = "🔴"
                    badge_bg = "rgba(239, 68, 68, 0.2)"
                    badge_color = "#EF4444"
                elif c_status in ["Uncertain / Not Visible", "Partial"]:
                    icon = "🟡"
                    badge_bg = "rgba(245, 158, 11, 0.2)"
                    badge_color = "#F59E0B"
                else:
                    icon = "⚪"
                    badge_bg = "rgba(148, 163, 184, 0.2)"
                    badge_color = "#94A3B8"

                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {status_color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; font-size: 0.95rem;">{icon} {item.get('item')}</span>
                                <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 700;">{c_status}</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">{item.get('notes')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Identified Site Hazards Section
        st.markdown("#### ⚠️ Identified Site Hazards & Immediate Remediation Plan")
        hazards = res.get("identified_hazards", [])
        if hazards:
            for idx, h in enumerate(hazards, 1):
                sev = h.get("severity", "Medium")
                with st.expander(f"Hazard #{idx}: {h.get('hazard_title')} [Severity: {sev}]", expanded=(sev in ["Critical", "High"])):
                    st.markdown(f"**Identified Zone:** `{h.get('location_in_photo')}`")
                    st.markdown(f"**Regulatory Standard Violated:** `{h.get('standard_violated')}`")
                    st.markdown(f"**🚨 Immediate Corrective Action:** {h.get('immediate_corrective_remedy')}")
                    st.markdown(f"**🛡️ Long-term Preventive Measure:** {h.get('preventive_measure')}")
        else:
            st.success("No critical or high-severity hazards detected in the inspected site zone.")

        # Cited Standards
        standards = res.get("standards_cited", [])
        if standards:
            st.markdown("##### 📜 Audited Regulatory Standards")
            st.write(", ".join([f"`{s}`" for s in standards]))

        # Downloadable Report
        st.markdown("---")
        col_dl1, col_dl2 = st.columns([1, 2])
        with col_dl1:
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="📥 Download Structured JSON Safety Report",
                data=json_str,
                file_name=f"ppe_safety_audit_{res.get('audit_timestamp', 'report')[:10]}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    print("=" * 70)
    print("🦺 CONSTRUCT-AI: PPE Safety Audit Module (Epic 2)")
    print("Platform ID: 6ac4c98d1dcde6d7857c1642")
    print("=" * 70)
    client = ConstructionGeminiClient()
    mock_res = client.get_mock_ppe_audit("sample.jpg")
    print(f"Safety Score: {mock_res['safety_score']}/100")
    print(f"Overall Status: {mock_res['overall_status']}")
    print(f"Checklist Items Audited: {len(mock_res['ppe_checklist'])}")
    print(f"Hazards Identified: {len(mock_res['identified_hazards'])}")
    print("=" * 70)
    print("✅ PPE Audit module loaded and verified successfully!")
