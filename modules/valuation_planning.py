"""
Planning & Real Estate Valuation Module (Epic 3)
Platform ID: 6ac4c98d1dcde6d7857c1642
Calculates Indian Real Estate CapEx, Market Asset Valuation (INR Lakhs/Crores),
and BoQ Material Requirements (Steel & Cement) with milestone indicators.
"""

from typing import Dict, Any
from config import LOCATION_TIERS, STRUCTURE_SPECS, MATERIAL_GRADES, COMMODITY_RATES

def format_inr(amount: float) -> str:
    """Formats an INR amount into Crores (Cr) or Lakhs (L)."""
    if amount >= 10_000_000:
        cr = amount / 10_000_000
        return f"₹{cr:,.2f} Cr"
    elif amount >= 100_000:
        lakhs = amount / 100_000
        return f"₹{lakhs:,.2f} L"
    else:
        return f"₹{amount:,.0f}"

def calculate_project_financials(
    structure_type: str,
    built_up_sqft: float,
    location_tier_name: str,
    completion_pct: float,
    material_grade_name: str = "Standard Builder Grade (Fe500 Steel, M25 Concrete, Vitrified Tiles)",
    land_area_sqft: float = None,
    current_market_rate_override: float = None
) -> Dict[str, Any]:
    """
    Computes CapEx, Current Valuation, Remaining Budget, and BoQ requirements.
    """
    tier_info = LOCATION_TIERS.get(location_tier_name, list(LOCATION_TIERS.values())[0])
    struct_info = STRUCTURE_SPECS.get(structure_type, list(STRUCTURE_SPECS.values())[0])
    grade_multiplier = MATERIAL_GRADES.get(material_grade_name, 1.00)

    # Base construction cost per sq ft
    unit_cost_sqft = tier_info["base_construction_sqft"] * struct_info["cost_multiplier"] * grade_multiplier
    total_construction_budget = unit_cost_sqft * built_up_sqft

    # Land & Approval Component (typically 30-45% of total asset capitalization in India)
    land_cost_factor = 0.40 if tier_info["tier"] == "Tier 1" else 0.30
    estimated_land_and_preconstruction = total_construction_budget * land_cost_factor

    total_project_capex_budget = total_construction_budget + estimated_land_and_preconstruction

    # CapEx Incurred to date
    # Land & initial approvals are 100% committed upfront, construction scales with completion %
    construction_incurred = total_construction_budget * (completion_pct / 100.0)
    capex_incurred = estimated_land_and_preconstruction + construction_incurred
    capex_remaining = max(0.0, total_project_capex_budget - capex_incurred)

    # Market Valuation Calculation
    market_rate_sqft = current_market_rate_override or tier_info["base_market_rate_sqft"]
    gross_market_potential = built_up_sqft * market_rate_sqft

    # In Indian real estate finance (RERA/NBFC benchmarks), an under-construction property is valued as:
    # Asset Value = Sunk CapEx (Land + Incurred Civil) + (Completion Progress * Development Margin) + Discounted Future Net Cash Flows
    # At 0%, value ~ Land Value. At 100%, value = Gross Market Potential.
    # Risk-discount curve: As completion % rises, the completion discount decreases.
    completion_factor = completion_pct / 100.0
    value_discount_factor = 0.65 + (0.35 * (completion_factor ** 0.85))
    current_asset_valuation = (
        estimated_land_and_preconstruction +
        (gross_market_potential - estimated_land_and_preconstruction) * completion_factor * value_discount_factor
    )

    # Material Requirement Thumb Rules (per IS 456 & CPWD DSR norms)
    factor_k_sqft = built_up_sqft / 1000.0
    total_steel_mt = struct_info["steel_mt_per_1000sqft"] * factor_k_sqft
    total_cement_bags = struct_info["cement_bags_per_1000sqft"] * factor_k_sqft
    total_sand_cft = struct_info["sand_cft_per_1000sqft"] * factor_k_sqft
    total_aggregate_cft = struct_info["aggregate_cft_per_1000sqft"] * factor_k_sqft

    # Materials consumed vs remaining based on completion
    steel_consumed_mt = total_steel_mt * (completion_pct / 100.0)
    steel_remaining_mt = total_steel_mt - steel_consumed_mt

    cement_consumed_bags = total_cement_bags * (completion_pct / 100.0)
    cement_remaining_bags = total_cement_bags - cement_consumed_bags

    # Embodied Carbon Footprint Estimate (IS / IGBC norms: ~0.82 kg CO2e/kg cement, ~1.85 kg CO2e/kg steel)
    carbon_footprint_tonnes = (
        (total_steel_mt * 1.85) +
        ((total_cement_bags * 50 / 1000.0) * 0.82)
    )

    # BoQ Cost Trade Breakdown
    civil_cost = total_construction_budget * struct_info["civil_cost_pct"]
    mep_cost = total_construction_budget * struct_info["mep_cost_pct"]
    finishing_cost = total_construction_budget * struct_info["finishing_cost_pct"]
    contingency_cost = total_construction_budget * struct_info["contingency_pct"]

    return {
        "built_up_sqft": built_up_sqft,
        "completion_pct": completion_pct,
        "location_tier": tier_info["tier"],
        "unit_construction_cost_sqft": unit_cost_sqft,
        "market_rate_sqft": market_rate_sqft,
        "total_construction_budget": total_construction_budget,
        "total_construction_budget_str": format_inr(total_construction_budget),
        "total_capex_budget": total_project_capex_budget,
        "total_capex_budget_str": format_inr(total_project_capex_budget),
        "capex_incurred": capex_incurred,
        "capex_incurred_str": format_inr(capex_incurred),
        "capex_remaining": capex_remaining,
        "capex_remaining_str": format_inr(capex_remaining),
        "current_asset_valuation": current_asset_valuation,
        "current_asset_valuation_str": format_inr(current_asset_valuation),
        "gross_completed_valuation": gross_market_potential,
        "gross_completed_valuation_str": format_inr(gross_market_potential),
        "materials": {
            "steel_total_mt": round(total_steel_mt, 1),
            "steel_consumed_mt": round(steel_consumed_mt, 1),
            "steel_remaining_mt": round(steel_remaining_mt, 1),
            "cement_total_bags": int(total_cement_bags),
            "cement_consumed_bags": int(cement_consumed_bags),
            "cement_remaining_bags": int(cement_remaining_bags),
            "cement_total_mt": round(total_cement_bags * 0.05, 1),
            "sand_total_cft": int(total_sand_cft),
            "aggregate_total_cft": int(total_aggregate_cft),
            "carbon_footprint_tonnes": round(carbon_footprint_tonnes, 1)
        },
        "trade_breakdown": {
            "Civil RCC & Superstructure": civil_cost,
            "MEP & Electrical Services": mep_cost,
            "Finishing & Glazing": finishing_cost,
            "Contingency & Safety": contingency_cost,
            "Land & Regulatory Approvals": estimated_land_and_preconstruction
        }
    }


def render_valuation_planning_tab():
    import streamlit as st
    import plotly.graph_objects as go
    from modules.pollinations_render import (
        ARCHITECTURAL_STYLES,
        LIGHTING_CONDITIONS,
        generate_architectural_prompt,
        get_pollinations_image_url
    )

    st.markdown("## 📊 Project Planning & Real Estate Valuation (Epic 3)")
    st.caption("Indian Real Estate Asset Capitalization, Incurred CapEx, BoQ Commodity Forecasting & Generative 3D Renders")

    # Input Control Cards
    with st.container():
        st.markdown("#### 1. Project Specifications & Location Parameters")
        c1, c2 = st.columns(2)
        with c1:
            structure_type = st.selectbox(
                "🏢 Structure / Asset Typology",
                options=list(STRUCTURE_SPECS.keys()),
                index=0,
                help="Defines structural load profile, steel-to-concrete density, and civil specifications."
            )
            built_up_sqft = st.number_input(
                "📐 Built-up Area (Sq. Ft.)",
                min_value=2000,
                max_value=2000000,
                value=75000,
                step=5000,
                help="Total gross built-up floor plate area across all levels."
            )
        with c2:
            location_tier = st.selectbox(
                "📍 Location Tier (Indian Real Estate)",
                options=list(LOCATION_TIERS.keys()),
                index=0,
                help="Tier 1 (Metro hubs), Tier 2 (Growth cities), Tier 3 (Emerging centers)."
            )
            material_grade = st.selectbox(
                "🏗️ Material Specification Grade",
                options=list(MATERIAL_GRADES.keys()),
                index=1,
                help="Governs steel grades (Fe500 vs Fe550D), concrete grade (M25 to M40+), and finishing spec."
            )

    st.markdown("#### 2. Construction Milestone & Execution Progress")
    completion_pct = st.slider(
        "Current Site Milestone Completion (%)",
        min_value=0,
        max_value=100,
        value=45,
        step=5,
        help="0% = Pre-excavation land phase; 45% = Superstructure RCC framed; 100% = Handover / Occupancy Certificate."
    )

    # Compute Financials
    fin = calculate_project_financials(
        structure_type=structure_type,
        built_up_sqft=built_up_sqft,
        location_tier_name=location_tier,
        completion_pct=completion_pct,
        material_grade_name=material_grade
    )

    st.markdown("---")
    st.markdown("### 💰 Financial Capitalization & Valuation Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Total Project Budget",
            value=fin["total_capex_budget_str"],
            help="Total estimated project cost including land acquisition, approvals, and construction."
        )
    with m2:
        st.metric(
            label="CapEx Incurred to Date",
            value=fin["capex_incurred_str"],
            delta=f"{completion_pct}% Execution"
        )
    with m3:
        st.metric(
            label="Remaining CapEx Needed",
            value=fin["capex_remaining_str"],
            delta=f"{100 - completion_pct}% Remaining",
            delta_color="inverse"
        )
    with m4:
        st.metric(
            label="Current Market Asset Valuation",
            value=fin["current_asset_valuation_str"],
            delta=f"Fully Built: {fin['gross_completed_valuation_str']}"
        )

    # Detailed Cost Breakdown & Material BoQ
    col_chart, col_boq = st.columns([1, 1], gap="medium")

    with col_chart:
        st.markdown("##### 🥧 Project Capitalization Trade Breakdown")
        trades = list(fin["trade_breakdown"].keys())
        values = list(fin["trade_breakdown"].values())

        fig_donut = go.Figure(data=[go.Pie(
            labels=trades,
            values=values,
            hole=0.55,
            marker=dict(colors=["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]),
            textinfo="label+percent"
        )])
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#F8FAFC'},
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_boq:
        st.markdown("##### 🏗️ BoQ Material Forecaster & Inventory Tracking")
        mat = fin["materials"]

        # Steel Metric
        st.markdown(f"**Structural Steel (TMT Fe500D/550D):** {mat['steel_consumed_mt']} MT consumed / **{mat['steel_total_mt']} MT Total**")
        steel_progress = min(1.0, mat['steel_consumed_mt'] / max(1.0, mat['steel_total_mt']))
        st.progress(steel_progress)

        # Cement Metric
        st.markdown(f"**Cement (OPC 53 / PPC):** {mat['cement_consumed_bags']:,} bags consumed / **{mat['cement_total_bags']:,} bags Total** (~{mat['cement_total_mt']} MT)")
        cement_progress = min(1.0, mat['cement_consumed_bags'] / max(1.0, mat['cement_total_bags']))
        st.progress(cement_progress)

        # Carbon & Aggregates
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 0.88rem; border-left: 3px solid #10B981;">
                🌱 <b>Embodied Carbon Footprint:</b> ~{mat['carbon_footprint_tonnes']:,} tCO₂e<br>
                ⏳ <b>Sand & Aggregates:</b> ~{mat['sand_total_cft']:,} cft Sand • ~{mat['aggregate_total_cft']:,} cft Coarse Aggregate
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3D Architectural Rendering via Pollinations AI
    st.markdown("---")
    st.markdown("### 🎨 Conceptual 3D Architectural Rendering (Pollinations / Flux AI)")
    st.caption("Generate photorealistic structural perspective renders matching the selected building typography and location tier.")

    col_render_controls, col_render_view = st.columns([1, 1], gap="medium")

    with col_render_controls:
        render_style = st.selectbox("Design Aesthetic / Façade Style", options=ARCHITECTURAL_STYLES, index=0)
        render_lighting = st.selectbox("Atmospheric Lighting & Environment", options=LIGHTING_CONDITIONS, index=0)
        custom_notes = st.text_input("Custom Design Elements (Optional)", placeholder="e.g. rooftop helipad, curved glass canopy, vertical garden pods")

        generated_prompt = generate_architectural_prompt(
            structure_type=structure_type,
            tier_name=fin["location_tier"],
            style=render_style,
            lighting=render_lighting,
            custom_enhancements=custom_notes
        )

        with st.expander("📝 View Synthesized AI Vision Prompt"):
            st.code(generated_prompt, language="text")

        gen_render_btn = st.button("🖼️ Generate 3D Architectural Render", type="primary", use_container_width=True)

    with col_render_view:
        if gen_render_btn or "pollinations_active_url" in st.session_state:
            if gen_render_btn:
                import random
                seed = random.randint(10000, 999999)
                render_url = get_pollinations_image_url(generated_prompt, seed=seed, width=1024, height=640)
                st.session_state["pollinations_active_url"] = render_url
                st.session_state["pollinations_prompt"] = generated_prompt

            active_url = st.session_state["pollinations_active_url"]
            with st.spinner("Streaming high-resolution 3D architectural render via Flux API..."):
                st.image(active_url, caption="Conceptual 3D Visualization (Pollinations AI / Flux)", use_container_width=True)
                st.markdown(f"[🔗 Direct High-Res Image Link]({active_url})")
        else:
            st.markdown(
                """
                <div style="border: 2px dashed #475569; border-radius: 12px; padding: 45px 20px; text-align: center; color: #94A3B8; background: rgba(30, 41, 59, 0.4);">
                    <div style="font-size: 3rem; margin-bottom: 8px;">🏢</div>
                    <p style="font-size: 1rem; font-weight: 500; margin: 0;">Click <b>Generate 3D Architectural Render</b> to trigger real-time AI rendering.</p>
                    <p style="font-size: 0.85rem; color: #64748B;">Powered by Pollinations / Flux API • Photorealistic 8K Architectural Visualization</p>
                </div>
                """,
                unsafe_allow_html=True
            )
