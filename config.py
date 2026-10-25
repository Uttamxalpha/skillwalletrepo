"""
Configuration & Knowledge Base for Multimodal Construction Intelligence Platform
Platform ID: 6ac4c98d1dcde6d7857c1642
Category: Generative AI | Real Estate Decision Support
"""

PLATFORM_ID = "6ac4c98d1dcde6d7857c1642"
PLATFORM_TITLE = "Multimodal Construction Intelligence Platform"
PLATFORM_SUBTITLE = "Skill Wallet Capstone Project 1 • Generative AI & Real Estate Decision Support"
VERSION = "1.0.0-PROD"

KANBAN_EPICS = [
    {"id": "Pre-requisites", "title": "Foundation & Environment", "status": "Ready", "desc": "Python 3.9+, Streamlit, Modern Component Styling"},
    {"id": "Epic 1", "title": "Requirements & Env", "status": "Ready", "desc": "Secure Gemini API key input, graceful demo fallback, sidebar navigation"},
    {"id": "Epic 2", "title": "PPE Safety Vision & Crack Diagnostics", "status": "Ready", "desc": "OSHA & IS 456 compliance, structured defect classification, urgency & repair BoQ"},
    {"id": "Epic 3", "title": "Project Planning & Real Estate Valuation", "status": "Ready", "desc": "INR CapEx, Market valuation (Lakhs/Cr), Steel/Cement BoQ & Pollinations 3D Renders"},
    {"id": "Epic 4", "title": "Multimodal AI & JSON Contracts", "status": "Ready", "desc": "Strict JSON schema contracts, robust error-recovery and audit exports"},
    {"id": "Epic 5", "title": "Site Chatbot & Weather Advisory", "status": "Ready", "desc": "Dynamic hazard matrix (wind, rain, heat), multi-turn civil engineering assistant"},
    {"id": "Epic 6", "title": "Interface, Testing & Deployment", "status": "Ready", "desc": "Streamlit Community Cloud 1-click readiness, zero DB dependencies"}
]

# Location Tier Data for Indian Real Estate
LOCATION_TIERS = {
    "Tier 1 (Metro Hubs: Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai)": {
        "tier": "Tier 1",
        "cities": ["Mumbai", "Delhi-NCR", "Bengaluru", "Hyderabad", "Chennai"],
        "base_construction_sqft": 3200,      # INR per sq ft
        "base_market_rate_sqft": 15500,     # INR per sq ft market selling price
        "land_appreciation_annual": 0.095,   # 9.5% annual
        "labor_daily_avg": 950              # INR/day skilled labor
    },
    "Tier 2 (Growth Cities: Pune, Ahmedabad, Kolkata, Jaipur, Kochi, Lucknow)": {
        "tier": "Tier 2",
        "cities": ["Pune", "Ahmedabad", "Kolkata", "Jaipur", "Kochi", "Lucknow", "Chandigarh"],
        "base_construction_sqft": 2400,
        "base_market_rate_sqft": 8200,
        "land_appreciation_annual": 0.08,
        "labor_daily_avg": 750
    },
    "Tier 3 (Emerging Centers: Indore, Coimbatore, Nagpur, Bhubaneswar, Surat)": {
        "tier": "Tier 3",
        "cities": ["Indore", "Coimbatore", "Nagpur", "Bhubaneswar", "Surat", "Vadodara"],
        "base_construction_sqft": 1850,
        "base_market_rate_sqft": 4800,
        "land_appreciation_annual": 0.065,
        "labor_daily_avg": 600
    }
}

# Structure Specifications & Material Thumb Rules
STRUCTURE_SPECS = {
    "Residential High-Rise (RCC Framed G+20)": {
        "cost_multiplier": 1.20,
        "steel_mt_per_1000sqft": 4.2,      # Metric Tonnes per 1000 sq ft (IS 456 standard)
        "cement_bags_per_1000sqft": 430,   # 50kg bags per 1000 sq ft
        "sand_cft_per_1000sqft": 1800,
        "aggregate_cft_per_1000sqft": 1350,
        "brick_blocks_per_1000sqft": 4200,
        "civil_cost_pct": 0.62,
        "mep_cost_pct": 0.18,
        "finishing_cost_pct": 0.15,
        "contingency_pct": 0.05
    },
    "Commercial Grade-A Office Complex": {
        "cost_multiplier": 1.35,
        "steel_mt_per_1000sqft": 4.8,
        "cement_bags_per_1000sqft": 470,
        "sand_cft_per_1000sqft": 1950,
        "aggregate_cft_per_1000sqft": 1500,
        "brick_blocks_per_1000sqft": 3200,
        "civil_cost_pct": 0.55,
        "mep_cost_pct": 0.25,
        "finishing_cost_pct": 0.15,
        "contingency_pct": 0.05
    },
    "Luxury G+2 Villa / Independent Residence": {
        "cost_multiplier": 1.28,
        "steel_mt_per_1000sqft": 3.6,
        "cement_bags_per_1000sqft": 400,
        "sand_cft_per_1000sqft": 1650,
        "aggregate_cft_per_1000sqft": 1200,
        "brick_blocks_per_1000sqft": 4800,
        "civil_cost_pct": 0.50,
        "mep_cost_pct": 0.18,
        "finishing_cost_pct": 0.27,
        "contingency_pct": 0.05
    },
    "Industrial Logistics Warehouse (PEB + Heavy Slab)": {
        "cost_multiplier": 0.90,
        "steel_mt_per_1000sqft": 5.4,      # Heavy structural steel frame
        "cement_bags_per_1000sqft": 330,   # Industrial flooring slabs
        "sand_cft_per_1000sqft": 1400,
        "aggregate_cft_per_1000sqft": 1450,
        "brick_blocks_per_1000sqft": 1800,
        "civil_cost_pct": 0.68,
        "mep_cost_pct": 0.16,
        "finishing_cost_pct": 0.10,
        "contingency_pct": 0.06
    },
    "Mixed-Use Retail & Residential Complex": {
        "cost_multiplier": 1.25,
        "steel_mt_per_1000sqft": 4.5,
        "cement_bags_per_1000sqft": 450,
        "sand_cft_per_1000sqft": 1850,
        "aggregate_cft_per_1000sqft": 1400,
        "brick_blocks_per_1000sqft": 3900,
        "civil_cost_pct": 0.58,
        "mep_cost_pct": 0.22,
        "finishing_cost_pct": 0.15,
        "contingency_pct": 0.05
    }
}

MATERIAL_GRADES = {
    "Standard Builder Grade (Fe500 Steel, M25 Concrete, Vitrified Tiles)": 1.00,
    "Premium Engineered Grade (Fe550D TMT, M30-M35 Concrete, Italian Marble & Façade)": 1.22,
    "Luxury Sustainable / Ultra-High Spec (Corrosion Resistant TMT, Self-Compacting M40+, Low-E Glass)": 1.45
}

# Current approximate Indian material commodity market rates (2025-2026 average)
COMMODITY_RATES = {
    "steel_per_mt": 62000,          # INR per Metric Tonne (Fe500D)
    "cement_per_bag": 380,          # INR per 50kg bag (OPC 53 / PPC)
    "sand_per_cft": 65,             # INR per cubic foot (River/M-Sand)
    "aggregate_per_cft": 42         # INR per cubic foot
}

# Construction Engineering Safety Standards
STANDARDS = {
    "OSHA_1926_E": "OSHA 1926 Subpart E - Personal Protective and Life Saving Equipment (Head, Eye, Foot & Respiratory Protection)",
    "OSHA_1926_M": "OSHA 1926 Subpart M - Fall Protection Systems and Guardrails",
    "IS_456_2000": "IS 456:2000 - Plain and Reinforced Concrete Code of Practice (Limit State of Serviceability & Durability)",
    "IS_13415_1992": "IS 13415:1992 - Code of Safety for Civil Engineering Construction and Demolition Works",
    "NBC_2016": "National Building Code of India 2016 (Volume 1 & 2 - Structural & Life Safety Standards)"
}

# Weather Hazard Matrix & Recommended Engineering Action Protocols
WEATHER_PROTOCOLS = {
    "Normal / Favorable (22°C - 32°C, Wind < 20 km/h)": {
        "status": "Green",
        "severity": "Normal Operations",
        "crane_operations": "Full clearance authorized. Monitor regular mast sway & load moments.",
        "concrete_protocol": "Standard curing cycle (minimum 7 to 10 days for OPC, 14 days for PPC). Standard water ponding or wet hessian cloth.",
        "electrical_safety": "Routine inspections of distribution boxes and residual current circuit breakers (RCCB).",
        "worker_welfare": "Standard 8-hour shift schedule with scheduled hydration pauses.",
        "scaffolding_status": "Inspect weekly and post-minor shifting. Standard green tag active."
    },
    "High Wind Advisory (> 45 km/h / Gale Gusts)": {
        "status": "Red",
        "severity": "CRITICAL WEATHER HALT",
        "crane_operations": "MANDATORY HALT: Weather-vane (free-slew mode) all tower cranes immediately. Lower all suspended loads to ground level.",
        "concrete_protocol": "Fast moisture evaporation risk: apply aliphatic moisture barrier spray. Cover freshly poured slabs with heavy-duty tarpaulins anchored against gusts.",
        "electrical_safety": "Secure overhead temporary power cables to prevent whipping against steel rebars or scaffolding.",
        "worker_welfare": "Suspend all work at height (>1.8m) on scaffolding, boom lifts, and perimeter suspended cradles immediately.",
        "scaffolding_status": "Inspect perimeter safety netting, toe boards, and loose debris on all elevated working decks."
    },
    "Heavy Rain / Monsoon Storm (> 30 mm/hr)": {
        "status": "Red",
        "severity": "HIGH RAINFALL HAZARD",
        "crane_operations": "Halt crane lifts. Ground visibility impaired and high slip hazard on rigging slings.",
        "concrete_protocol": "STOP CONCRETING: Halt external pours immediately. Protect freshly placed concrete with plastic sheets to prevent cement paste washout and cold joints.",
        "electrical_safety": "MANDATORY ISOLATION: De-energize sub-distribution boards in basement/ground excavation pits. Activate sump de-watering pumps with armored IP67 cabling.",
        "worker_welfare": "Mandate high-grip waterproof steel-toe boots (slip resistance SRC rating). Move crews to covered interior dry finishing works.",
        "scaffolding_status": "Excavation trench warning: Soil erosion and slope slippage risk. Maintain 1.5m minimum standoff from trench edges."
    },
    "Extreme Heat Advisory (> 40°C / Heat Index > 46°C)": {
        "status": "Orange",
        "severity": "HEAT STRESS PROTOCOL",
        "crane_operations": "Permitted with operational thermal monitoring of hydraulic fluid and hoist motor temperature.",
        "concrete_protocol": "HOT WEATHER CONCRETING (IS 7861 Part 1): Use chilled mixing water or ice flakes. Pour concrete during dawn/night hours. Apply retarder admixtures. Continuous wet curing.",
        "electrical_safety": "Inspect transformers and generator sets for thermal overheating. Keep fire suppression cylinders checked.",
        "worker_welfare": "Shift re-scheduling: Split shift (6 AM - 11 AM, 3 PM - 7 PM). Mandatory ORS (Oral Rehydration Salts) stations every 50 meters. Shaded rest pods.",
        "scaffolding_status": "Metal surfaces reach >58°C. Mandate thermal work gloves when handling steel rebars, shuttering plates, and scaffolding pipes."
    },
    "Fog / Low Visibility (< 150m Dense Haze)": {
        "status": "Orange",
        "severity": "VISIBILITY RESTRICTION",
        "crane_operations": "Halt crane swings without dedicated radio signalman (banksman) and visual beacon markers. Activate anti-collision beacons.",
        "concrete_protocol": "Standard curing. Concrete transport transit mixers must use hazard flashers and audible reverse alarms at all times.",
        "electrical_safety": "Ensure temporary site perimeter floodlighting is fully illuminated at 150+ lux.",
        "worker_welfare": "Mandate Class 3 fluorescent high-vis reflective vests for all personnel on access roads and active earthmoving zones.",
        "scaffolding_status": "Restricted vertical hoist operations until visibility clears beyond 300 meters."
    },
    "Severe Thunderstorm & Lightning": {
        "status": "Red",
        "severity": "EXTREME ATMOSPHERIC HAZARD",
        "crane_operations": "IMMEDIATE EVACUATION: Ground all crane operators immediately. Tower cranes act as primary lightning attractors.",
        "concrete_protocol": "Cease batching plant operations. Secure concrete boom pumps and fold placement booms.",
        "electrical_safety": "Disconnect all temporary mobile generators and sensitive surveying instrumentation.",
        "worker_welfare": "Clear all open decks, scaffolding, and steel rebar cages. Direct all labor force into certified lightning-safe structures.",
        "scaffolding_status": "Verify grounding/earthing continuity of all steel scaffolding towers."
    }
}
