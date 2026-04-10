"""
state_manager.py
Core_System_Cerebrus — Persistent State Manager

Saves and loads the world state between cycles.
Stocks deplete when resources are accepted. They replenish gradually (simulating
solar generation, harvests, deliveries, etc.).
Everything is stored in data/world_state.json — human-readable and editable.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


# ──────────────────────────────────────────────
#  DEFAULT STARTING STATE
# ──────────────────────────────────────────────

DEFAULT_STATE = {
    "meta": {
        "cycle": 0,
        "last_updated": "",
        "version": "1.0"
    },
    "stocks": {
        "food_kg":        20.0,
        "water_liters":   80.0,
        "energy_joules":  50_000.0,
        "recycling_kg":   5.0
    },
    "axiom07_metrics": {
        "daily_calories": 1400.0,
        "water_liters":   1.8,
        "temp_celsius":   16.0,
        "sleep_hours":    6.5
    },
    "pending_tasks": [
        {"name": "Greenhouse maintenance", "severity": "high"},
        {"name": "Recycling sorting",      "severity": "medium"}
    ],
    "volunteer_gaps": [
        {
            "task_id": "t001",
            "name": "Harvest — Zone 7",
            "slots_needed": 3,
            "location": "Zone 7",
            "duration": "2 hours",
            "urgent": True
        },
        {
            "task_id": "t002",
            "name": "Water pipe check — Zone 3",
            "slots_needed": 1,
            "location": "Zone 3",
            "duration": "1 hour",
            "urgent": False
        }
    ],
    "resources_available": [
        {"id": "solar_batch", "joules": 12000.0, "type": "energy"}
    ],
    # Replenishment rates per cycle (simulates nature + community production)
    "replenishment_rates": {
        "food_kg":        3.5,     # kg of food produced per cycle
        "water_liters":   25.0,    # litres collected/purified per cycle
        "energy_joules":  8000.0,  # joules generated (solar/wind) per cycle
        "recycling_kg":   1.0
    },
    # Consumption rates per cycle (simulates baseline usage)
    "consumption_rates": {
        "food_kg":        5.0,
        "water_liters":   30.0,
        "energy_joules":  6000.0,
        "recycling_kg":   0.0
    }
}

# How much Axiom 07 metrics improve per cycle when resources are accepted
AXIOM07_RECOVERY = {
    "daily_calories": 80.0,    # kcal gained per cycle if food proposals accepted
    "water_liters":   0.2,     # litres/day improvement per cycle
    "temp_celsius":   0.3,     # degrees gained (heating/insulation)
    "sleep_hours":    0.1
}

# Hard maximums (post-scarcity ceiling)
AXIOM07_MAX = {
    "daily_calories": 2800.0,
    "water_liters":   4.0,
    "temp_celsius":   24.0,
    "sleep_hours":    9.0
}


class StateManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "world_state.json"
        self.state = self._load()

    # ──────────────────────────────────────────────
    #  LOAD / SAVE
    # ──────────────────────────────────────────────

    def _load(self) -> Dict:
        """Load state from disk, or create default if first run."""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            print(f"[State] Loaded world state — cycle #{state['meta']['cycle']}")
            return state
        else:
            print("[State] No saved state found — starting from default.")
            self._save(DEFAULT_STATE)
            return dict(DEFAULT_STATE)

    def _save(self, state: Dict = None):
        """Persist current state to disk."""
        target = state or self.state
        target["meta"]["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(target, f, indent=2, ensure_ascii=False)

    # ──────────────────────────────────────────────
    #  CYCLE MANAGEMENT
    # ──────────────────────────────────────────────

    def advance_cycle(self, accepted_joules: float = 0.0, accepted_proposals: int = 0):
        """
        Advance the world state by one cycle.
        - Replenish stocks (nature + production)
        - Apply consumption (baseline usage)
        - If resources were accepted, improve Axiom 07 metrics
        - Increment cycle counter
        """
        self.state["meta"]["cycle"] += 1
        cycle = self.state["meta"]["cycle"]

        stocks = self.state["stocks"]
        replenish = self.state["replenishment_rates"]
        consume = self.state["consumption_rates"]

        # Apply replenishment
        for resource in stocks:
            stocks[resource] = round(
                stocks[resource] + replenish.get(resource, 0), 2
            )

        # Apply consumption
        for resource in stocks:
            stocks[resource] = round(
                max(0.0, stocks[resource] - consume.get(resource, 0)), 2
            )

        # Update energy resource available for next cycle
        for r in self.state["resources_available"]:
            if r["type"] == "energy":
                r["joules"] = round(
                    replenish.get("energy_joules", 8000) + stocks["energy_joules"] * 0.1, 2
                )

        # Improve Axiom 07 metrics if proposals were accepted
        if accepted_proposals > 0:
            metrics = self.state["axiom07_metrics"]
            for metric, gain in AXIOM07_RECOVERY.items():
                current = metrics.get(metric, 0)
                max_val = AXIOM07_MAX.get(metric, current + 1)
                metrics[metric] = round(min(max_val, current + gain * accepted_proposals), 2)

        self._save()
        print(f"[State] Cycle #{cycle} saved. Stocks updated.")
        return cycle

    def reset_to_default(self):
        """Reset world state to defaults (useful for testing)."""
        self.state = dict(DEFAULT_STATE)
        self.state["meta"]["cycle"] = 0
        self._save()
        print("[State] World state reset to defaults.")

    # ──────────────────────────────────────────────
    #  ACCESSORS
    # ──────────────────────────────────────────────

    def get_detector_state(self) -> Dict:
        """Returns the state dict expected by ResourceDetector."""
        return {
            "axiom07_metrics": self.state["axiom07_metrics"],
            "stocks":          self.state["stocks"],
            "pending_tasks":   self.state["pending_tasks"],
            "volunteer_gaps":  self.state["volunteer_gaps"]
        }

    def get_resources(self) -> list:
        return self.state["resources_available"]

    def get_cycle(self) -> int:
        return self.state["meta"]["cycle"]

    def get_stocks(self) -> Dict:
        return self.state["stocks"]

    def get_axiom07(self) -> Dict:
        return self.state["axiom07_metrics"]

    def summary(self) -> str:
        c = self.state["meta"]["cycle"]
        s = self.state["stocks"]
        m = self.state["axiom07_metrics"]
        lines = [
            f"  Cycle #{c} | {self.state['meta'].get('last_updated','')[:19]}",
            f"  Stocks  → food: {s.get('food_kg',0):.1f}kg | "
            f"water: {s.get('water_liters',0):.0f}L | "
            f"energy: {s.get('energy_joules',0)/1000:.1f}kJ",
            f"  Axiom07 → {m.get('daily_calories',0):.0f}kcal/day | "
            f"{m.get('water_liters',0):.1f}L/day | "
            f"{m.get('temp_celsius',0):.1f}°C | "
            f"{m.get('sleep_hours',0):.1f}h sleep"
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    sm = StateManager()
    print(sm.summary())
    sm.advance_cycle(accepted_joules=5000, accepted_proposals=2)
    print(sm.summary())
