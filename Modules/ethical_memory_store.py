"""
ethical_memory_store.py
Core_System_Cerebrus - Ethical Memory Store

Armazena todas as decisões, propostas, aceitações, recusas e resoluções de forma imutável.
Funciona como um ledger transparente e offline-first.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class EthicalMemoryStore:
    def __init__(self, storage_path: str = "data/ethical_memory.jsonl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.entries = self._load_all()

    def _load_all(self) -> list:
        if not os.path.exists(self.storage_path):
            return []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def log(self, entry: Dict[str, Any]) -> None:
        """Regista uma entrada de forma imutável (append-only)."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "entry_id": len(self.entries) + 1,
            **entry
        }
        self.entries.append(record)

        # Append-only write
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"[Memory] Logged entry {record['entry_id']} → {entry.get('type', 'unknown')}")

    def get_history(self, limit: int = 100) -> list:
        return self.entries[-limit:]

    def search_by_type(self, entry_type: str) -> list:
        return [e for e in self.entries if e.get("type") == entry_type]


# Teste simples
if __name__ == "__main__":
    memory = EthicalMemoryStore()
    memory.log({"type": "system_start", "message": "Core_System_Cerebrus initialized"})
    print("Memory ready. Total entries:", len(memory.get_history()))
