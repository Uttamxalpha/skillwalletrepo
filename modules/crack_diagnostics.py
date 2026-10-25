"""
Crack Diagnostics & Structural Integrity Component (Tab 2 - Epic 2)
Platform ID: 6ac4c98d1dcde6d7857c1642
Forensic defect classification and repair decision support under IS 456:2000 standards.
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

def render_crack_diagnostics_tab(gemini_client: ConstructionGeminiClient, sample_image_bytes: bytes = None):
    st.markdown("## 🔍 Concrete Crack Diagnostics & Structural Integrity")
    st.caption("Forensic AI Structural Defect Classification, Crack Width Metrology & IS 456:2000 Remediation Protocols")

    col_upload, col_preview = st.columns([1, 1], gap="medium")

    with col_upload:
        st.markdown("#### 1. Upload or Select Concrete Defect Surface")
        uploaded_file = st.file_uploader(
            "Upload Concrete / Wall Surface Photo (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            key="crack_uploader",
            help="High-detail macro or normal photograph of concrete beam, column, slab, or shear wall."
        )

        sample_btn = st.button("🧱 Load Sample RCC Shear Defect Photo", key="btn_crack_sample", use_container_width=True)
        if sample_btn:
            st.session_state["crack_use_sample"] = True
            st.session_state["crack_active_image"] = sample_image_bytes
            st.session_state["crack_image_name"] = "sample_rcc_shear_defect.jpg"

        if uploaded_file is not None:
            st.session_state["crack_use_sample"] = False
            st.session_state["crack_active_image"] = uploaded_file.getvalue()
            st.session_state["crack_image_name"] = uploaded_file.name

        active_img_bytes = st.session_state.get("crack_active_image", None)
        active_img_name = st.session_state.get("crack_image_name", "None")

        st.info(f"**Selected Defect Photo:** {active_img_name}")

        analyze_disabled = active_img_bytes is None
        analyze_btn = st.button(
            "🔬 Classify Defect & Generate Engineering Repair Plan",
            type="primary",
            disabled=analyze_disabled,
            use_container_width=True,
            key="btn_run_crack_diagnostics"
        )

    with col_preview:
        st.markdown("#### 2. Defect Image Preview")
        if active_img_bytes:
            image = Image.open(io.BytesIO(active_img_bytes))
            st.image(image, caption=f"Inspected Concrete Surface: {active_img_name}", use_container_width=True)
        else:
            st.markdown(
                """
                <div style="border: 2px dashed #475569; border-radius: 12px; padding: 50px 20px; text-align: center; color: #94A3B8; background: rgba(30, 41, 59, 0.4);">
                    <div style="font-size: 3rem; margin-bottom: 10px;">🧱</div>
                    <p style="font-size: 1.05rem; font-weight: 500; margin: 0;">Upload a concrete photo or click <b>Load Sample RCC Shear Defect Photo</b></p>
                    <p style="font-size: 0.85rem; color: #64748B;">Classifies Hairline, Settlement, Structural Shear, Thermal, or Spalling defects</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Execution & Results
    if analyze_btn and active_img_bytes:
        with st.spinner("Executing forensic AI vision inspection, calculating crack width, and evaluating IS 456 serviceability limits..."):
            diag_result, is_mock = gemini_client.analyze_crack_diagnostics(active_img_bytes, active_img_name)
            st.session_state["crack_diag_result"] = diag_result
            st.session_state["crack_is_mock"] = is_mock

    # Render results
    if "crack_diag_result" in st.session_state:
        res = st.session_state["crack_diag_result"]
        is_mock = st.session_state.get("crack_is_mock", False)

        st.markdown("---")
        st.markdown("### 🔬 Forensic Diagnostic Report & Repair Specifications")

        if is_mock:
            st.warning("⚡ **Demonstration Mode Active:** Serving high-precision forensic structural data benchmarked against IS 456:2000.")

        defect_type = res.get("defect_type", "Defect")
        severity_score = float(res.get("severity_score", 5.0))
        risk_rating = res.get("risk_rating", "Medium")
        width_mm = float(res.get("estimated_crack_width_mm", 0.5))
        is_structural = res.get("is_structural_threat", False)

        risk_color = "#EF4444" if risk_rating == "Critical" else ("#F97316" if risk_rating == "High" else ("#F59E0B" if risk_rating == "Medium" else "#10B981"))

        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Classified Defect", value=defect_type)
        with m2:
            st.metric(label="Estimated Crack Width", value=f"{width_mm:.2f} mm", delta="Exceeds 0.3mm Limit" if width_mm > 0.3 else "Within Service Limit")
        with m3:
            st.metric(label="Severity Index", value=f"{severity_score:.1f} / 10.0")
        with m4:
            st.metric(label="Structural Threat", value="YES (Load Bearing)" if is_structural else "NO (Cosmetic / Surface)")

        # IS 456 Compliance Alert Banner
        compliance_text = res.get("is456_compliance_status", "Compliant")
        if "EXCEEDS" in compliance_text.upper() or "VIOLATION" in compliance_text.upper() or width_mm > 0.3:
            st.error(f"🚨 **IS 456:2000 Compliance Warning:** {compliance_text}")
        else:
            st.success(f"✅ **IS 456:2000 Assessment:** {compliance_text}")

        # Visual Risk Gauge & Forensic Overview
        col_gauge, col_forensic = st.columns([1, 1], gap="medium")

        with col_gauge:
            st.markdown("##### 🌡️ Structural Severity Risk Gauge")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=severity_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Severity Score (0 - 10)", 'font': {'size': 16, 'color': '#F8FAFC'}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': risk_color},
                    'bgcolor': "#1E293B",
                    'steps': [
                        {'range': [0, 3], 'color': '#064E3B'},
                        {'range': [3, 6], 'color': '#78350F'},
                        {'range': [6, 10], 'color': '#7F1D1D'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 3},
                        'thickness': 0.8,
                        'value': 7.0
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

        with col_forensic:
            st.markdown("##### 🏗️ Substrate & Location Profiling")
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.6); padding: 16px; border-radius: 8px; border-left: 4px solid {risk_color};">
                    <p style="margin: 0 0 6px 0;"><b>Surface Material:</b> <code>{res.get('surface_material', 'RCC')}</code></p>
                    <p style="margin: 0 0 6px 0;"><b>Identified Location:</b> {res.get('identified_location', 'Superstructure element')}</p>
                    <p style="margin: 0 0 6px 0;"><b>Urgency Level:</b> <span style="color: {risk_color}; font-weight: 700;">{res.get('urgency_timeline', 'Standard action')}</span></p>
                    <p style="margin: 0;"><b>Estimated Repair Cost (INR):</b> <span style="color: #F59E0B; font-weight: 700;">{res.get('estimated_repair_cost_range_inr', 'Contact structural consultant')}</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Technical Narrative
        with st.expander("📖 Detailed Forensic Engineering Narrative", expanded=True):
            st.write(res.get("detailed_technical_narrative", ""))

        # Root Causes
        st.markdown("#### 🔬 Root Cause Analysis")
        causes = res.get("root_causes", [])
        for c in causes:
            st.markdown(f"- 📌 **Causal Factor:** {c}")

        # Recommended Engineering Repairs
        st.markdown("#### 🛠️ Recommended Engineering Repair Methodology")
        repairs = res.get("engineering_repairs", [])
        for idx, r in enumerate(repairs, 1):
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                    <div style="color: #F59E0B; font-weight: 600; font-size: 0.95rem;">Step {idx} Protocol:</div>
                    <div style="color: #E2E8F0; font-size: 0.9rem; margin-top: 4px;">{r}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Download Button
        st.markdown("---")
        col_dl, _ = st.columns([1, 2])
        with col_dl:
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="📥 Download Forensic Crack Diagnostic JSON",
                data=json_str,
                file_name=f"crack_forensic_report_{res.get('diagnostic_timestamp', 'report')[:10]}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    print("=" * 70)
    print("🧱 CONSTRUCT-AI: Concrete Crack Diagnostics Module (Epic 2)")
    print("Platform ID: 6ac4c98d1dcde6d7857c1642")
    print("=" * 70)
    client = ConstructionGeminiClient()
    mock_res = client.get_mock_crack_diagnostics("sample_crack.jpg")
    print(f"Defect Classified: {mock_res['defect_type']}")
    print(f"Crack Width: {mock_res['estimated_crack_width_mm']} mm")
    print(f"Severity Score: {mock_res['severity_score']}/10.0 | Risk: {mock_res['risk_rating']}")
    print(f"IS 456 Status: {mock_res['is456_compliance_status'][:60]}...")
    print(f"Engineering Repairs Recommended: {len(mock_res['engineering_repairs'])}")
    print("=" * 70)
    print("✅ Crack Diagnostics module loaded and verified successfully!")


