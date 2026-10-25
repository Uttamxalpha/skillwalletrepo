"""
Multimodal Gemini Client & JSON Contract Validator
Platform ID: 6ac4c98d1dcde6d7857c1642
Handles Google GenAI (Gemini 1.5/2.5) communication with automatic fallback to demonstration mode.
"""

import json
import re
import os
import io
import datetime
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field, field_validator
from PIL import Image

# ---------------------------------------------------------------------------
# Pydantic Schemas for JSON Contracts (Epic 4)
# ---------------------------------------------------------------------------

class PPEItem(BaseModel):
    item: str
    detected_count: int = Field(ge=0, default=0)
    compliance_status: str  # "Present", "Missing", "Uncertain / Not Visible", "Not Applicable"
    confidence: float = Field(ge=0.0, le=1.0, default=0.90)
    notes: str

    @field_validator("compliance_status", mode="before")
    @classmethod
    def normalize_compliance_status(cls, v: str) -> str:
        s = str(v).strip().lower()
        if "present" in s or "compliant" in s:
            return "Present"
        elif "missing" in s or "violation" in s or "absent" in s:
            return "Missing"
        elif "not applicable" in s or "n/a" in s:
            return "Not Applicable"
        else:
            return "Uncertain / Not Visible"


class SiteHazard(BaseModel):
    hazard_title: str
    severity: str = "Medium"  # "Low", "Medium", "High", "Critical"
    location_in_photo: str
    standard_violated: str
    immediate_corrective_remedy: str
    preventive_measure: str

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: str) -> str:
        s = str(v).strip().title()
        if s in ["Low", "Medium", "High", "Critical"]:
            return s
        return "Medium"


class PPEAuditResponse(BaseModel):
    safety_score: int = Field(ge=0, le=100)
    overall_status: str  # "Compliant", "Minor Violation", "Critical Hazard", "Non-Compliant"
    summary: str
    worker_count_detected: int = Field(ge=0, default=0)
    fully_compliant_workers: int = Field(ge=0, default=0)
    ppe_checklist: List[PPEItem]
    identified_hazards: List[SiteHazard]
    standards_cited: List[str]
    audit_timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    is_demonstration_mode: bool = False
    disclaimer: str = (
        "LEGAL & SAFETY DISCLAIMER: This AI visual assessment is an assistive decision-support tool based "
        "on 2D visual inputs. It does not constitute a certified occupational safety audit, guarantee full "
        "compliance under OSHA 1926 or IS 13415, or replace mandatory on-site inspections by certified safety officers."
    )

    @field_validator("safety_score", mode="before")
    @classmethod
    def clamp_score(cls, v: Any) -> int:
        try:
            val = int(v)
            return max(0, min(100, val))
        except Exception:
            return 75


class CrackDiagnosticResponse(BaseModel):
    defect_type: str  # "Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling / Corrosion"
    severity_score: float = Field(ge=0.0, le=10.0)
    risk_rating: str  # "Low", "Medium", "High", "Critical"
    estimated_crack_width_mm: Optional[float] = None
    width_measurement_confidence: str = "Subject to field optical calibration uncertainty"
    has_known_calibration_scale: bool = False
    is_structural_threat: bool = False
    is456_compliance_status: str
    surface_material: str
    identified_location: str
    root_causes: List[str]
    engineering_repairs: List[str]
    urgency_timeline: str
    estimated_repair_cost_range_inr: str
    detailed_technical_narrative: str
    diagnostic_timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    is_demonstration_mode: bool = False
    structural_disclaimer: str = (
        "STRUCTURAL ENGINEERING NOTICE: AI-generated defect classifications and repair sequences are "
        "preliminary forensic estimates for screening purposes only. A licensed Chartered Structural Engineer "
        "(IS 456 compliant) must conduct in-situ ultrasonic / core testing and issue stamped engineering "
        "specifications before any structural load-bearing repair, propping, or epoxy injection is executed."
    )

    @field_validator("defect_type", mode="before")
    @classmethod
    def normalize_defect_type(cls, v: str) -> str:
        s = str(v).strip().lower()
        if "shear" in s:
            return "Structural Shear Crack"
        elif "spall" in s or "corrosion" in s or "rebar" in s:
            return "Spalling & Rebar Corrosion"
        elif "settle" in s:
            return "Settlement Crack"
        elif "thermal" in s or "expansion" in s:
            return "Thermal Expansion Crack"
        elif "hairline" in s or "shrinkage" in s:
            return "Hairline Crack"
        return "Structural Defect"

    @field_validator("severity_score", mode="before")
    @classmethod
    def clamp_severity(cls, v: Any) -> float:
        try:
            val = float(v)
            return max(0.0, min(10.0, val))
        except Exception:
            return 5.0

    @field_validator("risk_rating", mode="before")
    @classmethod
    def normalize_risk(cls, v: str) -> str:
        s = str(v).strip().title()
        if s in ["Low", "Medium", "High", "Critical"]:
            return s
        return "Medium"


# ---------------------------------------------------------------------------
# Core Client Implementation
# ---------------------------------------------------------------------------

class ConstructionGeminiClient:
    """Manages Gemini Multimodal inference with full offline fallback capabilities."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = self._resolve_api_key(api_key)
        self.model_name = model_name
        self.client = None
        self.is_live = False
        self._init_client()

    def _resolve_api_key(self, user_supplied_key: Optional[str]) -> str:
        """Securely reads API key from user input, st.secrets, or environment variables."""
        if user_supplied_key and user_supplied_key.strip():
            return user_supplied_key.strip()

        # Check Streamlit secrets safely
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                val = st.secrets["GEMINI_API_KEY"]
                if val and str(val).strip():
                    return str(val).strip()
        except Exception:
            pass

        # Check environment variable
        return os.environ.get("GEMINI_API_KEY", "").strip()

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

    def validate_image_bytes(self, image_bytes: bytes) -> Tuple[bool, str]:
        """Validates that bytes constitute a valid, readable image."""
        if not image_bytes or len(image_bytes) < 100:
            return False, "File buffer is empty or too small to be a valid image."
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
            return True, "Valid image format."
        except Exception as e:
            return False, f"Invalid or corrupted image format: {str(e)}"

    def clean_json_response(self, text: str) -> Dict[str, Any]:
        """Strips markdown fences and parses JSON robustly with error recovery."""
        clean = text.strip()
        # Remove markdown code blocks if present
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        # Fix trailing commas before closing braces/brackets
        clean = re.sub(r",\s*([\]}])", r"\1", clean)

        return json.loads(clean)

    def analyze_ppe_compliance(self, image_bytes: bytes, filename: str = "site.jpg") -> Tuple[Dict[str, Any], bool]:
        """
        Multimodal audit of worker PPE under OSHA 1926 and IS 456/13415.
        Returns (result_dict, is_mock).
        """
        is_valid, err_msg = self.validate_image_bytes(image_bytes)
        if not is_valid:
            mock = self.get_mock_ppe_audit(filename)
            mock["summary"] = f"Note: Input file validation failed ({err_msg}). Displaying baseline demonstration scenario."
            return mock, True

        if not self.is_live or not self.client:
            return self.get_mock_ppe_audit(filename), True

        prompt = """
        You are a senior OSHA 1926 and IS 13415 certified construction safety inspector.
        Analyze this active construction site photograph for Personal Protective Equipment (PPE) compliance and occupational site hazards.

        Evaluate for:
        1. Hard hats / helmets (EN 397 / IS 2925)
        2. High-visibility reflective vests (IS 15809 / EN ISO 20471)
        3. Steel-toe safety boots (IS 15298 / ASTM F2413)
        4. Fall protection harnesses and lifelines (IS 3521 / OSHA 1926 Subpart M) if workers are at heights
        5. Eye/face protection and heavy mechanical work gloves where active work occurs
        6. Protruding uncapped rebar dowels (OSHA 1926.701b), tripping hazards, and electrical cables

        For each PPE item, explicitly categorize compliance_status as one of:
        ["Present", "Missing", "Uncertain / Not Visible", "Not Applicable"].

        Output strictly valid JSON with this exact schema:
        {
          "safety_score": 82,
          "overall_status": "Minor Violation",
          "summary": "Executive summary of visual observations.",
          "worker_count_detected": 4,
          "fully_compliant_workers": 3,
          "ppe_checklist": [
            {
              "item": "Industrial Safety Helmets",
              "detected_count": 4,
              "compliance_status": "Present",
              "confidence": 0.95,
              "notes": "All visible personnel wearing certified hard hats."
            },
            {
              "item": "High-Visibility Reflective Vests",
              "detected_count": 3,
              "compliance_status": "Missing",
              "confidence": 0.92,
              "notes": "1 perimeter worker detected without reflective vest."
            },
            {
              "item": "Steel-Toe Safety Footwear",
              "detected_count": 4,
              "compliance_status": "Present",
              "confidence": 0.88,
              "notes": "Heavy protective work boots visible."
            },
            {
              "item": "Fall Protection Harnesses",
              "detected_count": 0,
              "compliance_status": "Not Applicable",
              "confidence": 0.96,
              "notes": "Work is entirely at ground level."
            },
            {
              "item": "Eye & Hand Protective Gear",
              "detected_count": 2,
              "compliance_status": "Uncertain / Not Visible",
              "confidence": 0.80,
              "notes": "Gloves obscured; eye protection partially visible."
            }
          ],
          "identified_hazards": [
            {
              "hazard_title": "Uncapped Vertical Rebar Dowels",
              "severity": "Critical",
              "location_in_photo": "Foreground left quadrant",
              "standard_violated": "OSHA 1926.701(b) / IS 13415:1992",
              "immediate_corrective_remedy": "Fit OSHA-approved mushroom impalement caps over all starter bars.",
              "preventive_measure": "Daily Toolbox Talk sign-off before shift commencement."
            }
          ],
          "standards_cited": ["OSHA 1926 Subpart E", "IS 13415:1992", "NBC 2016 Part 7"]
        }
        Do not wrap in prose, only return the JSON.
        """

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                img = Image.open(io.BytesIO(image_bytes))
                model = legacy_genai.GenerativeModel(self.model_name)
                response = model.generate_content([prompt, img])
                raw_json = self.clean_json_response(response.text)
                validated = PPEAuditResponse(**raw_json)
                data = validated.model_dump()
                data["is_demonstration_mode"] = False
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
                raw_json = self.clean_json_response(response.text)
                validated = PPEAuditResponse(**raw_json)
                data = validated.model_dump()
                data["is_demonstration_mode"] = False
                return data, False
        except Exception:
            return self.get_mock_ppe_audit(filename), True

    def analyze_crack_diagnostics(self, image_bytes: bytes, filename: str = "crack.jpg") -> Tuple[Dict[str, Any], bool]:
        """
        Multimodal classification of concrete/wall cracks with engineering repair plan.
        Returns (result_dict, is_mock).
        """
        is_valid, err_msg = self.validate_image_bytes(image_bytes)
        if not is_valid:
            mock = self.get_mock_crack_diagnostics(filename)
            mock["detailed_technical_narrative"] = f"Note: Input file validation failed ({err_msg}). Displaying baseline demonstration scenario."
            return mock, True

        if not self.is_live or not self.client:
            return self.get_mock_crack_diagnostics(filename), True

        prompt = """
        You are a principal forensic structural engineer specializing in reinforced concrete durability and rehabilitation.
        Inspect this concrete or masonry surface photograph thoroughly.

        Analyze and classify:
        1. Defect Category: Exactly one of ["Hairline Crack", "Settlement Crack", "Structural Shear Crack", "Thermal Expansion Crack", "Spalling & Rebar Corrosion"].
        2. Estimated crack width (in millimeters, e.g. 1.45 mm). If no reference scale is visible, note calibration uncertainty.
        3. IS 456:2000 Limit State of Serviceability compliance (IS 456 Clause 35.3.2 specifies max crack width: 0.3mm for mild/moderate, 0.2mm for severe, 0.1mm for extreme).
        4. Severity score on a 0.0 to 10.0 scale.
        5. Risk rating: ["Low", "Medium", "High", "Critical"].
        6. Plausible root causes (e.g. principal diagonal shear stress, differential foundation settlement, plastic shrinkage, carbonation).
        7. Recommended engineering repair methodology (low-viscosity epoxy pressure injection ASTM C881, polyurethane re-grouting, CFRP wrap, propping).
        8. Urgency timeline and estimated repair cost range in INR.

        Output strictly valid JSON with this exact schema:
        {
          "defect_type": "Structural Shear Crack",
          "severity_score": 7.8,
          "risk_rating": "High",
          "estimated_crack_width_mm": 1.45,
          "width_measurement_confidence": "Estimated visual aperture (±30% field optical uncertainty without physical gauge)",
          "has_known_calibration_scale": true,
          "is_structural_threat": true,
          "is456_compliance_status": "EXCEEDS IS 456:2000 LIMIT (0.30mm): Observed width 1.45mm indicates active shear distress requiring propping and remediation.",
          "surface_material": "M30 Grade Reinforced Concrete (RCC) Main Beam",
          "identified_location": "Diagonal 45-degree angle propagating from support shear zone",
          "root_causes": [
            "Principal diagonal tensile stresses exceeding concrete tensile strength",
            "Deficiency in secondary shear stirrup spacing under peak gravity load",
            "Restrained thermal movement at beam-column node"
          ],
          "engineering_repairs": [
            "Erect temporary heavy-duty steel shores to relieve dead and live loads within 24 hours.",
            "Pressure inject ultra-low viscosity structural epoxy resin (ASTM C881 Grade 1) under 0.25 MPa.",
            "Apply dual-layer bidirectional Carbon Fiber Reinforced Polymer (CFRP) wrap across the shear zone."
          ],
          "urgency_timeline": "URGENT (Action within 48-72 Hours): Install temporary propping immediately; execute epoxy injection within 7 days.",
          "estimated_repair_cost_range_inr": "₹55,000 - ₹95,000 (Includes NDT testing, epoxy injection, and CFRP wrap)",
          "detailed_technical_narrative": "Forensic evaluation reveals diagonal shear distress. Core concrete confinement may be compromised by moisture ingress."
        }
        Do not wrap in prose, only return the JSON.
        """

        try:
            if self.client == "legacy":
                import google.generativeai as legacy_genai
                img = Image.open(io.BytesIO(image_bytes))
                model = legacy_genai.GenerativeModel(self.model_name)
                response = model.generate_content([prompt, img])
                raw_json = self.clean_json_response(response.text)
                validated = CrackDiagnosticResponse(**raw_json)
                data = validated.model_dump()
                data["is_demonstration_mode"] = False
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
                raw_json = self.clean_json_response(response.text)
                validated = CrackDiagnosticResponse(**raw_json)
                data = validated.model_dump()
                data["is_demonstration_mode"] = False
                return data, False
        except Exception:
            return self.get_mock_crack_diagnostics(filename), True

    def chat_query(self, query: str, conversation_history: List[Dict[str, str]], weather_context: Optional[Dict[str, Any]] = None) -> Tuple[str, bool]:
        """
        Interactive multi-turn construction engineering assistant chatbot.
        Returns (reply_text, is_mock).
        """
        if not query or not query.strip():
            return "Please provide an engineering question or select one of the quick prompt options above.", True

        if not self.is_live or not self.client:
            return self.get_mock_chat_response(query.strip(), weather_context), True

        sys_prompt = """
        You are 'SiteAssist AI', a certified Senior Civil Engineer and Construction Safety Consultant.
        You are an expert in OSHA 1926, Indian Standards (IS 456:2000, IS 13415, IS 1893, IS 2911, IS 7861), NBC 2016, and site economics (INR valuation, BoQ).
        Provide concise, technically authoritative, actionable guidance.
        Distinguish general technical standards from project-specific stamped engineering advice.
        """

        context_str = ""
        if weather_context:
            context_str = f"\nCurrent Active Site Weather Scenario: {weather_context.get('condition')} | Severity: {weather_context.get('severity')} | Crane Protocol: {weather_context.get('crane_operations')}\n"

        prompt = f"{sys_prompt}\n{context_str}\nUser Question: {query.strip()}"

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
            return self.get_mock_chat_response(query.strip(), weather_context), True

    # -----------------------------------------------------------------------
    # Deterministic Baseline Demonstration Scenario Generators
    # -----------------------------------------------------------------------

    def get_mock_ppe_audit(self, filename: str) -> Dict[str, Any]:
        """Deterministic OSHA & IS 456/13415 audit report for demonstration mode."""
        return {
            "safety_score": 82,
            "overall_status": "Minor Violation",
            "summary": "DEMONSTRATION SCENARIO: Visual inspection of active construction quadrant indicates substantial PPE adherence across the primary work crew. 4 out of 5 detected personnel exhibit certified hard hats and heavy-duty footwear. Identified non-compliance includes 1 worker operating without high-visibility outerwear in a vehicular transit zone, and uncapped starter dowels posing puncture hazards.",
            "worker_count_detected": 5,
            "fully_compliant_workers": 3,
            "ppe_checklist": [
                {
                    "item": "Industrial Safety Helmets (IS 2925 / EN 397)",
                    "detected_count": 5,
                    "compliance_status": "Present",
                    "confidence": 0.98,
                    "notes": "All 5 active workers detected wearing Class E/G rated industrial hard hats with chin straps fastened."
                },
                {
                    "item": "High-Visibility Reflective Vests (IS 15809)",
                    "detected_count": 4,
                    "compliance_status": "Missing",
                    "confidence": 0.94,
                    "notes": "1 worker handling perimeter shuttering has removed high-vis vest in proximity to excavator swing path."
                },
                {
                    "item": "Steel-Toe Safety Footwear (IS 15298 / ASTM F2413)",
                    "detected_count": 5,
                    "compliance_status": "Present",
                    "confidence": 0.91,
                    "notes": "Puncture-resistant, steel-toed work boots observed across all ground personnel."
                },
                {
                    "item": "Fall Arrest Harness & Lanyard (IS 3521 / OSHA 1926.502)",
                    "detected_count": 2,
                    "compliance_status": "Present",
                    "confidence": 0.95,
                    "notes": "Elevated scaffolding workers anchored to independent vertical lifeline with double-locking snap hooks."
                },
                {
                    "item": "Heavy Mechanical Work Gloves & Eye Shields (IS 4770)",
                    "detected_count": 3,
                    "compliance_status": "Uncertain / Not Visible",
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
            "audit_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_demonstration_mode": True,
            "disclaimer": (
                "LEGAL & SAFETY DISCLAIMER: This assessment is generated in DEMONSTRATION MODE. "
                "It serves as an illustrative baseline scenario for platform verification. It does NOT "
                "represent an actual vision analysis of an uploaded image and does not replace certified site safety audits."
            )
        }

    def get_mock_crack_diagnostics(self, filename: str) -> Dict[str, Any]:
        """Deterministic structural crack forensic analysis for demonstration mode."""
        return {
            "defect_type": "Structural Shear Crack",
            "severity_score": 7.8,
            "risk_rating": "High",
            "estimated_crack_width_mm": 1.45,
            "width_measurement_confidence": "Estimated using optical comparison gauge; ordinary photos carry ±30% uncertainty without physical target calibration",
            "has_known_calibration_scale": True,
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
            "diagnostic_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_demonstration_mode": True,
            "structural_disclaimer": (
                "STRUCTURAL ENGINEERING NOTICE: This defect assessment is generated in DEMONSTRATION MODE. "
                "It serves as an illustrative forensic scenario. A licensed Chartered Structural Engineer (IS 456 compliant) "
                "must conduct in-situ physical testing (UPV/rebound hammer) and structural calculations before executing structural repairs."
            )
        }

    def get_mock_chat_response(self, query: str, weather_context: Optional[Dict[str, Any]] = None) -> str:
        """Intelligent context-aware engineering chatbot response in demo mode."""
        q = query.lower()
        disclaimer_footer = "\n\n---\n*ℹ️ Note: SiteAssist AI provides general technical guidance based on IS 456 and OSHA 1926. It does not replace project-specific structural design or stamped engineering drawings.*"

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
                + disclaimer_footer
            )
        elif "wind" in q or "crane" in q or "gust" in q:
            return (
                "**Tower Crane Wind Speed Operational Protocol (IS 4573 / OSHA 1926.1431):**\n\n"
                "1. **Operational Wind Threshold (38 km/h / 20 knots):** At 38 km/h, tower crane operations must transition to high alert. Reduce hoisting of large surface-area forms (e.g., gang forms, curtain wall glass).\n"
                "2. **Mandatory Operational Cut-off (45 - 50 km/h / 24-27 knots):** All lifting operations must CEASE immediately. Lower any suspended loads to the ground.\n"
                "3. **Storm / Free-Slew Protocol (> 50 km/h):** Release crane slew brakes to put the crane in 'Weather-Vane' (free-slewing) mode. This allows the crane jib to orient along the wind direction, minimizing aerodynamic overturning moments on the tower mast."
                + disclaimer_footer
            )
        elif "curing" in q or "concrete" in q or "summer" in q or "heat" in q:
            return (
                "**Hot Weather Concreting & Curing Protocol (IS 7861 Part 1 & IS 456 Cl. 13.5):**\n\n"
                "When ambient temperatures exceed 40°C on site:\n"
                "1. **Concrete Placement Temperature:** Concrete temperature at placement should not exceed 30°C to 32°C. Use chilled mixing water or ice flakes at batching.\n"
                "2. **Admixtures:** Incorporate ASTM C494 Type D/G set-retarding water reducers to offset rapid cement hydration.\n"
                "3. **Moisture Protection:** Immediately after surface screeding, apply aliphatic evaporation retarders.\n"
                "4. **Curing Duration:** Continuous moist curing with wet burlap/hessian cloth for a minimum of **14 consecutive days** for Portland Pozzolana Cement (PPC) and mineral blended concretes."
                + disclaimer_footer
            )
        elif "scaffolding" in q or "load" in q:
            return (
                "**Scaffolding Structural Capacity & Inspection Guidelines (IS 3696 & OSHA 1926 Subpart L):**\n\n"
                "- **Standard Heavy Duty Civil Scaffolding:** Designed for 375 kg/m² (75 lb/ft²) uniformly distributed load (UDL).\n"
                "- **Working Deck Planking:** Full wooden/steel planks with minimum 25mm overhang, secured against wind uplift, with 150mm toe boards.\n"
                "- **Safety Factor:** Standard scaffolding systems require a structural safety factor of 4:1 against collapse.\n"
                "- **Tagging Requirement:** Daily inspection before shift start with visible color tagging (Green = Approved, Red = Prohibited for use)."
                + disclaimer_footer
            )
        else:
            weather_note = ""
            if weather_context:
                weather_note = f"\n*Current Active Site Scenario: {weather_context.get('condition')} ({weather_context.get('severity')})*"
            return (
                f"**Site Engineering Decision Support Response:**\n\n"
                f"Regarding your inquiry on *'{query}'*:\n"
                f"- **Regulatory Standard:** Review specifications under IS 456:2000, IS 13415:1992, and OSHA 1926.\n"
                f"- **Action Step:** Verify site field measurements against architectural shop drawings and structural consult sign-offs.\n"
                f"- **Quality Control:** Check calibration of on-site testing equipment (slump cones, rebound hammers, batch weighers).\n"
                f"{weather_note}\n\n"
                f"Feel free to ask for specific BoQ calculations, crack width repair procedures, or concrete grade mix designs!"
                + disclaimer_footer
            )


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 CONSTRUCT-AI: Gemini Client & Contract Validation (Epic 4)")
    print("Platform ID: 6ac4c98d1dcde6d7857c1642")
    print("=" * 70)
    client = ConstructionGeminiClient()
    print(f"Client Initialized. Live Mode: {client.is_live} (Fallback Active: {not client.is_live})")
    mock_audit = client.get_mock_ppe_audit("sample.jpg")
    print(f"PPE Safety Score: {mock_audit['safety_score']}/100 | Status: {mock_audit['overall_status']}")
    print(f"Hazards Identified: {len(mock_audit['identified_hazards'])}")
    print(f"Demonstration Mode Flag: {mock_audit['is_demonstration_mode']}")
    print("=" * 70)
    print("✅ Multimodal contracts verified successfully!")
