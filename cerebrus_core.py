"""
cerebrus_core.py
Core_System_Cerebrus — Main Executive Core

Brings all modules together into one coherent system cycle:
  Detect → Score → Propose → Human decides → Log → Advance state

World state persists between runs in data/world_state.json.
Run this file to start a cycle. Run again to continue from where you left off.
"""

import sys
import os
import json

# Enable ANSI colour codes on Windows
if sys.platform == "win32":
    os.system("color")
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# Make Modules importable from any working directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Modules"))

from ethical_memory_store       import EthicalMemoryStore
from conflict_grammar           import ConflictGrammar
from thermodynamic_orchestrator import ThermodynamicOrchestrator
from resource_detector          import ResourceDetector
from proposal_engine            import ProposalEngine
from vital_service_matcher      import VitalServiceMatcher
from human_interface            import HumanInterface
from state_manager              import StateManager


# ──────────────────────────────────────────────────────────
#  DEMO PEOPLE  (fixed simulation profiles)
# ──────────────────────────────────────────────────────────

DEMO_PEOPLE = [
    {
        "id": "person_001",
        "name": "Alex",
        "requested_joules": 5000,
        "conflict_history": [],
        "skills": ["agriculture", "maintenance"],
        "interests": ["environment"],
        "zone": "Zone 7",
        "availability": "flexible",
        "past_contributions": ["greenhouse_repair_2025"]
    },
    {
        "id": "person_002",
        "name": "Sam",
        "requested_joules": 3000,
        "conflict_history": [],
        "skills": ["teaching", "logistics"],
        "interests": ["education"],
        "zone": "Zone 3",
        "availability": "part-time"
    },
    {
        "id": "person_003",
        "name": "Jordan",
        "requested_joules": 6000,
        "conflict_history": [{"type": "minor_conflict", "timestamp": "2026-03-01T00:00:00"}],
        "skills": ["recycling", "logistics"],
        "interests": ["logistics"],
        "zone": "Zone 7",
        "availability": "full-time"
    },
]

DEMO_VITAL_TASKS = [
    {
        "id": "vcs_001",
        "name": "Greenhouse coordination — Zone 7",
        "category": "environment",
        "required_skills": ["agriculture"],
        "location": "Zone 7",
        "duration": "6–12 months",
        "duration_type": "long-term",
        "slots_needed": 2,
        "impact": "Feeds ~300 people year-round"
    },
    {
        "id": "vcs_002",
        "name": "Recycling centre sorting — Zone 7",
        "category": "maintenance",
        "required_skills": ["recycling"],
        "location": "Zone 7",
        "duration": "2 hours",
        "duration_type": "micro",
        "slots_needed": 4,
        "impact": "Closes the recycling loop for the week"
    },
]


# ──────────────────────────────────────────────────────────
#  CORE CLASS
# ──────────────────────────────────────────────────────────

class CerebrusCore:
    def __init__(self):
        self.state_mgr     = StateManager()
        self.memory        = EthicalMemoryStore()
        self.grammar       = ConflictGrammar()
        self.orchestrator  = ThermodynamicOrchestrator(self.memory, self.grammar)
        self.detector      = ResourceDetector()
        self.engine        = ProposalEngine(self.orchestrator)
        self.vital_matcher = VitalServiceMatcher()
        self.ui            = HumanInterface()

        self.memory.log({
            "type": "system_start",
            "message": f"Core_System_Cerebrus initialised — cycle #{self.state_mgr.get_cycle() + 1}"
        })

    def run_cycle(self):
        """
        One full system cycle — state is saved at the end.
        Run this again to continue from where you left off.
        """
        cycle_num = self.state_mgr.get_cycle() + 1

        print("\n" + "═" * 60)
        print(f"   CORE_SYSTEM_CEREBRUS — Cycle #{cycle_num}")
        print("═" * 60)

        # ── PREVIOUS STATE SUMMARY ─────────────────
        if self.state_mgr.get_cycle() > 0:
            print("\n  [Continuing from previous state]")
            print(self.state_mgr.summary())

        # ── 1. DETECT ──────────────────────────────
        current_state = self.state_mgr.get_detector_state()
        resources     = self.state_mgr.get_resources()
        people        = self._enrich_people(DEMO_PEOPLE, current_state["axiom07_metrics"])

        self.detector.update_state(current_state)
        print("\n" + self.detector.summary())

        # ── 2. RESOURCE PROPOSALS ──────────────────
        print("\n" + "─" * 60)
        print("  RESOURCE DISTRIBUTION PROPOSALS")
        print("─" * 60)

        proposals = self.engine.generate_resource_proposals(resources, people)
        self.ui.show_proposals(proposals)

        # ── 3. HUMAN RESPONSES ─────────────────────
        accepted_count  = 0
        accepted_joules = 0.0

        for prop in proposals:
            response = self.ui.get_user_response(prop)
            self.memory.log({"type": "human_response", "response": response})

            action = response.get("action", "ignore")

            if "accept" in action:
                accepted_count  += 1
                accepted_joules += prop.get("offered_joules", 0)

            elif action in ("negotiate", "suggest_alternative"):
                resolution = self.orchestrator.resolve_conflict({
                    "id": f"contest_{prop['id']}",
                    "person_id": prop.get("person_id"),
                    "reason": response.get("counter_proposal", "Negotiation requested"),
                    "contested_allocation": {prop.get("person_id"): prop.get("offered_joules", 0)},
                    "proposed_alternative": {}
                })
                self.ui.show_conflict_resolution(resolution)

        # ── 4. VITAL CIVIC SERVICE ─────────────────
        print("\n" + "─" * 60)
        print("  VITAL CIVIC SERVICE — OPEN TASKS")
        print("─" * 60)

        for person in people:
            vcs_proposals = self.vital_matcher.find_matches(person, DEMO_VITAL_TASKS)
            if vcs_proposals:
                self.ui.show_proposals(vcs_proposals[:1])
                vcs_response = self.ui.get_user_response(vcs_proposals[0])
                self.memory.log({"type": "vital_service_response", "response": vcs_response})
                if "accept" in vcs_response.get("action", ""):
                    accepted_count += 1

        # ── 5. ADVANCE WORLD STATE ─────────────────
        new_cycle = self.state_mgr.advance_cycle(
            accepted_joules=accepted_joules,
            accepted_proposals=accepted_count
        )

        # ── 6. END OF CYCLE REPORT ─────────────────
        print("\n" + "─" * 60)
        print("  END OF CYCLE REPORT")
        print("─" * 60)
        print(f"\n  Proposals accepted this cycle: {accepted_count}")
        print(f"  Energy accepted:               {accepted_joules/1000:.1f} kJ")
        print("\n  [Updated world state]")
        print(self.state_mgr.summary())

        self.ui.show_memory_summary(self.memory.export_summary(last_n=6))

        integrity = self.memory.verify_integrity()
        colour = "\033[92m" if integrity["status"] == "intact" else "\033[91m"
        print(f"  Memory integrity: {colour}{integrity['status']}\033[0m "
              f"({integrity['total_entries']} entries)\n")

        print("═" * 60)
        print(f"   Cycle #{new_cycle} complete. State saved to data/world_state.json")
        print("═" * 60 + "\n")

    # ──────────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────────

    def _enrich_people(self, people: list, axiom07: dict) -> list:
        """
        Inject live Axiom 07 metrics into each person profile.
        Adds small individual variation (±15%) around the world average.
        In production, each person would have their own sensor readings.
        """
        enriched = []
        for i, person in enumerate(people):
            p = dict(person)
            variance = 1.0 + (i - 1) * 0.15
            p["axiom07_metrics"] = {
                metric: round(max(0.0, value * variance), 2)
                for metric, value in axiom07.items()
            }
            enriched.append(p)
        return enriched


# ──────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    core = CerebrusCore()
    core.run_cycle()
