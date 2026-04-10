"""
cerebrus_core.py  ← Ficheiro principal
"""

import sys
import os

# Adiciona a pasta Modules ao path (importante no Windows)
sys.path.append(os.path.join(os.path.dirname(__file__), "Modules"))

from ethical_memory_store import EthicalMemoryStore
from resource_detector import ResourceDetector
from thermodynamic_orchestrator import ThermodynamicOrchestrator
from proposal_engine import ProposalEngine
from conflict_grammar import ConflictGrammar
from vital_service_matcher import VitalServiceMatcher
from human_interface import HumanInterface


class CerebrusCore:
    def __init__(self):
        self.memory = EthicalMemoryStore()
        self.conflict_grammar = ConflictGrammar()
        self.orchestrator = ThermodynamicOrchestrator(self.memory, self.conflict_grammar)
        self.proposal_engine = ProposalEngine(self.orchestrator)
        self.detector = ResourceDetector()
        self.vital_matcher = VitalServiceMatcher()
        self.interface = HumanInterface()

        self.memory.log({"type": "system_start", "message": "Core_System_Cerebrus initialized successfully"})

    def run_cycle(self):
        print("\n=== Core_System_Cerebrus Cycle Started ===\n")

        self.detector.update_state({
            "axiom07_metrics": {"daily_calories": 1450, "water_liters": 12}
        })

        resources = [{"id": "solar_batch_001", "joules": 12000, "type": "energy"}]
        recipients = [{"id": "person_001", "axiom07_metrics": {"daily_calories": 1450}}]

        proposals = self.proposal_engine.generate_proposals(resources, recipients)

        self.interface.show_proposals(proposals)

        for prop in proposals:
            response = self.interface.get_user_response(prop)
            self.memory.log({"type": "human_response", "response": response})

        print("\n=== Cycle completed. All actions logged in Ethical Memory Store. ===\n")


if __name__ == "__main__":
    core = CerebrusCore()
    core.run_cycle()
