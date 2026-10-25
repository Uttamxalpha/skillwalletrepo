"""
Multimodal Gemini Client & JSON Contract Validator
Platform ID: 6ac4c98d1dcde6d7857c1642
Handles Google GenAI (Gemini 1.5/2.5) communication with automatic fallback to demonstration mode.
"""

import json
import re
import os
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import datetime

# Pydantic Schemas for JSON Contracts (Epic 4)

class PPEItem(BaseModel):
    item: str
    detected_count: int
    compliance_status: str  # "Compliant", "Violation", "Partial", "Not Applicable"
    confidence: float
    notes: str

class SiteHazard(BaseModel):
    hazard_title: str
    severity: str  # "Low", "Medium", "High", "Critical"
    location_in_photo: str
    standard_violated: str
    immediate_corrective_remedy: str
    preventive_measure: str

class PPEAuditResponse(BaseModel):
    safety_score: int
    overall_status: str
    summary: str
    worker_count_detected: int
    fully_compliant_workers: int
    ppe_checklist: list[PPEItem]
    identified_hazards: list[SiteHazard]
    standards_cited: list[str]
    audit_timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class CrackDiagnosticResponse(BaseModel):
    defect_type: str  # "Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling / Corrosion"
    severity_score: float  # 0.0 - 10.0
    risk_rating: str  # "Low", "Medium", "High", "Critical"
    estimated_crack_width_mm: float
    is_structural_threat: bool
    is456_compliance_status: str
    surface_material: str
    identified_location: str
    root_causes: list[str]
    engineering_repairs: list[str]
    urgency_timeline: str
    estimated_repair_cost_range_inr: str
    detailed_technical_narrative: str
    diagnostic_timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ConstructionGeminiClient:
    """Manages Gemini Multimodal inference with full offline fallback capabilities."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self.client = None
        self.is_live = False
        self._init_client()

    def _init_client(self):
        """Initializes google.genai or flags demo fallback mode."""
        if not self.api_key:
            self.is_live = False
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.is_live = True
        except Exception:
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self.client = "legacy"
                self.is_live = True
            except Exception:
                self.is_live = False

    def clean_json_response(self, text: str) -> Dict[str, Any]:
        """Strips markdown fences and parses JSON robustly."""
        clean = text.strip()
        # Remove markdown code blocks if present
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        # Fix possible trailing commas before closing braces
        clean = re.sub(r",\s*([\]}])", r"\1", clean)

        return json.loads(clean)

    def analyze_ppe_compliance(self, image_bytes: bytes, filename: str = "site.jpg") -> Tuple[Dict[str, Any], bool]:
        """
        Multimodal audit of worker PPE under OSHA 1926 and IS 456/13415.
        Returns (result_dict, is_mock).
        """
        if not self.is_live or not self.client:
            return self.get_mock_ppe_audit(filename), True

        prompt = """
        You are a senior OSHA and IS 456 / IS 13415 certified construction safety inspector.
        Analyze this construction site photo thoroughly for Personal Protective Equipment (PPE) compliance and occupational hazards.

        Evaluate for:
        1. Hard hats / helmets (EN 397 / IS 2925)
        2. High-visibility reflective safety vests (IS 15809 / EN ISO 20471)
        3. Steel-toe safety footwear (IS 15298 / ASTM F2413)
        4. Fall protection harnesses and lifelines (IS 3521 / OSHA 1926 Subpart M) if working at heights
        5. Eye / face protection and heavy work gloves where active work occurs
        6. General site hazards (open floor edges, uncapped rebar dowels, tripping hazards, electrical cords in puddles)

        You MUST respond ONLY with valid JSON conforming strictly to this format:
        {
          "safety_score": 78,
          "overall_status": "Minor Violation",
          "summary": "Executive summary of site observations and compliance status",
          "worker_count_detected": 3,
          "fully_compliant_workers": 2,
          "ppe_checklist": [
            {
              "item": "Safety Hard Hats",
              "detected_count": 3,
              "compliance_status": "Compliant",
              "confidence": 0.96,
              "notes": "All visible personnel wearing certified hard hats with chinstraps."
            },
            {
              "item": "High-Visibility Vests",
              "detected_count": 2,
              "compliance_status": "Violation",
              "confidence": 0.92,
              "notes": "1 worker missing high-vis vest near vehicle transit zone."
            },
            {
              "item": "Steel-Toe Safety Boots",
              "detected_count": 3,
              "compliance_status": "Compliant",
              "confidence": 0.88,
              "notes": "Site-grade heavy work boots visible on ground-level crew."
            },
            {
              "item": "Fall Protection Harnesses",
              "detected_count": 0,
              "compliance_status": "Not Applicable",
              "confidence": 0.95,
              "notes": "All workers at ground grade; no elevated work detected."
            },
            {
              "item": "Eye / Hand Protective Gear",
              "detected_count": 1,
              "compliance_status": "Partial",
              "confidence": 0.85,
              "notes": "Rebar cutting crew member lacks safety goggles."
            }
          ],
          "identified_hazards": [
            {
              "hazard_title": "Uncapped Vertical Rebar Dowels",
              "severity": "High",
              "location_in_photo": "Lower left foreground near walkway",
              "standard_violated": "OSHA 1926.701(b) / IS 13415:1992",
              "immediate_corrective_remedy": "Fit bright mushroom impalement safety caps over exposed starter bars immediately.",
              "preventive_measure": "Mandate rebar caps prior to pouring slab edge footings."
            }
          ],
          "standards_cited": ["OSHA 1926 Subpart E", "IS 13415:1992", "IS 456:2000 Section 35"]
        }
        Do not wrap in any other explanation, only the JSON block.
        """

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_bytes))
                model = legacy_genai.GenerativeModel(self.model_name)
                response = model.generate_content([prompt, img])
                data = self.clean_json_response(response.text)
                return data, False
            else:
                from google.genai import types
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                    ]
                )
                data = self.clean_json_response(response.text)
                return data, False
        except Exception:
            return self.get_mock_ppe_audit(filename), True

    def analyze_crack_diagnostics(self, image_bytes: bytes, filename: str = "crack.jpg") -> Tuple[Dict[str, Any], bool]:
        """
        Multimodal classification of concrete/wall cracks with engineering repair plan.
        Returns (result_dict, is_mock).
        """
        if not self.is_live or not self.client:
            return self.get_mock_crack_diagnostics(filename), True

        prompt = """
        You are a principal forensic structural engineer specializing in reinforced concrete durability and forensic rehabilitation.
        Inspect this concrete/wall defect image thoroughly.

        Analyze and classify:
        1. Defect Type: Exactly one of ["Hairline Crack", "Settlement Crack", "Structural Shear Crack", "Thermal Expansion Crack", "Spalling & Rebar Corrosion"].
        2. Estimated crack width (in millimeters, e.g., 0.45 mm).
        3. Structural threat level and IS 456:2000 limit state compliance (IS 456 Clause 35.3.2 specifies max crack width 0.3mm for mild/moderate exposure, 0.2mm for severe, 0.1mm for extreme).
        4. Severity score on a 0.0 to 10.0 scale.
        5. Risk rating: ["Low", "Medium", "High", "Critical"].
        6. Root causes (differential foundation settlement, plastic shrinkage, excessive diagonal shear stress, carbonation/chloride attack).
        7. Recommended engineering repair methodology (low-viscosity epoxy resin injection under pressure, structural polyurethane re-grouting, carbon fiber reinforced polymer CFRP wrap, underpinning).
        8. Urgency timeline and estimated repair cost range in INR.

        You MUST respond ONLY with valid JSON conforming strictly to this format:
        {
          "defect_type": "Structural Shear Crack",
          "severity_score": 7.4,
          "risk_rating": "High",
          "estimated_crack_width_mm": 1.85,
          "is_structural_threat": true,
          "is456_compliance_status": "EXCEEDS IS 456:2000 LIMIT: Permissible threshold is 0.3mm; detected width 1.85mm compromises load-bearing capacity.",
          "surface_material": "M30 Grade Reinforced Concrete Column-Beam Junction",
          "identified_location": "Diagonal shear zone at beam support node",
          "root_causes": [
            "Excessive principal tensile stress exceeding concrete tensile capacity (fcr = 0.7*sqrt(fck))",
            "Inadequate stirrup spacing / shear link detailing at beam-column node",
            "Differential deflection under peak live load conditions"
          ],
          "engineering_repairs": [
            "Low-viscosity structural epoxy resin injection (ASTM C881 Grade 1) under 0.25 MPa pressure to restore monolithicity.",
            "Install dual-layer Carbon Fiber Reinforced Polymer (CFRP) bidirectional wrap across shear zone.",
            "Install mechanical tell-tale displacement monitoring gauge to verify crack stabilization over 21 days."
          ],
          "urgency_timeline": "High Urgency: Propping/shoring required within 24 hours; repair within 7 days.",
          "estimated_repair_cost_range_inr": "₹45,000 - ₹85,000 (including CFRP wrap & NDT sonic testing)",
          "detailed_technical_narrative": "Detailed technical forensic commentary on shear crack propagation, potential shear failure mechanisms, and load transfer restoration."
        }
        Do not wrap in any other explanation, only the JSON block.
        """

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_bytes))
                model = legacy_genai.GenerativeModel(self.model_name)
                response = model.generate_content([prompt, img])
                data = self.clean_json_response(response.text)
                return data, False
            else:
                from google.genai import types
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        prompt,
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                    ]
                )
                data = self.clean_json_response(response.text)
                return data, False
        except Exception:
            return self.get_mock_crack_diagnostics(filename), True

    def chat_query(self, query: str, conversation_history: list[dict], weather_context: Optional[dict] = None) -> Tuple[str, bool]:
        """
        Interactive multi-turn construction engineering assistant chatbot.
        Returns (reply_text, is_mock).
        """
        if not self.is_live or not self.client:
            return self.get_mock_chat_response(query, weather_context), True

        sys_prompt = """
        You are 'SiteAssist AI', the master site civil engineer, safety director, and quantity surveyor on a large-scale multimodal construction platform.
        You are an expert in OSHA 1926, Indian Standards (IS 456:2000, IS 13415, IS 1893, IS 2911), NBC 2016, and site economics (INR valuation, BoQ, scheduling).
        Provide concise, technically authoritative, actionable guidance with calculations where relevant.
        """

        context_str = ""
        if weather_context:
            context_str = f"\nCurrent Active Site Weather: {weather_context.get('condition')} | Safety Severity: {weather_context.get('severity')} | Crane Protocol: {weather_context.get('crane_operations')}\n"

        prompt = f"{sys_prompt}\n{context_str}\nUser Question: {query}"

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                model = legacy_genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                return response.text, False
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text, False
        except Exception:
            return self.get_mock_chat_response(query, weather_context), True

    # High-Fidelity Realistic Mock Data Generators for Standalone / Demo Mode

    def get_mock_ppe_audit(self, filename: str) -> Dict[str, Any]:
        """Realistic OSHA & IS 456/13415 audit report for demonstration mode."""
        return {
            "safety_score": 82,
            "overall_status": "Minor Violation",
            "summary": "Visual inspection of active construction quadrant indicates substantial PPE adherence across the primary work crew. 4 out of 5 detected personnel exhibit certified hard hats and heavy-duty footwear. Identified non-compliance includes 1 worker operating without high-visibility outerwear in a vehicular transit zone, and uncapped starter dowels posing puncture hazards.",
            "worker_count_detected": 5,
            "fully_compliant_workers": 3,
            "ppe_checklist": [
                {
                    "item": "Industrial Safety Helmets (IS 2925 / EN 397)",
                    "detected_count": 5,
                    "compliance_status": "Compliant",
                    "confidence": 0.98,
                    "notes": "All 5 active workers detected wearing Class E/G rated industrial hard hats with chin straps fastened."
                },
                {
                    "item": "High-Visibility Reflective Vests (IS 15809)",
                    "detected_count": 4,
                    "compliance_status": "Violation",
                    "confidence": 0.94,
                    "notes": "1 worker handling perimeter shuttering has removed high-vis vest in proximity to excavator swing path."
                },
                {
                    "item": "Steel-Toe Safety Footwear (IS 15298 / ASTM F2413)",
                    "detected_count": 5,
                    "compliance_status": "Compliant",
                    "confidence": 0.91,
                    "notes": "Puncture-resistant, steel-toed work boots observed across all ground personnel."
                },
                {
                    "item": "Fall Arrest Harness & Lanyard (IS 3521 / OSHA 1926.502)",
                    "detected_count": 2,
                    "compliance_status": "Compliant",
                    "confidence": 0.95,
                    "notes": "Elevated scaffolding workers anchored to independent vertical lifeline with double-locking snap hooks."
                },
                {
                    "item": "Heavy Mechanical Work Gloves & Eye Shields (IS 4770)",
                    "detected_count": 3,
                    "compliance_status": "Partial",
                    "confidence": 0.86,
                    "notes": "Rebar tying crew wearing cut-resistant gloves; helper grinding tie wires lacks impact safety goggles."
                }
            ],
            "identified_hazards": [
                {
                    "hazard_title": "Uncapped Vertical Rebar Dowels (Impalement Risk)",
                    "severity": "Critical",
                    "location_in_photo": "South-east column starter bar grid",
                    "standard_violated": "OSHA 1926.701(b) & IS 13415:1992 Cl. 4.2",
                    "immediate_corrective_remedy": "Immediately fit OSHA-approved steel-reinforced mushroom impalement caps over all exposed protruding dowels.",
                    "preventive_measure": "Incorporate rebar cap inspection into the daily morning Tool Box Talk (TBT) sign-off checklist."
                },
                {
                    "hazard_title": "Absence of High-Vis Vest in Mobile Equipment Zone",
                    "severity": "High",
                    "location_in_photo": "West haul road margin adjacent to batching transit route",
                    "standard_violated": "OSHA 1926.201(a) & NBC 2016 Part 7",
                    "immediate_corrective_remedy": "Issue fluorescent orange/lime Class 2 high-vis vest immediately prior to resuming haul road perimeter duty.",
                    "preventive_measure": "Site gatekeeper to enforce zero-entry policy without certified high-vis vest."
                },
                {
                    "hazard_title": "Trailing Temporary Electrical Power Cable",
                    "severity": "Medium",
                    "location_in_photo": "Ground level across central walkway near water drum",
                    "standard_violated": "OSHA 1926.405 & IS 732:2019",
                    "immediate_corrective_remedy": "Elevate temporary 230V rubber cabling on insulated S-hooks at minimum 2.4m clearance or protect with cable ramps.",
                    "preventive_measure": "Inspect all temporary distribution boards weekly with 30mA RCCB trip testing."
                }
            ],
            "standards_cited": [
                "OSHA 1926 Subpart E (Personal Protective Equipment)",
                "OSHA 1926.701(b) (Concrete and Masonry Construction Impalement Protection)",
                "IS 13415:1992 (Safety Code for Civil Engineering Works)",
                "IS 456:2000 (Plain and Reinforced Concrete - Health & Safety Compliance)",
                "NBC 2016 Part 7 (Construction Management, Practices and Safety)"
            ],
            "audit_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_mock_crack_diagnostics(self, filename: str) -> Dict[str, Any]:
        """Realistic structural crack forensic analysis for demonstration mode."""
        return {
            "defect_type": "Structural Shear Crack",
            "severity_score": 7.8,
            "risk_rating": "High",
            "estimated_crack_width_mm": 1.45,
            "is_structural_threat": True,
            "is456_compliance_status": "VIOLATION OF IS 456:2000 CLAUSE 35.3.2: Max permissible crack width under moderate exposure is 0.30 mm. Observed 1.45 mm exceeds serviceability limit by 383%, indicating active shear distress.",
            "surface_material": "M30 Grade Reinforced Concrete (RCC) Main Beam Flange",
            "identified_location": "Diagonal 45-degree angle propagating from support shear zone toward mid-span",
            "root_causes": [
                "Principal diagonal tensile stress exceeding concrete design tensile strength under superimposed gravity loads.",
                "Potential deficiency in secondary shear reinforcement (stirrup spacing > 0.75d limit specified in IS 456 Cl. 26.5.1.5).",
                "Thermal movement combined with partial torsional restraint at beam-column node."
            ],
            "engineering_repairs": [
                "Temporary Propping: Immediately erect heavy-duty adjustable steel shores beneath the damaged beam span to relieve 65% of live dead loads.",
                "Structural Epoxy Pressure Grouting: Inject ultra-low viscosity structural epoxy resin (conforming to ASTM C881 Type IV Grade 1) under 0.20 to 0.35 MPa to achieve full-depth bond restoration.",
                "CFRP Strengthening: Surface-mount dual-layer bidirectional Carbon Fiber Reinforced Polymer (CFRP) laminate wraps (300 gsm) at 45 degrees along the shear zone for tensile capacity enhancement.",
                "Verification NDT: Conduct Ultrasonic Pulse Velocity (UPV) testing per IS 516 Part 5 to confirm complete resin penetration and concrete homogeneity."
            ],
            "urgency_timeline": "URGENT ACTION (Within 48 Hours): Install temporary shoring props immediately; execute epoxy injection and CFRP remediation within 7 business days.",
            "estimated_repair_cost_range_inr": "₹55,000 - ₹95,000 (Includes NDT testing, surface preparation, epoxy injection, and dual-layer CFRP wrapping)",
            "detailed_technical_narrative": "Forensic visual and geometrical assessment demonstrates a textbook diagonal shear crack propagating at approximately 42 degrees to the horizontal axis of the RCC girder. The crack exhibits sharp, un-weathered margins with minor aggregate fracture, pointing toward recent peak load-induced distress rather than long-term shrinkage. Given that the crack penetrates beyond the 40mm nominal cover zone into the core concrete confinement zone, un-remediated moisture ingress will accelerate chloride-induced rebar depassivation, triggering expansive rust and catastrophic spalling.",
            "diagnostic_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_mock_chat_response(self, query: str, weather_context: Optional[dict] = None) -> str:
        """Intelligent context-aware engineering chatbot response in demo mode."""
        q = query.lower()
        if "crack" in q or "is 456" in q or "width" in q:
            return (
                "**IS 456:2000 Technical Guidance on Crack Width Limits:**\n\n"
                "According to **IS 456:2000 Clause 35.3.2 (Limit State of Serviceability - Cracking)**, crack width control is governed by exposure environment:\n\n"
                "- **Mild Exposure** (e.g. protected interior concrete): Maximum permissible surface crack width is **0.30 mm**.\n"
                "- **Moderate Exposure** (e.g. exterior sheltered concrete, buried concrete): Maximum permissible crack width is **0.20 mm**.\n"
                "- **Severe / Extreme Exposure** (e.g. coastal spray, aggressive chemical soil): Maximum permissible crack width is restricted to **0.10 mm**.\n\n"
                "When cracks exceed these limits:\n"
                "1. If width is <0.5mm (non-structural), seal with low-viscosity acrylic or polyurethane elastomeric sealants.\n"
                "2. If width is >0.75mm and structural, execute **low-viscosity epoxy pressure injection (ASTM C881)** and verify shear/flexural capacity using CFRP or steel plate bonding."
            )
        elif "wind" in q or "crane" in q or "gust" in q:
            return (
                "**Tower Crane Wind Speed Operational Protocol (IS 4573 / OSHA 1926.1431):**\n\n"
                "1. **Operational Wind Threshold (38 km/h / 20 knots):** At 38 km/h, tower crane operations must transition to high alert. Reduce hoisting of large surface-area forms (e.g., gang forms, curtain wall glass).\n"
                "2. **Mandatory Operational Cut-off (45 - 50 km/h / 24-27 knots):** All lifting operations must CEASE immediately. Lower any suspended loads to the ground.\n"
                "3. **Storm / Free-Slew Protocol (> 50 km/h):** Release crane slew brakes to put the crane in 'Weather-Vane' (free-slewing) mode. This allows the crane jib to orient along the wind direction, minimizing aerodynamic overturning moments on the tower mast."
            )
        elif "curing" in q or "concrete" in q or "summer" in q or "heat" in q:
            return (
                "**Hot Weather Concreting & Curing Protocol (IS 7861 Part 1 & IS 456 Cl. 13.5):**\n\n"
                "When ambient temperatures exceed 40°C on site:\n"
                "1. **Concrete Placement Temperature:** Concrete temperature at placement should not exceed 30°C to 32°C. Use chilled mixing water or ice flakes at batching.\n"
                "2. **Admixtures:** Incorporate ASTM C494 Type D/G set-retarding water reducers to offset rapid cement hydration.\n"
                "3. **Moisture Protection:** Immediately after surface screeding, apply aliphatic evaporation retarders.\n"
                "4. **Curing Duration:** Continuous moist curing with wet burlap/hessian cloth for a minimum of **14 consecutive days** for Portland Pozzolana Cement (PPC) and mineral blended concretes."
            )
        elif "scaffolding" in q or "load" in q:
            return (
                "**Scaffolding Structural Capacity & Inspection Guidelines (IS 3696 & OSHA 1926 Subpart L):**\n\n"
                "- **Standard Heavy Duty Civil Scaffolding:** Designed for 375 kg/m² (75 lb/ft²) uniformly distributed load (UDL).\n"
                "- **Working Deck Planking:** Full wooden/steel planks with minimum 25mm overhang, secured against wind uplift, with 150mm toe boards.\n"
                "- **Safety Factor:** Standard scaffolding systems require a structural safety factor of 4:1 against collapse.\n"
                "- **Tagging Requirement:** Daily inspection before shift start with visible color tagging (Green = Approved, Red = Prohibited for use)."
            )
        else:
            weather_note = ""
            if weather_context:
                weather_note = f"\n*Current Site Advisory: {weather_context.get('condition')} - {weather_context.get('severity')} active.*"
            return (
                f"**Site Engineering Decision Support Response:**\n\n"
                f"Regarding your inquiry on *'{query}'*:\n"
                f"- **Regulatory Standard:** Review specifications under IS 456:2000, IS 13415:1992, and OSHA 1926.\n"
                f"- **Action Step:** Verify site field measurements against architectural shop drawings and structural consult sign-offs.\n"
                f"- **Quality Control:** Check calibration of on-site testing equipment (slump cones, rebound hammers, batch weighers).\n"
                f"{weather_note}\n\n"
                f"Feel free to ask for specific BoQ calculations, crack width repair procedures, or concrete grade mix designs!"
            )
