"""
conflict_grammar.py
Core_System_Cerebrus — Conflict Grammar

Resolves contestations transparently, fairly, and on the record.
The system never decides in silence. Everything is explained and negotiable.
Restorative by design — never purely punitive.
"""

from datetime import datetime
from typing import Any, Dict, List


# Conflict severity levels (community-defined, not system-defined)
SEVERITY_CONFIG = {
    "physical_violence":    {"penalty_factor": 0.20, "reduction_days": 90},
    "sabotage":             {"penalty_factor": 0.30, "reduction_days": 60},
    "coercion":             {"penalty_factor": 0.35, "reduction_days": 60},
    "serious_dishonesty":   {"penalty_factor": 0.50, "reduction_days": 45},
    "minor_conflict":       {"penalty_factor": 0.80, "reduction_days": 14},
    "peaceful_disagreement":{"penalty_factor": 1.00, "reduction_days": 0},  # no penalty
}

REPAIR_PATHS = {
    "physical_violence": [
        "Participate in community mediation sessions (voluntary, ~8h total)",
        "Vital Civic Service: care tasks in a zone separate from the affected party (4 weeks)",
    ],
    "sabotage": [
        "Repair or replace what was damaged",
        "Vital Civic Service: maintenance tasks for 3 weeks",
    ],
    "coercion": [
        "Community mediation with an independent facilitator",
        "Written acknowledgment logged in the Ethical Memory Store",
    ],
    "serious_dishonesty": [
        "Transparent disclosure of the full situation to the Community Assembly",
        "Voluntary contribution to rebuild trust (negotiable with affected party)",
    ],
    "minor_conflict": [
        "Optional mediation — no action required if both parties agree",
    ],
    "peaceful_disagreement": [
        "No action required. Disagreement is healthy and logged for system learning.",
    ],
}


class ConflictGrammar:
    def __init__(self):
        self.resolution_history: List[Dict] = []

    def resolve(self, contestation: Dict, memory_store: Any) -> Dict:
        """
        Process a contestation and return a transparent resolution proposal.
        The human always retains the right to accept, counter-propose, or escalate.
        """
        contest_id = contestation.get("id", f"contest_{datetime.now().strftime('%H%M%S')}")
        reason = contestation.get("reason", "No reason provided")
        person_id = contestation.get("person_id", "unknown")
        contested_allocation = contestation.get("contested_allocation", {})
        proposed_alternative = contestation.get("proposed_alternative", {})

        conflict_type = self._classify(reason)
        new_suggestion = self._calculate_fair_adjustment(
            contested_allocation, proposed_alternative, conflict_type
        )

        resolution = {
            "timestamp": datetime.now().isoformat(),
            "type": "conflict_resolution",
            "contest_id": contest_id,
            "person_id": person_id,
            "original_reason": reason,
            "classified_as": conflict_type,
            "contested_allocation": contested_allocation,
            "new_suggestion": new_suggestion,
            "next_steps": self._next_steps(conflict_type),
            "note": (
                "You may accept this suggestion, propose a different alternative, "
                "or escalate to the Community Assembly. No penalty for contesting."
            )
        }

        self.resolution_history.append(resolution)

        if hasattr(memory_store, "log"):
            memory_store.log(resolution)

        return resolution

    def calculate_penalty_factor(self, conflict_history: List[Dict]) -> float:
        """
        Returns the factor by which a person's Need_Score is multiplied,
        based on their validated conflict history.
        Returns 1.0 (no penalty) if no conflicts exist.
        """
        if not conflict_history:
            return 1.0

        factor = 1.0
        now = datetime.now()

        for conflict in conflict_history:
            ctype = conflict.get("type", "minor_conflict")
            config = SEVERITY_CONFIG.get(ctype, SEVERITY_CONFIG["minor_conflict"])

            try:
                conflict_date = datetime.fromisoformat(conflict.get("timestamp", "2000-01-01"))
                days_elapsed = (now - conflict_date).days
                if days_elapsed < config["reduction_days"]:
                    factor = min(factor, config["penalty_factor"])
            except (ValueError, TypeError):
                pass

        return round(factor, 2)

    def generate_repair_path(self, person_id: str, conflict_type: str) -> Dict:
        """
        Suggests a restorative path — never purely punitive.
        The person can accept or decline. Declining keeps the penalty active longer.
        """
        options = REPAIR_PATHS.get(conflict_type, REPAIR_PATHS["minor_conflict"])
        return {
            "type": "repair_path_proposal",
            "person_id": person_id,
            "conflict_type": conflict_type,
            "options": options,
            "note": (
                "These are voluntary repair paths. Completing one restores your "
                "Need_Score to full sooner. You are never forced to accept."
            )
        }

    def _classify(self, reason: str) -> str:
        """Simple keyword-based classification. Expandable with NLP later."""
        r = reason.lower()
        if any(w in r for w in ["violen", "attack", "hit", "assault", "harm"]):
            return "physical_violence"
        if any(w in r for w in ["sabotag", "destroy", "break"]):
            return "sabotage"
        if any(w in r for w in ["force", "coer", "threaten", "pressure"]):
            return "coercion"
        if any(w in r for w in ["lie", "fraud", "deceiv", "dishon"]):
            return "serious_dishonesty"
        if any(w in r for w in ["unfair", "wrong", "disagree", "incorrect"]):
            return "peaceful_disagreement"
        return "minor_conflict"

    def _calculate_fair_adjustment(
        self, contested: Dict, proposed: Dict, conflict_type: str
    ) -> Dict:
        """
        Generates an adjusted allocation suggestion.
        If the person proposed an alternative, lean toward it.
        Otherwise, split more evenly from the contested values.
        """
        if proposed:
            return {"source": "human_proposal", "values": proposed}

        if not contested:
            return {"message": "No specific allocation to adjust."}

        adjusted = {}
        for key, value in contested.items():
            if isinstance(value, (int, float)):
                # Slight redistribution toward equity
                adjusted[key] = round(value * 0.90, 2)
            else:
                adjusted[key] = value

        return {"source": "system_adjustment", "values": adjusted,
                "note": "10% redistributed to increase equity. Open to further negotiation."}

    def _next_steps(self, conflict_type: str) -> List[str]:
        steps = [
            "Review the calculation breakdown (visible in the Ethical Memory Store).",
            "Accept this suggestion, propose your own, or request mediation.",
        ]
        if conflict_type in ("physical_violence", "sabotage", "coercion"):
            steps.append("A Community Assembly review has been flagged for this conflict.")
        return steps


if __name__ == "__main__":
    class DummyMemory:
        def log(self, data):
            import json
            print("Logged:", json.dumps(data, indent=2))

    grammar = ConflictGrammar()

    # Test a contestation
    result = grammar.resolve({
        "id": "contest_001",
        "person_id": "person_002",
        "reason": "I believe the allocation was unfair given my higher deficit",
        "contested_allocation": {"person_001": 3000, "person_002": 1500},
        "proposed_alternative": {"person_001": 2200, "person_002": 2300}
    }, DummyMemory())

    import json
    print(json.dumps(result, indent=2))

    # Test penalty factor
    conflicts = [{"type": "minor_conflict", "timestamp": "2026-03-01T00:00:00"}]
    print("\nPenalty factor:", grammar.calculate_penalty_factor(conflicts))
