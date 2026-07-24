from app.state import AgentState

# ─────────────────────────────────────────
def route_after_retrieve(state):

    intent = state.get("intent")

    print("ROUTER INTENT:", intent)

    if intent == "comparison":
        return "comparison_agent"

    if intent in ["cohort", "risk"]:
        return "cohort_agent"

    return "motor_agent"


# ── Determine Agent Node ──────────────────────────────────────────    
def determine_agent_execution(routing):

    intent = routing["intent"]

    run_motor = "motor" in routing["domains"]
    run_adl = "adl" in routing["domains"]
    run_nonmotor = "nonmotor" in routing["domains"] or "qol" in routing["domains"]

    run_comparison = intent == "comparison"
    run_cohort = intent in ["cohort", "risk"]

    return {
        "motor": run_motor,
        "adl": run_adl,
        "nonmotor": run_nonmotor,
        "comparison": run_comparison,
        "cohort": run_cohort
    } 