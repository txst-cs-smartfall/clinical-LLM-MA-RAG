from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import MOTOR_SCALE_CONTEXT

# ── Motor Agent ────────────────────────────────────────────
def motor_agent(state: AgentState) -> AgentState:

    facts      = state["motor_facts"]
    query      = state["query"]

    if not facts.strip():
        return {"motor_response": ""}

    system = (
        "You are a movement disorder specialist. "
        "Using ONLY the motor examination scores, "
        "describe the motor progression across visits "
        "use the Motor score values exactly as given. "
        "Do not invent symptoms or values. "
        "Report changes chronologically."
        "Always reference both the visit number and visit date when describing change, "
        "using the format: Visit N (YYYY-MM-DD). "
        "If individual MotorItems are provided with only single visit, report ALL of them with their scores — do not skip or filter any item."
        
        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE visit. All Motor scores from Visit 1 serve as the "
        "clinical reference point. For every visit after Visit 1, report both the change "
        "from the previous visit AND the cumulative change from Visit 1 baseline.\n"
        "Example: 'Visit 3 Motor=28 — worsened by +3 from Visit 2 (25), and +8 from "
        "baseline Visit 1 (20).'"

        "Direction labeling rule:\n"
        "For UPDRS Motor scores: a DECREASE from baseline = improvement, an INCREASE = worsening. "
        "Never use the word 'worsened' when the cumulative change from baseline is negative. "
        "Never use the word 'improved' when the cumulative change from baseline is positive.\n"
    )

    user = (
        f"Scale Reference:\n{MOTOR_SCALE_CONTEXT}\n\n"
        f"Motor Domain Facts:\n{facts}\n\n"
        f"Query: {query}\n"
        "Motor Progression:"
    )

    response = call_llm(system, user)

    print(f"[MOTOR AGENT] {len(response)} chars")

    return {
        "motor_response": response,
        "messages": [AIMessage(content=f"Motor:\n{response}")]
    }