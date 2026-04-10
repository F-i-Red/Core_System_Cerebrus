"""
human_interface.py
Core_System_Cerebrus — Human Interface

Displays proposals to humans and collects their responses.
Console-based for now. Designed to be easily replaced by a web UI or voice interface.

Every interaction is clear, calm, and non-coercive.
"""

import json
from typing import Any, Dict, List, Optional


# ANSI colour codes (work on Windows 10+ and all Unix terminals)
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
DIM    = "\033[2m"


class HumanInterface:
    def __init__(self, use_colour: bool = True):
        self.use_colour = use_colour

    # ──────────────────────────────────────────────
    #  DISPLAY
    # ──────────────────────────────────────────────

    def show_proposals(self, proposals: List[Dict]) -> None:
        if not proposals:
            self._print(f"\n{DIM}No proposals at this time.{RESET}\n")
            return

        self._print(f"\n{BOLD}{CYAN}=== VOLUNTARY PROPOSALS ==={RESET}\n")
        for i, prop in enumerate(proposals, 1):
            self._show_single_proposal(i, prop)

    def _show_single_proposal(self, index: int, prop: Dict) -> None:
        ptype = prop.get("type", "proposal")
        module = prop.get("module", "Core_System_Cerebrus")
        person = prop.get("person_id", "")

        self._print(f"{BOLD}[{index}] {module}{RESET}"
                    + (f"  →  {person}" if person else ""))

        # Type-specific display
        if ptype == "resource_allocation":
            self._show_resource_proposal(prop)
        elif ptype == "task_proposal":
            self._show_task_proposal(prop)
        elif ptype == "event_proposal":
            self._show_event_proposal(prop)
        elif ptype == "vital_service_proposal":
            self._show_vital_service_proposal(prop)
        else:
            self._show_generic_proposal(prop)

        self._print(f"  {DIM}{prop.get('voluntary_note', '')}{RESET}")
        self._print("")

    def _show_resource_proposal(self, prop: Dict) -> None:
        self._print(f"  {GREEN}Offered:{RESET}  {prop.get('offered_joules_readable', prop.get('offered_joules', '?'))}")
        self._print(f"  {CYAN}Reason:{RESET}   {prop.get('reason', '—')}")
        self._print(f"  {CYAN}Impact:{RESET}   {prop.get('impact', '—')}")
        if prop.get("penalty_note"):
            self._print(f"  {YELLOW}Note:{RESET}     {prop['penalty_note']}")

    def _show_task_proposal(self, prop: Dict) -> None:
        self._print(f"  {GREEN}Task:{RESET}     {prop.get('task', '—')}")
        self._print(f"  {CYAN}Where:{RESET}    {prop.get('location', 'flexible')}")
        self._print(f"  {CYAN}Duration:{RESET} {prop.get('suggested_duration', 'flexible')}")
        self._print(f"  {CYAN}Impact:{RESET}   {prop.get('impact', '—')}")
        if prop.get("why_you"):
            self._print(f"  {CYAN}Why you:{RESET}  {prop['why_you']}")

    def _show_event_proposal(self, prop: Dict) -> None:
        self._print(f"  {GREEN}Event:{RESET}    {prop.get('event_name', '—')}")
        self._print(f"  {CYAN}Date:{RESET}     {prop.get('event_date', '—')}")
        contrib = prop.get("suggested_contribution", {})
        self._print(f"  {CYAN}Contribution:{RESET} {contrib.get('task','—')} ({contrib.get('duration','?')}) within {contrib.get('window','?')}")
        self._print(f"  {CYAN}Impact:{RESET}   {prop.get('impact', '—')}")

    def _show_vital_service_proposal(self, prop: Dict) -> None:
        self._print(f"  {GREEN}Task:{RESET}     {prop.get('task_name', '—')}")
        self._print(f"  {CYAN}Category:{RESET} {prop.get('category', '—')}  |  Urgency: {prop.get('urgency','?')}")
        self._print(f"  {CYAN}Where:{RESET}    {prop.get('location', 'flexible')}")
        self._print(f"  {CYAN}Duration:{RESET} {prop.get('suggested_duration', 'flexible')}")
        self._print(f"  {CYAN}Impact:{RESET}   {prop.get('impact', '—')}")
        if prop.get("why_you"):
            reasons = prop["why_you"] if isinstance(prop["why_you"], list) else [prop["why_you"]]
            self._print(f"  {CYAN}Why you:{RESET}  {'; '.join(reasons)}")
        self._print(f"  {DIM}Exit terms: {prop.get('exit_terms', '30 days notice, no penalty')}{RESET}")

    def _show_generic_proposal(self, prop: Dict) -> None:
        for key in ("task", "task_name", "offered_joules_readable", "description"):
            if prop.get(key):
                self._print(f"  {GREEN}Details:{RESET} {prop[key]}")
                break
        if prop.get("impact"):
            self._print(f"  {CYAN}Impact:{RESET}  {prop['impact']}")

    # ──────────────────────────────────────────────
    #  INPUT
    # ──────────────────────────────────────────────

    def get_user_response(self, proposal: Dict) -> Dict:
        """Collect a human response to a single proposal."""
        options = proposal.get("options", ["Accept", "Reject", "Negotiate", "Ignore"])
        self._print(f"{BOLD}What would you like to do?{RESET}")
        for i, opt in enumerate(options, 1):
            self._print(f"  {i}. {opt}")

        choice_str = input("Choose (number): ").strip()

        try:
            choice_idx = int(choice_str) - 1
            chosen = options[choice_idx] if 0 <= choice_idx < len(options) else "Ignore"
        except (ValueError, IndexError):
            chosen = "Ignore"

        response: Dict[str, Any] = {
            "proposal_id": proposal.get("id", "unknown"),
            "action": chosen.lower().replace(" ", "_"),
            "label": chosen
        }

        if "negotiate" in chosen.lower() or "alternative" in chosen.lower():
            counter = input("Your counter-proposal or preferred alternative: ").strip()
            response["counter_proposal"] = counter

        if "reject" in chosen.lower() or "decline" in chosen.lower():
            try:
                reason = input("Reason (optional — press Enter to skip): ").strip()
                if reason:
                    response["reason"] = reason
            except EOFError:
                pass

        return response

    def show_distribution_result(self, result: Dict) -> None:
        """Display the full result of a distribution cycle."""
        self._print(f"\n{BOLD}{GREEN}=== DISTRIBUTION CYCLE COMPLETE ==={RESET}")
        self._print(f"  Total available: {result.get('total_joules_available', 0):,.0f} J")
        self._print(f"  Total allocated: {result.get('total_joules_allocated', 0):,.0f} J")
        self._print(f"  Remaining:       {result.get('remaining_joules', 0):,.0f} J")
        self._print(f"  {DIM}{result.get('note','')}{RESET}\n")

    def show_conflict_resolution(self, resolution: Dict) -> None:
        """Display a conflict resolution in a calm, transparent way."""
        self._print(f"\n{BOLD}{YELLOW}=== CONFLICT RESOLUTION ==={RESET}")
        self._print(f"  Contest ID:    {resolution.get('contest_id','?')}")
        self._print(f"  Original reason: {resolution.get('original_reason','?')}")
        self._print(f"  Classified as: {resolution.get('classified_as','?')}")
        suggestion = resolution.get("new_suggestion", {})
        if suggestion.get("values"):
            self._print(f"  New suggestion: {json.dumps(suggestion['values'])}")
        for step in resolution.get("next_steps", []):
            self._print(f"  → {step}")
        self._print(f"  {DIM}{resolution.get('note','')}{RESET}\n")

    def show_memory_summary(self, summary: str) -> None:
        self._print(f"\n{DIM}{summary}{RESET}\n")

    # ──────────────────────────────────────────────
    #  UTILITY
    # ──────────────────────────────────────────────

    def _print(self, text: str) -> None:
        if not self.use_colour:
            # Strip ANSI codes if colour is disabled
            import re
            text = re.sub(r'\033\[[0-9;]*m', '', text)
        print(text)


if __name__ == "__main__":
    ui = HumanInterface()

    test_proposals = [
        {
            "id": "prop_001",
            "type": "resource_allocation",
            "person_id": "person_001",
            "module": "Core_System_Cerebrus",
            "offered_joules": 4500,
            "offered_joules_readable": "4.5 kJ",
            "reason": "Critical Axiom 07 deficit — highest priority",
            "impact": "Covers a significant portion of daily caloric needs (1,075 kcal equivalent)",
            "voluntary_note": "You may accept, reject, negotiate, or ignore — no penalty.",
            "options": ["Accept", "Reject", "Negotiate", "Ignore"]
        },
        {
            "id": "prop_002",
            "type": "task_proposal",
            "person_id": "person_001",
            "module": "Core_System_Cerebrus",
            "task": "Harvest — Zone 7 (3 volunteers needed)",
            "location": "Zone 7",
            "suggested_duration": "2 hours",
            "impact": "240 kg of fresh food for the community",
            "why_you": "You're 12 minutes from Zone 7 and have helped with agriculture before",
            "voluntary_note": "Completely voluntary. Decline freely.",
            "options": ["Accept", "Schedule for later", "Suggest alternative", "Decline"]
        }
    ]

    ui.show_proposals(test_proposals)

    for prop in test_proposals:
        response = ui.get_user_response(prop)
        print(f"\nResponse recorded: {json.dumps(response, indent=2)}")
