"""
resource_detector.py
Core_System_Cerebrus — Resource Detector

Detects what the system needs, what is surplus, and what tasks are pending.
Works with real sensor data, human reports, or simulated states.
"""

from datetime import datetime
from typing import Dict, List, Any


# Minimum stock levels before a shortage is flagged
STOCK_THRESHOLDS = {
    "food_kg":        50.0,
    "water_liters":   200.0,
    "energy_joules":  100_000.0,
    "recycling_kg":   30.0,    # triggers recycling task when above this
}


class ResourceDetector:
    def __init__(self):
        self.current_state: Dict[str, Any] = {}
        self.last_updated: str = ""

    def update_state(self, new_data: Dict[str, Any]):
        """
        Update the system state.
        In production this would pull from sensors / IoT / human reports.
        In simulation, pass a dict directly.
        """
        self.current_state.update(new_data)
        self.last_updated = datetime.now().isoformat()

    def detect_needs(self) -> List[Dict]:
        """
        Scan the current state and return a list of detected needs.
        Each need includes type, severity, and a human-readable description.
        """
        needs = []
        needs += self._check_axiom07_deficits()
        needs += self._check_stock_shortages()
        needs += self._check_pending_tasks()
        needs += self._check_volunteer_gaps()

        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        needs.sort(key=lambda n: severity_order.get(n.get("severity", "low"), 3))

        return needs

    def detect_surpluses(self) -> List[Dict]:
        """
        Identify resources available for redistribution.
        Surplus is flagged when stock is above the threshold.
        """
        surpluses = []
        stocks = self.current_state.get("stocks", {})

        for resource, threshold in STOCK_THRESHOLDS.items():
            if resource == "recycling_kg":
                continue  # recycling excess triggers tasks, not redistribution
            available = stocks.get(resource, 0)
            if available > threshold * 1.5:
                surpluses.append({
                    "type": "surplus",
                    "resource": resource,
                    "amount": round(available - threshold, 2),
                    "note": f"{resource} is {round(available / threshold * 100 - 100)}% above minimum stock"
                })

        return surpluses

    # ──────────────────────────────────────────────
    #  INTERNAL CHECKS
    # ──────────────────────────────────────────────

    def _check_axiom07_deficits(self) -> List[Dict]:
        needs = []
        metrics = self.current_state.get("axiom07_metrics", {})

        checks = [
            ("daily_calories", 2100, "kcal/day",    "Food supply below Axiom 07 minimum"),
            ("water_liters",   2.5,  "L/day",       "Water supply below Axiom 07 minimum"),
            ("temp_celsius",   18.0, "°C",           "Temperature below Axiom 07 minimum"),
            ("sleep_hours",    7.0,  "h/night",      "Sleep quality below Axiom 07 minimum"),
        ]

        for key, minimum, unit, label in checks:
            value = metrics.get(key)
            if value is None:
                continue
            if value < minimum:
                deficit_pct = round((minimum - value) / minimum * 100, 1)
                needs.append({
                    "type": "axiom07_deficit",
                    "metric": key,
                    "current": value,
                    "minimum": minimum,
                    "unit": unit,
                    "deficit_pct": deficit_pct,
                    "severity": "critical" if deficit_pct > 30 else "high" if deficit_pct > 15 else "medium",
                    "description": f"{label}: {value}{unit} (need {minimum}{unit}, deficit {deficit_pct}%)"
                })

        return needs

    def _check_stock_shortages(self) -> List[Dict]:
        needs = []
        stocks = self.current_state.get("stocks", {})

        for resource, threshold in STOCK_THRESHOLDS.items():
            if resource == "recycling_kg":
                continue
            available = stocks.get(resource, None)
            if available is None:
                continue
            if available < threshold:
                deficit_pct = round((threshold - available) / threshold * 100, 1)
                needs.append({
                    "type": "stock_shortage",
                    "resource": resource,
                    "available": available,
                    "threshold": threshold,
                    "deficit_pct": deficit_pct,
                    "severity": "critical" if deficit_pct > 50 else "high" if deficit_pct > 25 else "medium",
                    "description": f"Low stock: {resource} at {available} (threshold {threshold})"
                })

        return needs

    def _check_pending_tasks(self) -> List[Dict]:
        needs = []
        for task in self.current_state.get("pending_tasks", []):
            needs.append({
                "type": "pending_task",
                "task": task,
                "severity": task.get("severity", "medium") if isinstance(task, dict) else "medium",
                "description": task.get("name", str(task)) if isinstance(task, dict) else str(task)
            })
        return needs

    def _check_volunteer_gaps(self) -> List[Dict]:
        needs = []
        gaps = self.current_state.get("volunteer_gaps", [])
        for gap in gaps:
            needs.append({
                "type": "volunteer_gap",
                "task_id": gap.get("task_id"),
                "task_name": gap.get("name"),
                "slots_needed": gap.get("slots_needed", 1),
                "duration": gap.get("duration", "flexible"),
                "location": gap.get("location"),
                "severity": "high" if gap.get("urgent") else "medium",
                "description": (
                    f"Volunteer gap: '{gap.get('name')}' needs "
                    f"{gap.get('slots_needed', 1)} person(s) — {gap.get('location', 'any zone')}"
                )
            })
        return needs

    def summary(self) -> str:
        needs = self.detect_needs()
        surpluses = self.detect_surpluses()
        lines = [f"=== Resource Detector — {self.last_updated[:19]} ==="]
        lines.append(f"  Needs detected:    {len(needs)}")
        lines.append(f"  Surpluses detected: {len(surpluses)}")
        for n in needs:
            lines.append(f"  [{n['severity'].upper()}] {n['description']}")
        return "\n".join(lines)


if __name__ == "__main__":
    detector = ResourceDetector()
    detector.update_state({
        "axiom07_metrics": {
            "daily_calories": 1500,
            "water_liters": 1.8,
            "temp_celsius": 16.0,
        },
        "stocks": {
            "food_kg": 20,
            "water_liters": 80,
            "energy_joules": 200_000,
        },
        "pending_tasks": [
            {"name": "Greenhouse maintenance", "severity": "high"},
            {"name": "Recycling sorting", "severity": "medium"},
        ],
        "volunteer_gaps": [
            {"task_id": "t001", "name": "Harvest — Zone 7", "slots_needed": 3,
             "location": "Zone 7", "duration": "2 hours", "urgent": True}
        ]
    })

    print(detector.summary())
