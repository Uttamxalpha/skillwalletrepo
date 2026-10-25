"""
Daily Site Assistant & Weather-Aware Advisory Module (Epic 5)
Platform ID: 6ac4c98d1dcde6d7857c1642
Provides dynamic meteorological safety hazard protocols under OSHA and IS guidelines.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any
from config import WEATHER_PROTOCOLS

def get_weather_protocol(condition_name: str) -> Dict[str, Any]:
    """Retrieves full engineering protocol for the selected weather condition."""
    protocol = WEATHER_PROTOCOLS.get(condition_name, list(WEATHER_PROTOCOLS.values())[0])
    return {
        "condition": condition_name,
        "status": protocol["status"],
        "severity": protocol["severity"],
        "crane_operations": protocol["crane_operations"],
        "concrete_protocol": protocol["concrete_protocol"],
        "electrical_safety": protocol["electrical_safety"],
        "worker_welfare": protocol["worker_welfare"],
        "scaffolding_status": protocol["scaffolding_status"]
    }

def get_weather_alert_level_color(status: str) -> str:
    """Returns CSS color code for status badge."""
    mapping = {
        "Green": "#10B981",    # Emerald
        "Orange": "#F59E0B",   # Amber
        "Red": "#EF4444"       # Rose/Red
    }
    return mapping.get(status, "#6B7280")


if __name__ == "__main__":
    print("=" * 70)
    print("🌦️ CONSTRUCT-AI: Weather Advisory Matrix (Epic 5)")
    print("Platform ID: 6ac4c98d1dcde6d7857c1642")
    print("=" * 70)
    p = get_weather_protocol("High Wind Advisory (> 45 km/h / Gale Gusts)")
    print(f"Condition: {p['condition']}")
    print(f"Severity: {p['severity']} ({p['status']})")
    print(f"Crane Ops: {p['crane_operations']}")
    print("=" * 70)
    print("✅ Weather Advisory matrix loaded successfully!")


