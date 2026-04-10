"""
thermodynamic_orchestrator.py
Core_System_Cerebrus — Thermodynamic Orchestrator

The calculation engine. Distributes resources based on:
  1. Axiom 07 — physical well-being (calories, water, shelter, temperature)
  2. Need Score — higher deficit = higher priority
  3. Penalty factor — validated aggressors receive reduced priority temporarily
  4. Equity split — divisible resources are shared proportionally, never winner-takes-all
  5. Minimum randomisation — only as absolute last resort, with a public seed

The Orchestrator PROPOSES. Humans DECIDE.
"""

import random
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Tuple


# Axiom 07 minimum thresholds for physical survival
AXIOM07_MINIMUMS = {
    "daily_calories":    2100,   # kcal/day
    "water_liters":      2.5,    # litres/day
    "temp_celsius":      18.0,   # minimum ambient temperature
    "sleep_hours":       7.0,    # hours/night
}

# Weight of each metric in the Need Score calculation
AXIOM07_WEIGHTS = {
    "daily_calories": 0.40,
    "water_liters":   0.25,
    "temp_celsius":   0.20,
    "sleep_hours":    0.15,
}


class ThermodynamicOrchestrator:
    def __init__(self, memory_store: Any, conflict_grammar: Any):
        self.memory = memory_store
        self.conflict_grammar = conflict_grammar

    # ──────────────────────────────────────────────
    #  PUBLIC API
    # ──────────────────────────────────────────────

    def distribute(self, resources: List[Dict], recipients: List[Dict]) -> Dict:
        """
        Main distribution method.
        Returns a proposal dict — not a binding decision.
        """
        if not recipients:
            return {"status": "no_recipients", "allocation_proposals": {}}

        total_joules = sum(r.get("joules", 0) for r in resources)
        remaining = total_joules

        # Step 1 — Score every recipient
        scored = self._score_recipients(recipients)

        # Step 2 — Allocate proportionally to Need Score
        allocation = self._allocate(scored, total_joules)
        remaining = total_joules - sum(v["allocated_joules"] for v in allocation.values())

        # Step 3 — Distribute any leftover equally (never waste)
        if remaining > 0.01 and scored:
            extra = remaining / len(scored)
            for rec_id in allocation:
                allocation[rec_id]["allocated_joules"] = round(
                    allocation[rec_id]["allocated_joules"] + extra, 2
                )
                allocation[rec_id]["reason"] += " + equitable surplus share"
            remaining = 0.0

        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_joules_available": total_joules,
            "total_joules_allocated": round(total_joules - remaining, 2),
            "remaining_joules": round(remaining, 2),
            "allocation_proposals": allocation,
            "note": (
                "All proposals are voluntary. "
                "Recipients may accept, reject, negotiate, or propose an alternative "
                "through the Conflict Grammar — with no penalty."
            )
        }

        self.memory.log({
            "type": "resource_distribution",
            "resources": resources,
            "scores": {r["id"]: r["need_score"] for r in scored},
            "allocation": allocation,
        })

        return result

    def resolve_conflict(self, contestation: Dict) -> Dict:
        """Activate the Conflict Grammar when someone contests a proposal."""
        return self.conflict_grammar.resolve(contestation, self.memory)

    # ──────────────────────────────────────────────
    #  SCORING
    # ──────────────────────────────────────────────

    def _score_recipients(self, recipients: List[Dict]) -> List[Dict]:
        """
        Compute Need_Score for each recipient.
        Higher score = further below Axiom 07 minimums = higher priority.
        Penalty factor from Conflict Grammar reduces score for validated aggressors.
        """
        scored = []
        for person in recipients:
            metrics = person.get("axiom07_metrics", {})
            raw_score = self._compute_need_score(metrics)

            # Apply conflict penalty if any
            conflict_history = person.get("conflict_history", [])
            penalty = self.conflict_grammar.calculate_penalty_factor(conflict_history)
            final_score = round(raw_score * penalty, 2)

            scored.append({
                **person,
                "raw_need_score": raw_score,
                "penalty_factor": penalty,
                "need_score": final_score,
            })

        # Sort: highest need first
        scored.sort(key=lambda x: x["need_score"], reverse=True)
        return scored

    def _compute_need_score(self, metrics: Dict) -> float:
        """
        Need Score = weighted sum of normalised deficits below Axiom 07 minimums.
        Score is 0 if all minimums are met. Higher = more urgent.
        """
        score = 0.0
        for metric, minimum in AXIOM07_MINIMUMS.items():
            actual = metrics.get(metric, minimum)  # assume minimum if not reported
            deficit = max(0.0, minimum - actual)
            normalised = deficit / minimum  # 0.0–1.0
            score += normalised * AXIOM07_WEIGHTS.get(metric, 0.1)

        return round(score * 1000, 2)  # scale to readable number (0–1000)

    # ──────────────────────────────────────────────
    #  ALLOCATION
    # ──────────────────────────────────────────────

    def _allocate(self, scored: List[Dict], total_joules: float) -> Dict:
        """
        Proportional allocation based on Need Score.
        If all scores are zero (everyone is fine), divide equally.
        Tie-breaking: highest deficit first → equal split → public random seed.
        """
        total_score = sum(r["need_score"] for r in scored)
        allocation = {}

        for person in scored:
            pid = person["id"]
            requested = person.get("requested_joules", total_joules)

            if total_score == 0:
                # Everyone meets minimums — equal distribution
                share = total_joules / len(scored)
                reason = "Equal distribution — all Axiom 07 minimums met"
            else:
                share = (person["need_score"] / total_score) * total_joules
                reason = self._allocation_reason(person)

            actual = min(requested, share)

            allocation[pid] = {
                "allocated_joules": round(actual, 2),
                "need_score": person["need_score"],
                "penalty_factor": person["penalty_factor"],
                "reason": reason,
            }

            if person["penalty_factor"] < 1.0:
                days_left = self._days_until_full_score(person.get("conflict_history", []))
                allocation[pid]["penalty_note"] = (
                    f"Priority reduced to {int(person['penalty_factor']*100)}% "
                    f"due to validated conflict history. "
                    f"Full priority restored in ~{days_left} days, or sooner via a repair path."
                )

        return allocation

    def _allocation_reason(self, person: Dict) -> str:
        score = person["need_score"]
        if score > 500:
            return "Critical Axiom 07 deficit — highest priority"
        if score > 200:
            return "Significant Axiom 07 deficit — elevated priority"
        if score > 50:
            return "Moderate need — proportional allocation"
        return "Low deficit — standard proportional distribution"

    def _days_until_full_score(self, conflict_history: List[Dict]) -> int:
        """Estimate days until penalty expires."""
        if not conflict_history:
            return 0
        from Modules.conflict_grammar import SEVERITY_CONFIG
        max_days = 0
        now = datetime.now()
        for c in conflict_history:
            cfg = SEVERITY_CONFIG.get(c.get("type", "minor_conflict"), {})
            reduction_days = cfg.get("reduction_days", 0)
            try:
                elapsed = (now - datetime.fromisoformat(c["timestamp"])).days
                remaining = max(0, reduction_days - elapsed)
                max_days = max(max_days, remaining)
            except (KeyError, ValueError):
                pass
        return max_days

    # ──────────────────────────────────────────────
    #  TIE-BREAKING: public random seed
    # ──────────────────────────────────────────────

    def _public_random_seed(self) -> int:
        """
        Generates a deterministic, public seed for tie-breaking.
        Seed = SHA256(current minute timestamp) — anyone can verify it.
        """
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M")
        seed_hex = hashlib.sha256(ts.encode()).hexdigest()[:8]
        return int(seed_hex, 16)


# ──────────────────────────────────────────────
#  DEMO
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import json, sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from Modules.ethical_memory_store import EthicalMemoryStore
    from Modules.conflict_grammar import ConflictGrammar

    memory = EthicalMemoryStore()
    grammar = ConflictGrammar()
    orchestrator = ThermodynamicOrchestrator(memory, grammar)

    resources = [{"id": "solar_batch_001", "joules": 12000, "type": "energy"}]

    recipients = [
        {
            "id": "person_001",
            "axiom07_metrics": {"daily_calories": 1400, "water_liters": 1.8},
            "requested_joules": 5000,
            "conflict_history": []
        },
        {
            "id": "person_002",
            "axiom07_metrics": {"daily_calories": 2200, "water_liters": 3.0},
            "requested_joules": 3000,
            "conflict_history": []
        },
        {
            "id": "person_003",
            "axiom07_metrics": {"daily_calories": 800, "water_liters": 1.0},
            "requested_joules": 6000,
            "conflict_history": [{"type": "minor_conflict", "timestamp": "2026-03-01T00:00:00"}]
        },
    ]

    result = orchestrator.distribute(resources, recipients)
    print(json.dumps(result, indent=2))
