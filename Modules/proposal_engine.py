"""
proposal_engine.py
Gera propostas voluntárias personalizadas e amigáveis.
"""

from datetime import datetime
from Modules.thermodynamic_orchestrator import ThermodynamicOrchestrator
from typing import Dict, List


class ProposalEngine:
    def __init__(self, orchestrator: ThermodynamicOrchestrator):
        self.orchestrator = orchestrator

    def generate_proposals(self, resources: List[Dict], recipients: List[Dict]) -> List[Dict]:
        distribution = self.orchestrator.distribute(resources, recipients)

        proposals = []
        for person_id, alloc in distribution.get("allocation_proposals", {}).items():
            proposal = {
                "timestamp": datetime.now().isoformat(),
                "person_id": person_id,
                "type": "resource_allocation",
                "suggested_amount": alloc.get("allocated_joules", 0),
                "unit": "joules",
                "reason": alloc.get("reason", "To support community well-being according to Axiom 07"),
                "impact": f"Contributes to maintaining physical well-being (Axiom 07) for the community.",
                "voluntary_note": "This is a voluntary proposal. You can accept, reject, negotiate or ignore with no penalty.",
                "module": "Core_System_Cerebrus"
            }
            proposals.append(proposal)

        return proposals


# Teste rápido (opcional)
if __name__ == "__main__":
    print("ProposalEngine module loaded successfully.")
