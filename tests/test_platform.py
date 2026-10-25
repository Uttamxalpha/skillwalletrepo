"""
Automated Test Suite for Multimodal Construction Intelligence Platform
Platform ID: 6ac4c98d1dcde6d7857c1642
Tests data contracts, financial calculators, fallback reasoning, and schema adherence.
"""

import unittest
import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from modules.gemini_client import (
    ConstructionGeminiClient,
    PPEAuditResponse,
    CrackDiagnosticResponse
)
from modules.valuation_planning import calculate_project_financials, format_inr
from modules.pollinations_render import generate_architectural_prompt, get_pollinations_image_url
from modules.weather_advisory import get_weather_protocol

class TestConstructionPlatform(unittest.TestCase):

    def test_platform_metadata(self):
        """Verify Capstone Platform ID and metadata."""
        self.assertEqual(config.PLATFORM_ID, "6ac4c98d1dcde6d7857c1642")
        self.assertIn("Multimodal Construction Intelligence", config.PLATFORM_TITLE)
        self.assertGreaterEqual(len(config.KANBAN_EPICS), 6)

    def test_inr_formatting(self):
        """Verify Indian currency formatting for Crores and Lakhs."""
        self.assertEqual(format_inr(150_000_000), "₹15.00 Cr")
        self.assertEqual(format_inr(25_000_000), "₹2.50 Cr")
        self.assertEqual(format_inr(750_000), "₹7.50 L")
        self.assertEqual(format_inr(45_000), "₹45,000")

    def test_financial_valuation_calculator(self):
        """Verify real estate valuation and BoQ estimation algorithms."""
        result = calculate_project_financials(
            structure_type="Residential High-Rise (RCC Framed G+20)",
            built_up_sqft=100000,
            location_tier_name="Tier 1 (Metro Hubs: Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai)",
            completion_pct=50
        )

        self.assertIn("total_capex_budget", result)
        self.assertIn("capex_incurred", result)
        self.assertIn("current_asset_valuation", result)
        self.assertIn("materials", result)

        # 100,000 sq ft at 4.2 MT per 1000 sq ft = 420 MT
        self.assertEqual(result["materials"]["steel_total_mt"], 420.0)
        self.assertEqual(result["materials"]["steel_consumed_mt"], 210.0)

        # Cement: 100,000 sq ft at 430 bags per 1000 sq ft = 43,000 bags
        self.assertEqual(result["materials"]["cement_total_bags"], 43000)
        self.assertEqual(result["materials"]["cement_consumed_bags"], 21500)

        # Financial logic check: Incurred + Remaining = Total CapEx
        self.assertAlmostEqual(
            result["capex_incurred"] + result["capex_remaining"],
            result["total_capex_budget"],
            places=2
        )

    def test_ppe_audit_schema_contract(self):
        """Verify PPE Audit JSON contract conforms to Pydantic schema."""
        client = ConstructionGeminiClient(api_key="")  # Demo mode
        mock_data = client.get_mock_ppe_audit("sample.jpg")

        # Validate with Pydantic
        validated = PPEAuditResponse(**mock_data)
        self.assertGreaterEqual(validated.safety_score, 0)
        self.assertLessEqual(validated.safety_score, 100)
        self.assertGreater(len(validated.ppe_checklist), 0)
        self.assertGreater(len(validated.identified_hazards), 0)
        self.assertIn("OSHA 1926", str(validated.standards_cited))

    def test_crack_diagnostic_schema_contract(self):
        """Verify Crack Diagnostic JSON contract conforms to Pydantic schema."""
        client = ConstructionGeminiClient(api_key="")  # Demo mode
        mock_data = client.get_mock_crack_diagnostics("sample_crack.jpg")

        validated = CrackDiagnosticResponse(**mock_data)
        self.assertIn(validated.defect_type, [
            "Hairline Crack", "Settlement Crack", "Structural Shear Crack",
            "Thermal Expansion Crack", "Spalling & Rebar Corrosion"
        ])
        self.assertGreater(validated.estimated_crack_width_mm, 0.0)
        self.assertGreater(len(validated.engineering_repairs), 0)
        self.assertIn("IS 456", validated.is456_compliance_status)

    def test_weather_protocol_matrix(self):
        """Verify microclimate protocols for extreme conditions."""
        wind_protocol = get_weather_protocol("High Wind Advisory (> 45 km/h / Gale Gusts)")
        self.assertEqual(wind_protocol["status"], "Red")
        self.assertIn("free-slew", wind_protocol["crane_operations"].lower())

        heat_protocol = get_weather_protocol("Extreme Heat Advisory (> 40°C / Heat Index > 46°C)")
        self.assertIn("IS 7861", heat_protocol["concrete_protocol"])

    def test_pollinations_prompt_and_url(self):
        """Verify Pollinations AI URL generation."""
        prompt = generate_architectural_prompt(
            structure_type="Commercial Grade-A Office Complex",
            tier_name="Tier 1",
            style="Parametric Smart Commercial Complex with Kinetic Louvers",
            lighting="Golden hour sunset with warm architectural glow and dusk street reflections"
        )
        self.assertIn("Commercial Grade-A Office Complex", prompt)
        url = get_pollinations_image_url(prompt, seed=12345)
        self.assertTrue(url.startswith("https://image.pollinations.ai/prompt/"))
        self.assertIn("seed=12345", url)

    def test_sample_images_exist(self):
        """Verify bundled sample test images exist and are non-empty."""
        ppe_img = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_ppe_site.jpg")
        crack_img = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_crack_defect.jpg")
        self.assertTrue(os.path.exists(ppe_img))
        self.assertTrue(os.path.exists(crack_img))
        self.assertGreater(os.path.getsize(ppe_img), 1000)
        self.assertGreater(os.path.getsize(crack_img), 1000)


if __name__ == "__main__":
    unittest.main()
