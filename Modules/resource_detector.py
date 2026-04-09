"""
resource_detector.py
Core_System_Cerebrus - Resource Detector

Deteta necessidades, sobras, tarefas pendentes, lixo, energia, etc.
Pode receber dados de sensores, relatórios humanos ou simulações.
"""

from typing import Dict, List, Any
from datetime import datetime


class ResourceDetector:
    def __init__(self):
        self.current_state = {}

    def update_state(self, new_data: Dict):
        """Atualiza o estado atual do sistema."""
        self.current_state.update(new_data)
        self.current_state["last_update"] = datetime.now().isoformat()

    def detect_needs(self) -> List[Dict]:
        """Retorna lista de necessidades detetadas (o que falta)."""
        needs = []
        metrics = self.current_state.get("axiom07_metrics", {})

        # Exemplos de deteção
        if metrics.get("daily_calories", 2000) < 1800:
            needs.append({
                "type": "food",
                "priority": "high",
                "deficit": 1800 - metrics.get("daily_calories", 2000),
                "description": "Caloric deficit detected"
            })

        if metrics.get("water_liters", 18) < 15:
            needs.append({
                "type": "water",
                "priority": "high",
                "deficit": 15 - metrics.get("water_liters", 18)
            })

        # Tarefas pendentes (exemplo)
        if self.current_state.get("pending_tasks"):
            for task in self.current_state["pending_tasks"]:
                needs.append({"type": "task", "task": task})

        return needs

    def detect_surpluses(self) -> List[Dict]:
        """Retorna sobras (recursos em excesso)."""
        # Implementação futura mais completa
        return []


# Teste
if __name__ == "__main__":
    detector = ResourceDetector()
    detector.update_state({
        "axiom07_metrics": {"daily_calories": 1200, "water_liters": 10},
        "pending_tasks": ["Estufa maintenance", "Recycling sorting"]
    })
    print("Detected needs:", detector.detect_needs())
