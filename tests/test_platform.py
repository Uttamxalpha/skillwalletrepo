"""
Automated Test Suite for Multimodal Construction Intelligence Platform
Platform ID: 6ac4c98d1dcde6d7857c1642
Tests data contracts, financial calculators, fallback reasoning, schema adherence, and edge cases.
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
    CrackDiagnosticResponse,
    PPEItem,
    SiteHazard
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

    def test_financial_valuation_calculator_normal(self):
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

        # Financial balance check: Incurred + Remaining = Total CapEx
        self.assertAlmostEqual(
            result["capex_incurred"] + result["capex_remaining"],
            result["total_capex_budget"],
            places=2
        )

    def test_financial_valuation_edge_cases(self):
        """Verify handling of zero, negative, and excessively large inputs."""
        # Zero sqft floor check
        res_zero = calculate_project_financials(
            structure_type="Commercial Grade-A Office Complex",
            built_up_sqft=0,
            location_tier_name="Tier 2 (Growth Cities: Pune, Ahmedabad, Kolkata, Jaipur, Kochi, Lucknow)",
            completion_pct=0
        )
        self.assertGreater(res_zero["built_up_sqft"], 0)
        self.assertEqual(res_zero["completion_pct"], 0.0)

        # Negative completion percentage clamp check
        res_neg = calculate_project_financials(
            structure_type="Industrial Logistics Warehouse (PEB + Heavy Slab)",
            built_up_sqft=-5000,
            location_tier_name="Tier 3 (Emerging Centers: Indore, Coimbatore, Nagpur, Bhubaneswar, Surat)",
            completion_pct=-15
        )
        self.assertEqual(res_neg["completion_pct"], 0.0)
        self.assertGreater(res_neg["total_capex_budget"], 0)

        # Exceeding 100% completion clamp check
        res_over = calculate_project_financials(
            structure_type="Luxury G+2 Villa / Independent Residence",
            built_up_sqft=25000,
            location_tier_name="Tier 1 (Metro Hubs: Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai)",
            completion_pct=140
        )
        self.assertEqual(res_over["completion_pct"], 100.0)
        self.assertEqual(res_over["capex_remaining"], 0.0)

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
        self.assertTrue(validated.is_demonstration_mode)

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
        self.assertTrue(validated.is_demonstration_mode)

    def test_weather_advisory_all_four_required_conditions(self):
        """Verify microclimate protocols for all 4 required scenarios."""
        # Condition 1: High Wind
        wind_p = get_weather_protocol("High Wind Advisory (> 45 km/h / Gale Gusts)")
        self.assertEqual(wind_p["status"], "Red")
        self.assertIn("free-slew", wind_p["crane_operations"].lower())

        # Condition 2: Heavy Rain
        rain_p = get_weather_protocol("Heavy Rain / Monsoon Storm (> 30 mm/hr)")
        self.assertEqual(rain_p["status"], "Red")
        self.assertIn("stop concreting", rain_p["concrete_protocol"].lower())
        self.assertIn("isolation", rain_p["electrical_safety"].lower())

        # Condition 3: Extreme Heat
        heat_p = get_weather_protocol("Extreme Heat Advisory (> 40°C / Heat Index > 46°C)")
        self.assertEqual(heat_p["status"], "Orange")
        self.assertIn("IS 7861", heat_p["concrete_protocol"])
        self.assertIn("shift", heat_p["worker_welfare"].lower())

        # Condition 4: Normal
        norm_p = get_weather_protocol("Normal / Favorable (22°C - 32°C, Wind < 20 km/h)")
        self.assertEqual(norm_p["status"], "Green")
        self.assertIn("clearance", norm_p["crane_operations"].lower())

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

    def test_sample_images_exist_and_valid(self):
        """Verify bundled sample test images exist, are non-empty, and are valid images."""
        ppe_img = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_ppe_site.jpg")
        crack_img = os.path.join(os.path.dirname(__file__), "..", "assets", "sample_crack_defect.jpg")
        self.assertTrue(os.path.exists(ppe_img))
        self.assertTrue(os.path.exists(crack_img))

        client = ConstructionGeminiClient()
        with open(ppe_img, "rb") as f:
            valid, msg = client.validate_image_bytes(f.read())
            self.assertTrue(valid)

        with open(crack_img, "rb") as f:
            valid, msg = client.validate_image_bytes(f.read())
            self.assertTrue(valid)

    def test_invalid_image_bytes_handling(self):
        """Verify invalid or corrupted files do not crash the engine."""
        client = ConstructionGeminiClient()
        
        # Test empty buffer
        valid, msg = client.validate_image_bytes(b"")
        self.assertFalse(valid)

        # Test corrupt text bytes
        valid, msg = client.validate_image_bytes(b"NOT_AN_IMAGE_CONTENT_STREAM")
        self.assertFalse(valid)

        # Test analyze with invalid bytes falls back gracefully to demonstration data
        res, is_mock = client.analyze_ppe_compliance(b"corrupt", "bad.jpg")
        self.assertTrue(is_mock)
        self.assertIn("safety_score", res)

    def test_clean_json_response_recovery(self):
        """Verify robust parsing of markdown-wrapped JSON and trailing commas."""
        client = ConstructionGeminiClient()

        # Fenced markdown JSON
        fenced = '```json\n{"safety_score": 88, "overall_status": "Compliant"}\n```'
        parsed = client.clean_json_response(fenced)
        self.assertEqual(parsed["safety_score"], 88)

        # Trailing comma recovery
        trailing = '{"safety_score": 75, "overall_status": "Minor Violation",}'
        parsed_tr = client.clean_json_response(trailing)
        self.assertEqual(parsed_tr["safety_score"], 75)

    def test_chatbot_query_handling(self):
        """Verify assistant handles questions, empty inputs, and context."""
        client = ConstructionGeminiClient()

        # Empty string handling
        reply_empty, _ = client.chat_query("", [])
        self.assertIn("Please provide an engineering question", reply_empty)

        # IS 456 query
        reply_is456, _ = client.chat_query("What are the IS 456 crack width limits?", [])
        self.assertIn("0.30 mm", reply_is456)
        self.assertIn("IS 456", reply_is456)

        # Crane query
        reply_crane, _ = client.chat_query("When should tower crane ops stop in high winds?", [])
        self.assertIn("38 km/h", reply_crane)
        self.assertIn("free-slew", reply_crane.lower())


if __name__ == "__main__":
    unittest.main()
