"""
Daily Site Assistant & Weather-Aware Advisory Component (Tab 4 - Epic 5)
Platform ID: 6ac4c98d1dcde6d7857c1642
Dynamic meteorological hazard mitigation and multi-turn civil engineering chat assistant.
"""

import streamlit as st
from config import WEATHER_PROTOCOLS
from modules.weather_advisory import get_weather_protocol, get_weather_alert_level_color
from modules.gemini_client import ConstructionGeminiClient

PRESET_QUICK_PROMPTS = [
    "Explain IS 456 crack width limits & serviceability rules",
    "Crane wind speed cutoff checklist & free-slew protocol",
    "Hot weather concrete curing & retarder admixture dosing",
    "Heavy-duty scaffolding load capacity & inspection criteria",
    "Basement excavation de-watering & electrical safety protocols"
]

def render_weather_and_chatbot_tab(gemini_client: ConstructionGeminiClient):
    st.markdown("## 🌦️ Daily Site Assistant & Weather-Aware Advisory (Epic 5)")
    st.caption("Real-Time Microclimate Safety Matrix, Dynamic Engineering Protocols & Multi-Turn Site AI Assistant")

    # Section 1: Weather Condition Selector & Dynamic Protocols
    st.markdown("### 1. Active Weather Condition & Hazard Alerts")

    weather_choice = st.selectbox(
        "Current Site Weather / Environmental Condition",
        options=list(WEATHER_PROTOCOLS.keys()),
        index=0,
        help="Select live or forecast atmospheric conditions to trigger automated safety protocol adjustments."
    )

    protocol = get_weather_protocol(weather_choice)
    alert_color = get_weather_alert_level_color(protocol["status"])

    # High-impact dynamic alert header
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.7); border-left: 6px solid {alert_color}; border-radius: 10px; padding: 18px 22px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">{weather_choice}</span>
                <span style="background: {alert_color}; color: #0F172A; font-weight: 800; font-size: 0.85rem; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase;">
                    {protocol['severity']}
                </span>
            </div>
            <div style="font-size: 0.95rem; color: #CBD5E1;">
                Active safety and operational constraints are updated dynamically below under OSHA 1926 & IS 13415 rules.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4-Quadrant Operational Protocol Cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; height: 140px;">
                <div style="color: #F59E0B; font-weight: 700; font-size: 0.92rem; margin-bottom: 4px;">🏗️ Tower Crane & Heavy Hoisting Protocol</div>
                <div style="color: #E2E8F0; font-size: 0.88rem; line-height: 1.4;">{protocol['crane_operations']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; height: 140px;">
                <div style="color: #38BDF8; font-weight: 700; font-size: 0.92rem; margin-bottom: 4px;">⚡ Electrical & Excavation De-watering</div>
                <div style="color: #E2E8F0; font-size: 0.88rem; line-height: 1.4;">{protocol['electrical_safety']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; height: 140px;">
                <div style="color: #10B981; font-weight: 700; font-size: 0.92rem; margin-bottom: 4px;">🧪 Concrete Curing & Pouring Strategy (IS 7861)</div>
                <div style="color: #E2E8F0; font-size: 0.88rem; line-height: 1.4;">{protocol['concrete_protocol']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; height: 140px;">
                <div style="color: #EC4899; font-weight: 700; font-size: 0.92rem; margin-bottom: 4px;">👷 Worker Welfare & Scaffolding Restrictions</div>
                <div style="color: #E2E8F0; font-size: 0.88rem; line-height: 1.4;">{protocol['worker_welfare']} | {protocol['scaffolding_status']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Section 2: Interactive Construction Engineering Assistant Chatbot
    st.markdown("---")
    st.markdown("### 2. Multi-Turn Construction Engineering Site Assistant")
    st.caption("Ask technical questions on IS 456, OSHA, NBC 2016, BoQ calculations, or active site dilemmas.")

    if not gemini_client.is_live:
        st.info("💡 **Demonstration Assistant Mode:** Responds with civil engineering expertise even without a Gemini API key.")

    # Initialize chat message history
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your **SiteAssist AI Engineer**.\n\n"
                    "I can help you interpret **IS 456 / OSHA 1926 standards**, calculate scaffolding load distributions, "
                    "prescribe concrete curing protocols, or troubleshoot on-site structural issues.\n\n"
                    "How can I assist you on the site today?"
                )
            }
        ]

    # Quick Prompt Buttons
    st.markdown("##### ⚡ Quick Engineering Prompts")
    prompt_cols = st.columns(len(PRESET_QUICK_PROMPTS))
    selected_quick_prompt = None
    for i, p_text in enumerate(PRESET_QUICK_PROMPTS):
        label_short = p_text.split("&")[0].strip()
        if prompt_cols[i].button(label_short, key=f"quick_btn_{i}", use_container_width=True):
            selected_quick_prompt = p_text

    # Render Conversation History
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "user":
            st.chat_message("user", avatar="👷").markdown(msg["content"])
        else:
            st.chat_message("assistant", avatar="🏗️").markdown(msg["content"])

    # Handle Input from quick button or chat input
    user_query = st.chat_input("Ask SiteAssist AI a construction engineering or safety question...")

    target_query = selected_quick_prompt or user_query

    if target_query:
        # Append User Message
        st.session_state["chat_messages"].append({"role": "user", "content": target_query})
        st.chat_message("user", avatar="👷").markdown(target_query)

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="🏗️"):
            with st.spinner("Consulting IS 456 / OSHA knowledge base and synthesizing engineering advice..."):
                reply, is_mock = gemini_client.chat_query(
                    query=target_query,
                    conversation_history=st.session_state["chat_messages"],
                    weather_context=protocol
                )
                st.markdown(reply)
                st.session_state["chat_messages"].append({"role": "assistant", "content": reply})

    # Clear Chat History Button
    st.markdown("---")
    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Reset Chat History", use_container_width=True):
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": "Chat history cleared. How can I assist your site operations today?"
                }
            ]
            st.rerun()
