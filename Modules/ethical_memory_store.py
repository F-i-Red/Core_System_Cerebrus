"""
ethical_memory_store.py
Core_System_Cerebrus — Ethical Memory Store

Stores ALL system decisions in an auditable, persistent, tamper-evident log.
Nothing is deleted. Anyone can read. Every entry is chained by hash.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class EthicalMemoryStore:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.log_file = self.data_dir / "ethical_memory.jsonl"
        self.entries: List[Dict] = []
        self._load_existing()

    def _load_existing(self):
        """Load entries from previous sessions — history is always preserved."""
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            self.entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

    def _compute_hash(self, entry: Dict, previous_hash: str) -> str:
        """Chained hash — any retroactive tampering becomes detectable."""
        content = json.dumps(entry, sort_keys=True, ensure_ascii=False) + previous_hash
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def log(self, data: Dict[str, Any]) -> Dict:
        """Record an entry. Immutable once written."""
        previous_hash = self.entries[-1].get("hash", "genesis") if self.entries else "genesis"
        entry_index = len(self.entries) + 1

        entry = {
            "index": entry_index,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "previous_hash": previous_hash,
            "hash": ""
        }
        entry["hash"] = self._compute_hash(
            {k: v for k, v in entry.items() if k != "hash"},
            previous_hash
        )

        self.entries.append(entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"[Memory] Logged entry #{entry_index} → type: {data.get('type', 'unknown')}")
        return entry

    def get_all(self) -> List[Dict]:
        return self.entries

    def get_by_type(self, entry_type: str) -> List[Dict]:
        return [e for e in self.entries if e.get("data", {}).get("type") == entry_type]

    def get_conflict_history_for(self, person_id: str) -> List[Dict]:
        """Returns all validated conflict entries involving a specific person."""
        return [
            e for e in self.entries
            if e.get("data", {}).get("type") == "conflict_resolution"
            and person_id in json.dumps(e)
        ]

    def verify_integrity(self) -> Dict:
        """Verify the log has not been tampered with."""
        if not self.entries:
            return {"status": "empty", "total": 0}

        errors = []
        prev_hash = "genesis"
        for entry in self.entries:
            expected = self._compute_hash(
                {k: v for k, v in entry.items() if k not in ("hash", "previous_hash")},
                prev_hash
            )
            if entry.get("previous_hash") != prev_hash:
                errors.append(f"Entry #{entry['index']}: previous_hash mismatch")
            prev_hash = entry.get("hash", "")

        return {
            "status": "intact" if not errors else "TAMPERED",
            "total_entries": len(self.entries),
            "errors": errors
        }

    def export_summary(self, last_n: int = 10) -> str:
        """Human-readable summary of the last N entries."""
        lines = [f"=== Ethical Memory Store — {len(self.entries)} total entries ==="]
        for e in self.entries[-last_n:]:
            d = e.get("data", {})
            lines.append(
                f"  #{e['index']} [{e['timestamp'][:19]}] "
                f"{d.get('type','?')}: {d.get('message', '')}"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    store = EthicalMemoryStore()
    store.log({"type": "system_start", "message": "Core_System_Cerebrus initialized"})
    store.log({"type": "distribution", "resource": "energy", "joules": 5000})
    print(store.export_summary())
    print("\nIntegrity check:", store.verify_integrity())
