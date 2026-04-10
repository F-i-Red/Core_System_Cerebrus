"""
dashboard.py
Core_System_Cerebrus — Web Dashboard

Run with:  streamlit run dashboard.py
Install:   pip install streamlit
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Modules"))

import streamlit as st
from state_manager    import StateManager
from ethical_memory_store import EthicalMemoryStore

# ──────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Core_System_Cerebrus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
#  LOAD STATE
# ──────────────────────────────────────────────

@st.cache_resource
def load_state_manager():
    return StateManager()

@st.cache_resource
def load_memory():
    return EthicalMemoryStore()

sm     = load_state_manager()
memory = load_memory()

# ──────────────────────────────────────────────
#  AXIOM 07 MINIMUMS (for progress bars)
# ──────────────────────────────────────────────

AXIOM07_MIN = {"daily_calories": 2100, "water_liters": 2.5, "temp_celsius": 18.0, "sleep_hours": 7.0}
AXIOM07_MAX = {"daily_calories": 2800, "water_liters": 4.0, "temp_celsius": 24.0, "sleep_hours": 9.0}
STOCK_MAX   = {"food_kg": 200, "water_liters": 1000, "energy_joules": 500_000, "recycling_kg": 100}

# ──────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────

with st.sidebar:
    st.title("🧠 Core_System_Cerebrus")
    st.caption("Thermodynamic Civic Operating System")
    st.divider()

    cycle = sm.get_cycle()
    st.metric("Current Cycle", f"#{cycle}" if cycle > 0 else "Not started")
    last = sm.state["meta"].get("last_updated", "")
    if last:
        st.caption(f"Last updated: {last[:19]}")

    st.divider()
    page = st.radio(
        "Navigate",
        ["🌍 World State", "📊 Axiom 07", "📦 Stocks", "🗂️ Memory Log", "⚙️ Simulate Cycle"],
        label_visibility="collapsed"
    )

    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    if st.button("⚠️ Reset to defaults", use_container_width=True):
        sm.reset_to_default()
        st.cache_resource.clear()
        st.rerun()

# ──────────────────────────────────────────────
#  PAGE: WORLD STATE
# ──────────────────────────────────────────────

if page == "🌍 World State":
    st.title("🌍 World State Overview")

    stocks  = sm.get_stocks()
    axiom07 = sm.get_axiom07()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cal = axiom07.get("daily_calories", 0)
        delta = round(cal - AXIOM07_MIN["daily_calories"])
        st.metric("Daily Calories", f"{cal:.0f} kcal", delta=f"{delta:+.0f} vs minimum",
                  delta_color="normal" if delta >= 0 else "inverse")
    with col2:
        water = axiom07.get("water_liters", 0)
        delta = round(water - AXIOM07_MIN["water_liters"], 1)
        st.metric("Water / Day", f"{water:.1f} L", delta=f"{delta:+.1f} vs minimum",
                  delta_color="normal" if delta >= 0 else "inverse")
    with col3:
        temp = axiom07.get("temp_celsius", 0)
        delta = round(temp - AXIOM07_MIN["temp_celsius"], 1)
        st.metric("Temperature", f"{temp:.1f} °C", delta=f"{delta:+.1f} vs minimum",
                  delta_color="normal" if delta >= 0 else "inverse")
    with col4:
        food = stocks.get("food_kg", 0)
        st.metric("Food Stock", f"{food:.1f} kg",
                  delta="Critical" if food < 30 else "OK",
                  delta_color="inverse" if food < 30 else "normal")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("⚡ Energy")
        ej = stocks.get("energy_joules", 0)
        st.progress(min(1.0, ej / STOCK_MAX["energy_joules"]))
        st.caption(f"{ej/1000:.1f} kJ available")

        st.subheader("💧 Water Stock")
        wl = stocks.get("water_liters", 0)
        st.progress(min(1.0, wl / STOCK_MAX["water_liters"]))
        st.caption(f"{wl:.0f} L in reserve")

    with col_b:
        st.subheader("🌿 Pending Tasks")
        tasks = sm.state.get("pending_tasks", [])
        if tasks:
            for task in tasks:
                name = task.get("name", task) if isinstance(task, dict) else str(task)
                sev  = task.get("severity", "medium") if isinstance(task, dict) else "medium"
                icon = "🔴" if sev == "critical" else "🟠" if sev == "high" else "🟡"
                st.write(f"{icon} {name}")
        else:
            st.success("No pending tasks.")

        st.subheader("🙋 Volunteer Gaps")
        gaps = sm.state.get("volunteer_gaps", [])
        if gaps:
            for gap in gaps:
                urgent = "🔴" if gap.get("urgent") else "🟡"
                st.write(f"{urgent} **{gap.get('name')}** — {gap.get('slots_needed')} slot(s) needed in {gap.get('location','?')}")
        else:
            st.success("No volunteer gaps.")

# ──────────────────────────────────────────────
#  PAGE: AXIOM 07
# ──────────────────────────────────────────────

elif page == "📊 Axiom 07":
    st.title("📊 Axiom 07 — Physical Well-being")
    st.caption("These are hard constraints. No resource allocation is valid if it violates these minimums.")

    axiom07 = sm.get_axiom07()
    metrics = [
        ("🍎 Daily Calories",   "daily_calories",  "kcal/day",  2100, 2800),
        ("💧 Water per Day",    "water_liters",     "L/day",     2.5,  4.0),
        ("🌡️ Temperature",     "temp_celsius",     "°C",        18.0, 24.0),
        ("😴 Sleep Hours",      "sleep_hours",      "h/night",   7.0,  9.0),
    ]

    for label, key, unit, minimum, maximum in metrics:
        value = axiom07.get(key, 0)
        pct   = min(1.0, max(0.0, value / maximum))
        met   = value >= minimum

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{label}**")
            colour = "green" if met else "red"
            st.progress(pct)
            st.caption(
                f"Current: {value:.1f} {unit}  |  "
                f"Minimum: {minimum} {unit}  |  "
                f"Status: {'✅ Met' if met else '❌ BELOW MINIMUM'}"
            )
        with col2:
            st.metric(label=" ", value=f"{value:.1f} {unit}",
                      delta=f"{value - minimum:+.1f}",
                      delta_color="normal" if met else "inverse",
                      label_visibility="hidden")
        st.write("")

    st.divider()
    st.info(
        "Axiom 07 metrics improve each cycle when resource proposals are accepted. "
        "Run more cycles and accept proposals to see the numbers rise."
    )

# ──────────────────────────────────────────────
#  PAGE: STOCKS
# ──────────────────────────────────────────────

elif page == "📦 Stocks":
    st.title("📦 Resource Stocks")

    stocks      = sm.get_stocks()
    replenish   = sm.state.get("replenishment_rates", {})
    consume     = sm.state.get("consumption_rates", {})

    items = [
        ("🌾 Food",    "food_kg",        "kg",  50),
        ("💧 Water",   "water_liters",   "L",   200),
        ("⚡ Energy",  "energy_joules",  "J",   100_000),
        ("♻️ Recycling","recycling_kg",  "kg",  30),
    ]

    for label, key, unit, threshold in items:
        val  = stocks.get(key, 0)
        r    = replenish.get(key, 0)
        c    = consume.get(key, 0)
        net  = r - c
        pct  = min(1.0, val / STOCK_MAX.get(key, val + 1))
        warn = val < threshold

        with st.expander(f"{label}  —  {val:,.1f} {unit}  {'⚠️' if warn else '✅'}", expanded=warn):
            col1, col2, col3 = st.columns(3)
            col1.metric("Current", f"{val:,.1f} {unit}")
            col2.metric("Per cycle +", f"+{r:.1f} {unit}")
            col3.metric("Per cycle −", f"−{c:.1f} {unit}")
            st.progress(pct)
            net_colour = "green" if net >= 0 else "red"
            st.caption(
                f"Net per cycle: {net:+.1f} {unit}  |  "
                f"Threshold: {threshold} {unit}  |  "
                f"{'Below threshold — needs attention' if warn else 'Above threshold'}"
            )

# ──────────────────────────────────────────────
#  PAGE: MEMORY LOG
# ──────────────────────────────────────────────

elif page == "🗂️ Memory Log":
    st.title("🗂️ Ethical Memory Store")
    st.caption("Immutable, tamper-evident log of every system decision and human response.")

    integrity = memory.verify_integrity()
    if integrity["status"] == "intact":
        st.success(f"✅ Memory integrity: intact — {integrity['total_entries']} entries")
    else:
        st.error(f"⚠️ Memory integrity: {integrity['status']}")

    entries = memory.get_all()
    if not entries:
        st.info("No entries yet. Run a cycle first.")
    else:
        # Filter
        types = sorted(set(e.get("data", {}).get("type", "unknown") for e in entries))
        selected = st.multiselect("Filter by type", types, default=types)

        filtered = [e for e in entries if e.get("data", {}).get("type") in selected]
        st.caption(f"Showing {len(filtered)} of {len(entries)} entries")

        for entry in reversed(filtered[-50:]):  # last 50, newest first
            d = entry.get("data", {})
            etype = d.get("type", "unknown")
            ts    = entry.get("timestamp", "")[:19]
            idx   = entry.get("index", "?")

            icon = {
                "system_start":          "🟢",
                "resource_distribution": "⚡",
                "human_response":        "🙋",
                "vital_service_response":"🌱",
                "conflict_resolution":   "⚖️",
            }.get(etype, "📝")

            with st.expander(f"{icon} #{idx} [{ts}] {etype}"):
                st.json(d)
                st.caption(f"Hash: {entry.get('hash','?')}  |  Prev: {entry.get('previous_hash','?')}")

# ──────────────────────────────────────────────
#  PAGE: SIMULATE CYCLE
# ──────────────────────────────────────────────

elif page == "⚙️ Simulate Cycle":
    st.title("⚙️ Simulate a Cycle")
    st.caption(
        "Use this to advance the world state without running the terminal. "
        "Choose how many proposals are accepted and watch the state evolve."
    )

    st.subheader("Simulation Parameters")

    col1, col2 = st.columns(2)
    with col1:
        accepted = st.slider("Proposals accepted this cycle", 0, 10, 3)
    with col2:
        joules   = st.slider("Energy accepted (kJ)", 0.0, 20.0, 8.0, step=0.5)

    st.write("")
    preview_col, _ = st.columns([2, 1])
    with preview_col:
        st.info(
            f"Accepting **{accepted} proposals** and **{joules:.1f} kJ** will:\n"
            f"- Replenish stocks (natural production)\n"
            f"- Apply baseline consumption\n"
            f"- Improve Axiom 07 metrics (×{accepted} recovery steps)\n"
            f"- Advance to cycle #{sm.get_cycle() + 1}"
        )

    if st.button("▶️ Advance one cycle", type="primary", use_container_width=False):
        new_cycle = sm.advance_cycle(
            accepted_joules=joules * 1000,
            accepted_proposals=accepted
        )
        memory.log({
            "type": "simulated_cycle",
            "cycle": new_cycle,
            "accepted_proposals": accepted,
            "accepted_joules": joules * 1000
        })
        st.cache_resource.clear()
        st.success(f"✅ Cycle #{new_cycle} complete. State saved.")
        st.rerun()

    st.divider()
    st.subheader("Current state (before advancing)")
    st.json(sm.state)
