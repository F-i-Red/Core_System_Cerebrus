# Core_System_Cerebrus

**Thermodynamic executive engine of the Shared Ethical Memory (SEM 2063)**

Core_System_Cerebrus is the central orchestrator responsible for managing resource flows, logistics, human needs, and voluntary contributions in a transparent, post-scarcity civilization.

It works as the "brain" of the SEM framework:
- Detects real needs and surpluses
- Optimizes distribution based on joules and **Axiom 07** (measurable physical well-being)
- Generates **voluntary proposals** only — never commands
- Includes the **Serviço Cívico Vital** module for larger or longer-term voluntary contributions
- Resolves conflicts through Conflict Grammar
- Logs everything immutably in the Ethical Memory Store

**Core principles**: Offline-first, fully auditable, anti-capture, human-centric, and 100% voluntary.

### Project Structure
Core_System_Cerebrus/
├── cerebrus_core.py
├── requirements.txt
├── README.md
├── data/                     # Auto-created (ethical_memory.jsonl)
└── Modules/
├── ethical_memory_store.py
├── resource_detector.py
├── thermodynamic_orchestrator.py
├── proposal_engine.py
├── conflict_grammar.py
├── vital_service_matcher.py
└── human_interface.py


### How to Run

```bash
# 1. Clone the repo
git clone https://github.com/F-i-Red/Core_System_Cerebrus.git
cd Core_System_Cerebrus

# 2. Install dependencies (optional for basic use)
pip install -r requirements.txt

# 3. Run the core system
python cerebrus_core.py
```
### Current Status

Fully functional basic cycle (detection → orchestration → proposals → human response → logging)
All modules are modular and extensible
Ready for simulation and small real-world pilots

### Future Improvements

## Web dashboard

Persistent state (Modules/state_manager.py) — The world state now lives in data/world_state.json. Every time you run cerebrus_core.py, it loads from where you left off. Stocks replenish each cycle (solar energy generated, water collected, food produced) and deplete (baseline consumption). If you accept more proposals, the Axiom 07 metrics improve — calories go up, water improves, temperature rises. Run it 10 times accepting everything and you'll see the community recover. Run it ignoring everything and it degrades.
Dashboard (dashboard.py) — Five pages: World State overview, Axiom 07 metrics with progress bars, Stocks with per-cycle flow rates, the full Memory Log with hash verification, and a Simulate Cycle page where you can advance state directly from the browser without touching the terminal.


To launch the dashboard, install Streamlit once and run:
pip install streamlit
streamlit run dashboard.py
It opens in your browser automatically at localhost:8501.

Web dashboard (Streamlit/Gradio)
Integration with joule_sim from Shared-Ethical-Memory
Sensor/IoT data input
More sophisticated Axiom 07 metrics
