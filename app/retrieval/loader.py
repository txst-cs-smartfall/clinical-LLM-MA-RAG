

# app/retrieval/loader.py
from langchain_core.messages import AIMessage
from app.state import AgentState
import re
from typing import Dict, List, Optional, Tuple
from app.retrieval.db import memory_db
from app.utils.parsing import extract_key_facts, detect_domains_and_scales
from app.utils.formatting import split_facts_by_domain, apply_visit_filter


# ── Retrieve Node (redundancy removed) ──────────────────────
def retrieve_node(state: AgentState) -> AgentState:

    query = state["query"]
    plan  = state["analysis_plan"]

    # ── Parse plan ONCE — single source of truth ────────────
    participants  = None
    analysis_type = None
    filter_type   = "none"

    for line in plan.split("\n"):

        if "PARTICIPANTS:" in line:
            val = line.split("PARTICIPANTS:")[-1].strip().lower()
            if val in ["all", "unknown", "none", "not specified"]:
                participants = "ALL"
            else:
                ids = re.findall(r"\d+", val)
                participants = [int(p) for p in ids] if ids else None

        if "ANALYSIS_TYPE:" in line:
            analysis_type = line.split("ANALYSIS_TYPE:")[-1].strip().lower()

        if "FILTER:" in line:
            filter_type = line.split("FILTER:")[-1].strip()

    if participants is None:
        participants = "ALL"
    if analysis_type is None:
        analysis_type = "trajectory"  # safety fallback, mirrors plan_node default

    # ── Map plan's ANALYSIS_TYPE directly to intent ─────────
    # Normalizes label mismatch: plan uses "single-session", pipeline uses "single_session"
    analysis_type_to_intent = {
        "trajectory":     "trajectory",
        "comparison":     "comparison",
        "cohort":         "cohort",
        "single-session": "single_session",
    }
    intent = analysis_type_to_intent.get(analysis_type, "trajectory")

    # "risk" has no equivalent ANALYSIS_TYPE in plan_node's enum, so it is
    # still detected via a lightweight keyword check on the raw query.
    q = query.lower()
    if any(k in q for k in ["risk", "danger", "monitor"]):
        intent = "risk"

    # ── Domain / scale detection — kept, since plan_node's METRICS field
    # only distinguishes UPDRS vs PDQ8, not motor/adl/nonmotor sub-domains ──
    domains, scales = detect_domains_and_scales(query, plan)

    if "pdq8" in scales and "qol" not in domains:
        domains.append("qol")

    print(f"[ROUTING] intent={intent} domains={domains} scales={scales}")

    # ── Resolve patient list ─────────────────────────────────
    if participants == "ALL":
        all_meta = memory_db.get(include=["metadatas"])["metadatas"]
        pid_list = sorted(set(m["proj_id"] for m in all_meta))
    else:
        pid_list = participants

    print(f"[RETRIEVE] fetching {len(pid_list)} patient(s): {pid_list}")

    # ── Fetch per patient, per instrument ───────────────────
    patient_contexts = []

    for pid in pid_list:

        updrs_results = memory_db.get(
            where={"$and": [
                {"proj_id": {"$eq": pid}},
                {"instrument": {"$eq": "updrs"}},
                {"granularity": {"$eq": "session"}}
            ]},
            include=["documents"]
        )
        for doc in updrs_results["documents"]:
            patient_contexts.append(f"[PATIENT {pid}]\n{doc}")

        print(f"  [PID {pid}] UPDRS sessions: {len(updrs_results['documents'])}")

        pdq8_results = memory_db.get(
            where={"$and": [
                {"proj_id": {"$eq": pid}},
                {"instrument": {"$eq": "pdq8"}},
                {"granularity": {"$eq": "session"}}
            ]},
            include=["documents"]
        )
        for doc in pdq8_results["documents"]:
            patient_contexts.append(f"[PATIENT {pid}]\n{doc}")

        print(f"  [PID {pid}] PDQ8  sessions: {len(pdq8_results['documents'])}")

    # ── Extract + filter facts ───────────────────────────────
    facts = extract_key_facts(patient_contexts, single_session=(intent == "single_session"))
    facts = apply_visit_filter(facts, filter_type)

    motor_facts, adl_facts, nonmotor_facts, qol_facts = split_facts_by_domain(facts)

    # ── For non-cohort queries, suppress irrelevant domains ──
    if intent not in ["cohort", "risk"]:
        if "motor"    not in domains: motor_facts    = ""
        if "adl"      not in domains: adl_facts      = ""
        if "nonmotor" not in domains: nonmotor_facts = ""
        if "qol" not in domains and "pdq8" not in scales:
            qol_facts = ""

    return {
        "intent":             intent,
        "domains":            domains,
        "scales":             scales,
        "retrieved_contexts": patient_contexts,
        "extracted_facts":    facts,
        "motor_facts":        motor_facts,
        "adl_facts":          adl_facts,
        "nonmotor_facts":     nonmotor_facts,
        "qol_facts":          qol_facts,
        "messages": [AIMessage(content=f"Retrieved {len(patient_contexts)} records for {len(pid_list)} patient(s)")]
    }
