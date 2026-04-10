"""
vital_service_matcher.py
Core_System_Cerebrus — Vital Civic Service Matcher

Handles voluntary matching for longer-term or critical tasks.
Entry can happen at any age, any time. Exit is always possible with 30 days notice.
The system entices — it never compels.
"""

from datetime import datetime
from typing import Dict, List, Optional


# Task categories and their characteristics
TASK_CATEGORIES = {
    "emergency":        {"typical_duration": "days to weeks",   "urgency": "critical"},
    "infrastructure":   {"typical_duration": "months to years",  "urgency": "high"},
    "care":             {"typical_duration": "flexible",         "urgency": "medium"},
    "education":        {"typical_duration": "flexible",         "urgency": "medium"},
    "environment":      {"typical_duration": "weeks to months",  "urgency": "medium"},
    "logistics":        {"typical_duration": "flexible",         "urgency": "low"},
    "maintenance":      {"typical_duration": "flexible",         "urgency": "low"},
}


class VitalServiceMatcher:
    def __init__(self):
        self.active_assignments: List[Dict] = []

    def find_matches(self, person: Dict, available_tasks: List[Dict]) -> List[Dict]:
        """
        Find suitable Vital Civic Service tasks for a person.
        Ranks by compatibility (skills, location, interests, availability).
        Returns a list of voluntary proposals — best matches first.
        """
        proposals = []

        for task in available_tasks:
            score, reasons = self._compatibility_score(person, task)
            if score > 0:
                proposals.append(self._build_proposal(person, task, score, reasons))

        # Best match first
        proposals.sort(key=lambda p: p["match_score"], reverse=True)
        return proposals

    def register_entry(self, person_id: str, task_id: str, commitment: Dict) -> Dict:
        """Register a person's voluntary decision to join a task."""
        assignment = {
            "id": f"vcs_{person_id}_{task_id}_{datetime.now().strftime('%Y%m%d')}",
            "timestamp": datetime.now().isoformat(),
            "person_id": person_id,
            "task_id": task_id,
            "start_date": commitment.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "expected_duration": commitment.get("duration", "open"),
            "mode": commitment.get("mode", "full-time"),  # full-time / part-time / micro
            "exit_terms": "30 days notice at any time, no penalty, no explanation required",
            "status": "active"
        }
        self.active_assignments.append(assignment)
        return assignment

    def register_exit(self, person_id: str, task_id: str, reason: Optional[str] = None) -> Dict:
        """Register a voluntary exit. No penalty. Logged with respect."""
        exit_record = {
            "timestamp": datetime.now().isoformat(),
            "type": "vital_service_exit",
            "person_id": person_id,
            "task_id": task_id,
            "reason": reason or "Not provided — not required",
            "note": "Exit is unconditional. Thank you for the time contributed."
        }

        for a in self.active_assignments:
            if a["person_id"] == person_id and a["task_id"] == task_id:
                a["status"] = "completed"
                a["exit_timestamp"] = exit_record["timestamp"]

        return exit_record

    def micro_task_proposal(self, person: Dict, task: Dict) -> Dict:
        """
        Generate a micro-task proposal (15 min to 2 hours).
        For spontaneous, in-the-moment contributions.
        """
        return {
            "id": f"micro_{person.get('id','?')}_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "micro_task",
            "person_id": person.get("id"),
            "task_id": task.get("id"),
            "task_name": task.get("name"),
            "duration": task.get("duration", "15–60 minutes"),
            "location": task.get("location"),
            "proximity_note": task.get("proximity_note", "You're nearby"),
            "impact": task.get("impact", "Direct community benefit"),
            "voluntary_note": "One-time, right now, no commitment. Accept only if you feel like it.",
            "options": ["I'm in", "Not now", "Maybe later — remind me"]
        }

    # ──────────────────────────────────────────────
    #  INTERNAL SCORING
    # ──────────────────────────────────────────────

    def _compatibility_score(self, person: Dict, task: Dict) -> tuple:
        score = 0
        reasons = []

        # Skill match
        person_skills = set(person.get("skills", []))
        task_skills = set(task.get("required_skills", []))
        matched_skills = person_skills & task_skills
        if matched_skills:
            score += len(matched_skills) * 30
            reasons.append(f"Skill match: {', '.join(matched_skills)}")

        # Location match
        if task.get("location") and task["location"] == person.get("zone"):
            score += 20
            reasons.append(f"Located in your zone ({task['location']})")

        # Interests match
        person_interests = set(person.get("interests", []))
        task_category = task.get("category", "")
        if task_category in person_interests:
            score += 25
            reasons.append(f"Matches your interest in {task_category}")

        # Availability match
        task_duration = task.get("duration_type", "flexible")
        person_availability = person.get("availability", "flexible")
        if task_duration == "micro" and person_availability in ("micro", "flexible"):
            score += 15
            reasons.append("Fits your availability (short task)")
        elif task_duration == "long-term" and person_availability in ("long-term", "full-time"):
            score += 15
            reasons.append("Fits your availability (long-term commitment)")

        # Past contributions
        past = person.get("past_contributions", [])
        if any(task_category in str(p) for p in past):
            score += 10
            reasons.append("You've contributed to similar tasks before")

        return score, reasons

    def _build_proposal(self, person: Dict, task: Dict, score: int, reasons: List[str]) -> Dict:
        category = task.get("category", "general")
        cat_info = TASK_CATEGORIES.get(category, {"typical_duration": "flexible", "urgency": "medium"})

        return {
            "id": f"vcs_prop_{person.get('id','?')}_{task.get('id','?')}",
            "timestamp": datetime.now().isoformat(),
            "type": "vital_service_proposal",
            "module": "Vital Civic Service",
            "person_id": person.get("id"),
            "task_id": task.get("id"),
            "task_name": task.get("name"),
            "category": category,
            "urgency": cat_info["urgency"],
            "location": task.get("location"),
            "suggested_duration": task.get("duration", cat_info["typical_duration"]),
            "slots_available": task.get("slots_needed", 1),
            "match_score": score,
            "why_you": reasons,
            "impact": task.get("impact", "Closes a critical gap in the system"),
            "commitment_options": [
                "Full participation (as described above)",
                "Part-time participation (negotiate duration)",
                "Micro-contribution only (1–2 hours, no ongoing commitment)"
            ],
            "exit_terms": "30 days notice at any time. No penalty. No explanation required.",
            "voluntary_note": (
                "This is a Vital Civic Service proposal. "
                "You are never obligated to accept. "
                "The system is asking because it believes you'd be a great fit."
            ),
            "options": ["Accept", "Negotiate terms", "Offer micro-task only", "Decline"]
        }


if __name__ == "__main__":
    matcher = VitalServiceMatcher()

    person = {
        "id": "person_042",
        "skills": ["agriculture", "maintenance", "teaching"],
        "interests": ["environment", "education"],
        "zone": "Zone 7",
        "availability": "flexible",
        "past_contributions": ["greenhouse_repair_2025", "soil_prep_2026"]
    }

    tasks = [
        {
            "id": "t001",
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
            "id": "t002",
            "name": "Basic skills workshop — Zone 3",
            "category": "education",
            "required_skills": ["teaching"],
            "location": "Zone 3",
            "duration": "4 weeks",
            "duration_type": "flexible",
            "slots_needed": 1,
            "impact": "Upskills 20 community members"
        },
        {
            "id": "t003",
            "name": "Recycling centre sorting — Zone 7",
            "category": "maintenance",
            "required_skills": [],
            "location": "Zone 7",
            "duration": "2 hours",
            "duration_type": "micro",
            "slots_needed": 5,
            "impact": "Keeps the recycling loop closed"
        }
    ]

    proposals = matcher.find_matches(person, tasks)
    import json
    for p in proposals:
        print(f"\n[Match score: {p['match_score']}] {p['task_name']}")
        print(f"  Why you: {'; '.join(p['why_you'])}")
        print(f"  Impact:  {p['impact']}")
