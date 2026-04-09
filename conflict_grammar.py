"""
conflict_grammar.py
Core_System_Cerebrus - Conflict Grammar Module

Resolve conflitos e contestações de forma transparente, seguindo os princípios
do Shared Ethical Memory (pluralismo ativo, humildade sistémica e Axiom 00).
"""

import json
from datetime import datetime
from typing import Dict, Any


class ConflictGrammar:
    def __init__(self):
        self.resolution_history = []

    def resolve(self, contestation: Dict, memory_store: Any) -> Dict:
        """
        Resolve uma contestação à distribuição de recursos.
        Retorna uma proposta de resolução justa e transparente.
        """
        contestation_id = contestation.get("id", "unknown")
        reason = contestation.get("reason", "No reason provided")
        proposed_allocation = contestation.get("proposed_allocation", {})

        # Lógica simples mas expansível
        resolution = {
            "timestamp": datetime.now().isoformat(),
            "contestation_id": contestation_id,
            "status": "resolved",
            "original_reason": reason,
            "decision": "Adjusted allocation after review",
            "new_suggestion": self._suggest_fair_adjustment(proposed_allocation),
            "note": "Human can accept, reject or escalate to Community Assembly."
        }

        self.resolution_history.append(resolution)

        # Regista no Ethical Memory Store
        if hasattr(memory_store, "log"):
            memory_store.log({
                "type": "conflict_resolution",
                "contestation": contestation,
                "resolution": resolution
            })

        return resolution

    def _suggest_fair_adjustment(self, allocation: Dict) -> Dict:
        """Sugere um ajuste simples (podes melhorar mais tarde)."""
        if not allocation:
            return {"message": "No specific adjustment needed"}
        # Exemplo: redistribui um pouco para aumentar equidade
        adjusted = {}
        for key, value in allocation.items():
            adjusted[key] = round(value * 0.95, 2) if isinstance(value, (int, float)) else value
        return adjusted

    def get_history(self) -> list:
        return self.resolution_history


# ====================== EXEMPLO ======================
if __name__ == "__main__":
    grammar = ConflictGrammar()
    test_contestation = {
        "id": "contest_001",
        "reason": "I believe I have higher need than person_003",
        "proposed_allocation": {"person_001": 1800, "person_003": 1200}
    }
    # memory placeholder
    class DummyMemory:
        def log(self, data): print("Logged to memory:", json.dumps(data, indent=2))
    
    result = grammar.resolve(test_contestation, DummyMemory())
    print(json.dumps(result, indent=2))
