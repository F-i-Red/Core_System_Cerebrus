"""
vital_service_matcher.py
Core_System_Cerebrus - Vital Service Matcher

Módulo especializado no Serviço Cívico Vital.
Faz matching voluntário entre pessoas e tarefas de maior escala ou permanência.
"""

from typing import Dict, List


class VitalServiceMatcher:
    def __init__(self):
        pass

    def generate_vital_proposals(self, person: Dict, available_tasks: List[Dict]) -> List[Dict]:
        """Gera propostas para o Serviço Cívico Vital."""
        proposals = []
        for task in available_tasks:
            proposal = {
                "module": "Serviço Cívico Vital",
                "person_id": person.get("id"),
                "task_id": task.get("id"),
                "task_name": task.get("name"),
                "suggested_duration": task.get("duration", "flexible"),
                "location": task.get("location"),
                "impact": task.get("impact", "Colmata lacunas críticas do sistema"),
                "voluntary_note": "100% voluntary. You choose duration and can leave anytime with 30 days notice.",
                "why_this_person": "Based on your skills/location/previous interests"
            }
            proposals.append(proposal)
        return proposals


# Teste
if __name__ == "__main__":
    matcher = VitalServiceMatcher()
    person = {"id": "p001", "skills": ["agriculture", "maintenance"]}
    tasks = [
        {"id": "t001", "name": "Estufa coordination", "duration": "6-24 months", "location": "Zone 7"}
    ]
    print(matcher.generate_vital_proposals(person, tasks))
