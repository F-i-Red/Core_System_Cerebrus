"""
proposal_engine.py
Core_System_Cerebrus — Proposal Engine

The "enticer" — never commands, only suggests.
Generates personalised voluntary proposals for people and communities.
Every proposal explains the impact clearly. Every proposal can be refused without consequence.
"""

from datetime import datetime
from typing import Any, Dict, List


class ProposalEngine:
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def generate_resource_proposals(
        self, resources: List[Dict], recipients: List[Dict]
    ) -> List[Dict]:
        """
        Generate voluntary resource proposals based on thermodynamic distribution.
        """
        distribution = self.orchestrator.distribute(resources, recipients)
        proposals = []

        for person_id, alloc in distribution.get("allocation_proposals", {}).items():
            joules = alloc.get("allocated_joules", 0)
            proposals.append({
                "id": f"prop_{person_id}_{datetime.now().strftime('%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "type": "resource_allocation",
                "person_id": person_id,
                "module": "Core_System_Cerebrus",
                "offered_joules": joules,
                "offered_joules_readable": self._joules_to_human(joules),
                "reason": alloc.get("reason", "Proportional distribution based on Axiom 07"),
                "need_score": alloc.get("need_score"),
                "penalty_note": alloc.get("penalty_note"),
                "impact": self._describe_impact(joules),
                "voluntary_note": (
                    "This is a voluntary proposal. You may accept, reject, "
                    "negotiate, or ignore it — no penalty either way."
                ),
                "options": ["Accept", "Reject", "Negotiate", "Ignore"]
            })

        return proposals

    def generate_task_proposal(self, person: Dict, need: Dict) -> Dict:
        """
        Generate a voluntary task proposal for a detected community need.
        Personalised based on proximity, skills, and past preferences.
        """
        task_name = need.get("description", need.get("task", "Community task"))
        location = need.get("location", "nearby")
        duration = need.get("duration", "flexible")
        slots_needed = need.get("slots_needed", 1)

        return {
            "id": f"task_{person.get('id','?')}_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "task_proposal",
            "person_id": person.get("id"),
            "module": "Core_System_Cerebrus",
            "task": task_name,
            "location": location,
            "suggested_duration": duration,
            "slots_still_needed": slots_needed,
            "impact": (
                f"If {slots_needed} people each contribute {duration}, "
                f"this need is fully resolved for the community."
            ),
            "why_you": self._personalised_reason(person, need),
            "voluntary_note": (
                "Completely voluntary. You can accept right now, schedule it for later, "
                "suggest a different contribution, or simply decline — no questions asked."
            ),
            "options": ["Accept", "Schedule for later", "Suggest alternative", "Decline"]
        }

    def generate_event_proposal(self, person: Dict, event: Dict) -> Dict:
        """
        Generate an event-entry proposal tied to a contribution (the 'ticket' model).
        Example: a concert with limited seats, where entry is a small voluntary contribution.
        """
        contribution = event.get("suggested_contribution", {})
        return {
            "id": f"event_{person.get('id','?')}_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "event_proposal",
            "person_id": person.get("id"),
            "module": "Core_System_Cerebrus",
            "event_name": event.get("name"),
            "event_date": event.get("date"),
            "seats_available": event.get("seats_available"),
            "suggested_contribution": {
                "task": contribution.get("task", "1 hour of maintenance or cleaning"),
                "duration": contribution.get("duration", "1 hour"),
                "window": contribution.get("window", "within the next 2 weeks"),
            },
            "impact": (
                f"If {event.get('seats_available', '?')} people each contribute "
                f"{contribution.get('duration','1h')}, the event happens and the space stays spotless."
            ),
            "voluntary_note": (
                "This contribution is entirely voluntary. "
                "You can propose a different contribution, attend without contributing, "
                "or simply not attend — all fine."
            ),
            "options": [
                "Accept contribution and attend",
                "Propose a different contribution",
                "Attend without contributing",
                "Decline"
            ]
        }

    # ──────────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────────

    def _joules_to_human(self, joules: float) -> str:
        if joules >= 1_000_000:
            return f"{joules/1_000_000:.1f} MJ"
        if joules >= 1_000:
            return f"{joules/1_000:.1f} kJ"
        return f"{joules:.0f} J"

    def _describe_impact(self, joules: float) -> str:
        kcal = joules / 4184
        if kcal >= 2100:
            return f"Covers full daily caloric needs for one person ({kcal:.0f} kcal equivalent)"
        if kcal >= 500:
            return f"Covers a significant portion of daily caloric needs ({kcal:.0f} kcal equivalent)"
        return f"Contributes to community energy pool ({joules:.0f} J)"

    def _personalised_reason(self, person: Dict, need: Dict) -> str:
        reasons = []
        person_skills = person.get("skills", [])
        need_skills = need.get("required_skills", [])

        if any(s in need_skills for s in person_skills):
            matched = [s for s in person_skills if s in need_skills]
            reasons.append(f"Your skills ({', '.join(matched)}) are a great match for this task")

        location = need.get("location")
        if location and location in person.get("zone", ""):
            reasons.append(f"This task is in your zone ({location})")

        past = person.get("past_contributions", [])
        if any(need.get("category") in p for p in past):
            reasons.append("You've helped with similar tasks before")

        if not reasons:
            reasons.append("You're part of this community and your contribution matters")

        return ". ".join(reasons) + "."


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from Modules.ethical_memory_store import EthicalMemoryStore
    from Modules.conflict_grammar import ConflictGrammar
    from Modules.thermodynamic_orchestrator import ThermodynamicOrchestrator

    memory = EthicalMemoryStore()
    grammar = ConflictGrammar()
    orchestrator = ThermodynamicOrchestrator(memory, grammar)
    engine = ProposalEngine(orchestrator)

    # Resource proposals
    resources = [{"id": "solar_001", "joules": 10000}]
    recipients = [
        {"id": "person_001", "axiom07_metrics": {"daily_calories": 1400}, "conflict_history": []},
        {"id": "person_002", "axiom07_metrics": {"daily_calories": 2200}, "conflict_history": []},
    ]
    print("=== Resource Proposals ===")
    for p in engine.generate_resource_proposals(resources, recipients):
        print(f"  {p['person_id']}: {p['offered_joules_readable']} — {p['reason']}")

    # Event proposal
    print("\n=== Event Proposal ===")
    event_prop = engine.generate_event_proposal(
        {"id": "person_001"},
        {
            "name": "Dance performance — Central Square",
            "date": "2026-05-10",
            "seats_available": 50,
            "suggested_contribution": {"task": "Cleaning or maintenance", "duration": "1 hour", "window": "within 2 weeks"}
        }
    )
    import json
    print(json.dumps(event_prop, indent=2))
