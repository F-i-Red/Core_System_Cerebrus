"""
proposal_engine.py
Core_System_Cerebrus - Proposal Engine

Gera propostas voluntárias personalizadas para humanos.
Nunca força — apenas sugere de forma clara, útil e atraente.
"""

from datetime import datetime
from typing import Dict, List, Any
from Modules.thermodynamic_orchestrator import ThermodynamicOrchestrator


class ProposalEngine:
    def __init__(self, orchestrator: ThermodynamicOrchestrator):
        self.orchestrator = orchestrator

    def generate_proposals(self, resources: List[Dict], recipients: List[Dict]) -> List[Dict]:
        """
        Gera propostas voluntárias baseadas na distribuição termodinâmica.
        """
        distribution = self.orchestrator.distribute(resources, recipients)

        proposals = []
        for person_id, alloc in distribution.get("allocation_proposals", {}).items():
            proposal = {
                "timestamp": datetime.now().isoformat(),
                "person_id": person_id,
                "type": "resource_contribution" if "joules" in str(resources) else "task",
                "suggested_amount": alloc.get("allocated_joules"),
                "reason": alloc.get("reason", "To support community well-being (Axiom 07)"),
                "duration": "flexible (you choose)",
                "voluntary_note": "You can accept, reject, negotiate or propose alternative. No penalty.",
                "impact": f"Helps maintain real physical well-being for the community."
            }
            proposals.append(proposal)

        return proposals

    def generate_vital_service_proposal(self, person: Dict, task: Dict) -> Dict:
        """Gera proposta para o Serviço Cívico Vital (mais estruturada)."""
        return {
            "timestamp": datetime.now().isoformat(),
            "person_id": person.get("id"),
            "module": "Serviço Cívico Vital",
            "task": task.get("name"),
            "suggested_duration": task.get("duration", "flexible"),
            "location": task.get("location"),
            "impact": task.get("impact", "Helps close critical gaps"),
            "note": "Completely voluntary. You decide when, how long, and if you want to participate."
        }


# ====================== EXEMPLO ======================
if __name__ == "__main__":
    # Placeholders
    class DummyMemory: 
        def log(self, data): pass
    class DummyGrammar: 
        def resolve(self, c, m): return {}

    orchestrator = ThermodynamicOrchestrator(DummyMemory(), DummyGrammar())
    engine = ProposalEngine(orchestrator)

    resources = [{"id": "energy_1", "joules": 8000}]
    recipients = [
        {"id": "person_001", "axiom07_metrics": {"daily_calories": 1300}},
        {"id": "person_002", "axiom07_metrics": {"daily_calories": 2200}}
    ]

    proposals = engine.generate_proposals(resources, recipients)
    for p in proposals:
        print(p)
