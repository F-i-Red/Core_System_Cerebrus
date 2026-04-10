"""
cerebrus_core.py  ← Ficheiro principal (na raiz do repo)
Core_System_Cerebrus - Main Executive Core
"""

from Modules.ethical_memory_store import EthicalMemoryStore
from Modules.resource_detector import ResourceDetector
from Modules.thermodynamic_orchestrator import ThermodynamicOrchestrator
from Modules.proposal_engine import ProposalEngine
from Modules.conflict_grammar import ConflictGrammar
from Modules.vital_service_matcher import VitalServiceMatcher
from Modules.human_interface import HumanInterface


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
        """Um ciclo completo: deteção → orquestração → propostas → resposta humana."""
        print("\n=== Core_System_Cerebrus Cycle Started ===\n")

        # 1. Detetar necessidades
        self.detector.update_state({
            "axiom07_metrics": {"daily_calories": 1450, "water_liters": 12}
        })

        resources = [{"id": "solar_batch_001", "joules": 12000, "type": "energy"}]
        recipients = [
            {"id": "person_001", "axiom07_metrics": {"daily_calories": 1450, "water_liters": 12}}
        ]

        # 2. Gerar propostas
        proposals = self.proposal_engine.generate_proposals(resources, recipients)

        # 3. Mostrar ao humano
        self.interface.show_proposals(proposals)

        # 4. Receber respostas (interação simples)
        for prop in proposals:
            response = self.interface.get_user_response(prop)
            self.memory.log({"type": "human_response", "proposal": prop, "response": response})

        print("\n=== Cycle completed. All actions logged in Ethical Memory Store. ===\n")


if __name__ == "__main__":
    core = CerebrusCore()
    core.run_cycle()
