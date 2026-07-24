from langchain_core.messages import AIMessage

from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import COMPARISON_SCALE_CONTEXT
from app.utils.scoring import compute_cohort_statistics, detect_patient_risk
from app.utils.parsing import detect_cohort_intent
from app.utils.scoring import interpret_cohort_stats

# ── Cohort Agent ───────────────────────────────────────────
def cohort_agent(state: AgentState) -> AgentState:

    plan  = state["analysis_plan"]
    query = state["query"]

    analysis_type = ""

    for line in plan.split("\n"):
        if "ANALYSIS_TYPE:" in line:
            analysis_type = line.split("ANALYSIS_TYPE:")[-1].strip().lower()

    if analysis_type != "cohort" and "risk" not in query.lower():
        return {"cohort_response": ""}

    facts = state["extracted_facts"]

    if not facts.strip():
        return {"cohort_response": "No cohort data available."}

    stats = compute_cohort_statistics(facts)

    metric = detect_cohort_intent(query)

    interpretation = interpret_cohort_stats(query, stats, metric)

    print(f"[COHORT STATS] {stats}")
    print(f"[COHORT METRIC] {metric}")
    # print(f"[COHORT INTERPRETATION] {interpretation}")

    return {
        "cohort_stats": stats,
        "cohort_metric": metric,
        "cohort_response": interpretation,
        "messages": [AIMessage(content=f"Cohort:\n{interpretation}")]
    }