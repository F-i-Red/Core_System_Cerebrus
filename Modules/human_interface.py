"""
human_interface.py
Core_System_Cerebrus - Human Interface

Mostra propostas ao humano e recebe respostas (aceitar, recusar, negociar).
"""

from typing import Dict, List
import json


class HumanInterface:
    def show_proposals(self, proposals: List[Dict]) -> None:
        print("\n=== PROPOSTAS VOLUNTÁRIAS ===")
        for i, prop in enumerate(proposals, 1):
            print(f"\n{i}. {prop.get('module', 'Proposal')}")
            print(f"   Task: {prop.get('task_name') or prop.get('suggested_amount')}")
            print(f"   Reason: {prop.get('reason') or prop.get('impact')}")
            print(f"   Note: {prop.get('voluntary_note', 'Voluntary')}")
            print("-" * 50)

    def get_user_response(self, proposal: Dict) -> Dict:
        """Simula interação humana (em produção pode ser GUI ou API)."""
        print(f"\nWhat do you want to do with this proposal?")
        print("1. Accept    2. Reject    3. Negotiate    4. Ignore")
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            return {"action": "accept", "proposal": proposal}
        elif choice == "2":
            return {"action": "reject", "reason": input("Reason (optional): ")}
        elif choice == "3":
            return {"action": "negotiate", "new_suggestion": input("Your counter-proposal: ")}
        else:
            return {"action": "ignore"}


# Teste rápido
if __name__ == "__main__":
    interface = HumanInterface()
    test_prop = {"module": "Serviço Cívico Vital", "task_name": "Help with recycling"}
    interface.show_proposals([test_prop])
    response = interface.get_user_response(test_prop)
    print("Response:", response)
