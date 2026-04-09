"""
cerebrus_core.py
Core_System_Cerebrus - Main Executive Core

Junta todos os módulos num sistema coeso.
"""

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
        """Um ciclo completo de deteção → proposta → interação."""
        print("\n=== Core_System_Cerebrus Cycle ===")

        # 1. Detetar
        self.detector.update_state({"axiom07_metrics": {"daily_calories": 1400}})
        needs = self.detector.detect_needs()

        # 2. Orquestrar + Gerar propostas
        resources = [{"id": "solar_001", "joules": 10000}]
        recipients = [{"id": "p001", "axiom07_metrics": {"daily_calories": 1400}}]

        proposals = self.proposal_engine.generate_proposals(resources, recipients)

        # 3. Mostrar ao humano
        self.interface.show_proposals(proposals)

        # 4. Obter resposta (simulada por agora)
        for prop in proposals:
            response = self.interface.get_user_response(prop)
            self.memory.log({"type": "human_response", "response": response})

        print("Cycle completed. All logged in Ethical Memory Store.")


# ====================== RUN ======================
if __name__ == "__main__":
    core = CerebrusCore()
    core.run_cycle()
