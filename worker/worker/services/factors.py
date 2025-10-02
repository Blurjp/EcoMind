import os
from pathlib import Path
from typing import Dict, Any

import yaml


class FactorsService:
    """Service for loading and merging environmental factors."""

    def __init__(self):
        self.defaults: Dict[str, Any] = {}
        self.grid_intensity: Dict[str, float] = {}

    def load_defaults(self):
        """Load default factors from YAML."""
        # Look for factors_defaults.yaml in docs/ or local
        possible_paths = [
            Path("docs/factors_defaults.yaml"),
            Path("../docs/factors_defaults.yaml"),
            Path("../../docs/factors_defaults.yaml"),
        ]

        factors_file = None
        for p in possible_paths:
            if p.exists():
                factors_file = p
                break

        if factors_file:
            with open(factors_file) as f:
                data = yaml.safe_load(f)
                self.defaults = data
                print(f"✅ Loaded factors from {factors_file}")
        else:
            print("⚠️  factors_defaults.yaml not found, using hardcoded defaults")
            self._load_hardcoded_defaults()

        # Load grid intensity
        possible_grid_paths = [
            Path("docs/grid_intensity.yaml"),
            Path("../docs/grid_intensity.yaml"),
            Path("../../docs/grid_intensity.yaml"),
        ]

        grid_file = None
        for p in possible_grid_paths:
            if p.exists():
                grid_file = p
                break

        if grid_file:
            with open(grid_file) as f:
                data = yaml.safe_load(f)
                regions = data.get("regions", {})
                self.grid_intensity = {
                    k: v["gco2_per_kwh"] for k, v in regions.items()
                }
                print(f"✅ Loaded grid intensity from {grid_file}")
        else:
            print("⚠️  grid_intensity.yaml not found, using defaults")
            self.grid_intensity = {"UNKNOWN": 500, "GLOBAL": 475}

    def _load_hardcoded_defaults(self):
        """Fallback hardcoded defaults."""
        self.defaults = {
            "defaults": {
                "pue": 1.5,
                "water_l_per_kwh": 1.8,
                "co2_kg_per_kwh": 0.4,
            },
            "providers": {
                "openai": {
                    "kwh_per_call": 0.0003,
                    "models": {
                        "gpt-4o": {"kwh_per_call": 0.0005},
                        "gpt-4": {"kwh_per_call": 0.0006},
                        "gpt-3.5-turbo": {"kwh_per_call": 0.0002},
                    },
                },
                "anthropic": {
                    "kwh_per_call": 0.0004,
                    "models": {
                        "claude-3-opus": {"kwh_per_call": 0.0007},
                        "claude-3-sonnet": {"kwh_per_call": 0.0004},
                        "claude-3-haiku": {"kwh_per_call": 0.0001},
                    },
                },
                "unknown": {"kwh_per_call": 0.0003},
            },
        }

    def get_kwh_per_call(self, provider: str, model: str) -> float:
        """Get kWh per call for a provider/model."""
        providers = self.defaults.get("providers", {})
        provider_data = providers.get(provider, providers.get("unknown", {}))

        # Check model-specific
        models = provider_data.get("models", {})
        if model and model in models:
            return models[model].get("kwh_per_call", 0.0003)

        # Provider default
        return provider_data.get("kwh_per_call", 0.0003)

    def get_pue(self) -> float:
        """Get Power Usage Effectiveness."""
        return self.defaults.get("defaults", {}).get("pue", 1.5)

    def get_water_per_kwh(self) -> float:
        """Get water liters per kWh."""
        return self.defaults.get("defaults", {}).get("water_l_per_kwh", 1.8)

    def get_co2_per_kwh(self) -> float:
        """Get default CO2 kg per kWh (global avg)."""
        return self.defaults.get("defaults", {}).get("co2_kg_per_kwh", 0.4)

    def get_grid_intensity(self, region: str) -> float:
        """Get grid carbon intensity (gCO2/kWh) for a region."""
        return self.grid_intensity.get(region, self.grid_intensity.get("UNKNOWN", 500))