"""
thermodynamic_orchestrator.py
Core_System_Cerebrus - Thermodynamic Executive Engine (SEM 2063)

Orquestrador responsável por otimizar a distribuição de recursos
com base em eficiência termodinâmica (joules) e Axiom 07 (bem-estar físico real).
Gera apenas propostas voluntárias. Tudo é transparente e auditável.
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any

# Assumindo que estes módulos existem no projeto
from ethical_memory_store import EthicalMemoryStore
from conflict_grammar import ConflictGrammar


class ThermodynamicOrchestrator:
    def __init__(self, memory_store: EthicalMemoryStore, conflict_grammar: ConflictGrammar):
        self.memory = memory_store
        self.conflict_grammar = conflict_grammar
        self.penalty_period_days = 60  # penalização temporária para agressores

    def calculate_need_score(self, entity: Dict) -> float:
        """
        Calcula Need_Score baseado em défices de Axiom 07.
        Quanto maior o défice, maior a prioridade.
        """
        base = 100.0
        deficit = 0.0

        # Exemplos de métricas Axiom 07 (podes expandir)
        metrics = entity.get("axiom07_metrics", {})
        deficit += max(0, 2000 - metrics.get("daily_calories", 2000)) * 0.05
        deficit += max(0, 18 - metrics.get("water_liters", 18)) * 2.0
        deficit += max(0, 20 - metrics.get("comfort_temperature", 20)) * 1.5
        deficit += max(0, 7 - metrics.get("sleep_hours", 7)) * 3.0

        # Agressores têm penalização temporária
        if self.is_aggressor(entity):
            deficit *= 0.3

        return base + deficit

    def is_aggressor(self, entity: Dict) -> bool:
        """Verifica se existe registo recente de agressão validada."""
        history = entity.get("conflict_history", [])
        if not history:
            return False
        last = history[-1]
        if last.get("type") in ["violence", "sabotage", "coercion"]:
            days_ago = (datetime.now() - datetime.fromisoformat(last["timestamp"])).days
            return days_ago < self.penalty_period_days
        return False

    def distribute(self, resources: List[Dict], recipients: List[Dict]) -> Dict:
        """
        Distribui recursos de forma termodinâmica otimizada.
        Retorna propostas voluntárias + explicação transparente.
        """
        if not resources or not recipients:
            return {"status": "error", "message": "No resources or recipients provided"}

        # Passo 1: Calcular eficiência termodinâmica base (joules)
        # Aqui simplificado — podes integrar com joule_sim.py depois
        total_joules = sum(r.get("joules", 0) for r in resources)

        # Passo 2: Calcular Need_Score para cada recipient
        for recipient in recipients:
            recipient["need_score"] = self.calculate_need_score(recipient)

        # Ordenar por Need_Score (maior primeiro)
        recipients.sort(key=lambda x: x["need_score"], reverse=True)

        allocation = {}
        remaining = total_joules

        for recipient in recipients:
            if remaining <= 0:
                break

            requested = recipient.get("requested_joules", float('inf'))
            need_based = (recipient["need_score"] / sum(r["need_score"] for r in recipients)) * total_joules

            amount = min(requested, need_based, remaining)

            allocation[recipient["id"]] = {
                "allocated_joules": round(amount, 2),
                "reason": "High need score (Axiom 07 priority)" if recipient["need_score"] > 150 else "Proportional distribution"
            }
            remaining -= amount

        # Passo 3: Se ainda houver empate forte, aplicar divisão equitativa ou random mínima
        if remaining > 0 and len(recipients) > 0:
            extra_per_person = remaining / len(recipients)
            for rec_id in allocation:
                allocation[rec_id]["allocated_joules"] += round(extra_per_person, 2)
                allocation[rec_id]["reason"] += " + equitable share"

        # Registar no Ethical Memory Store
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "type": "resource_distribution",
            "resources": resources,
            "allocation": allocation,
            "total_joules_allocated": total_joules - remaining
        }
        self.memory.log(decision_log)

        return {
            "status": "success",
            "allocation_proposals": allocation,
            "remaining_joules": round(remaining, 2),
            "note": "All proposals are voluntary. Humans can accept, reject or negotiate via Conflict Grammar."
        }

    def resolve_conflict(self, contestation: Dict) -> Dict:
        """Ativa o Conflict Grammar quando alguém contesta a proposta."""
        resolution = self.conflict_grammar.resolve(contestation, self.memory)
        self.memory.log(resolution)
        return resolution


# ====================== EXEMPLO DE USO ======================

if __name__ == "__main__":
    # Simulação simples
    memory = EthicalMemoryStore()          # placeholder
    grammar = ConflictGrammar()            # placeholder

    orchestrator = ThermodynamicOrchestrator(memory, grammar)

    resources = [
        {"id": "solar_batch_001", "joules": 5000, "type": "energy"}
    ]

    recipients = [
        {"id": "person_001", "axiom07_metrics": {"daily_calories": 1400, "water_liters": 12}, "requested_joules": 2000, "conflict_history": []},
        {"id": "person_002", "axiom07_metrics": {"daily_calories": 2100, "water_liters": 20}, "requested_joules": 1500, "conflict_history": []},
        {"id": "person_003", "axiom07_metrics": {"daily_calories": 900, "water_liters": 8}, "requested_joules": 2500, "conflict_history": [{"type": "violence", "timestamp": "2026-03-01T00:00:00"}]},
    ]

    result = orchestrator.distribute(resources, recipients)
    print(json.dumps(result, indent=2))
