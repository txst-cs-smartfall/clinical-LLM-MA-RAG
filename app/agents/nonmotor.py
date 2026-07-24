from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import NONMOTOR_SCALE_CONTEXT

# ── Non-Motor Agent ────────────────────────────────────────────    
def nonmotor_agent(state: AgentState) -> AgentState:

    facts      = state["nonmotor_facts"]
    query      = state["query"]
    
    if not facts.strip():
        return {"nonmotor_response": ""}

    system = (
        "You are a neuropsychiatry specialist analyzing UPDRS Part I non-motor scores "
        "for Parkinson disease.\n\n"

        "The raw scores and individual item values are already displayed separately. "
        "DO NOT restate, reprint, or list the item scores. "
        "If NonMotor=0, state that all symptoms resolved. Do not name any driving symptoms. "
        "Your job is to write ONLY clinical interpretation and commentary.\n\n"

        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE. For every subsequent visit, report the change "
        "from the previous visit AND the cumulative change from Visit 1 baseline. "
        "For Visit 1, state it is the baseline. Do not report a change from baseline at Visit 1.\n\n"

        "For each visit, write 2-3 sentences covering:\n"
        "1. The total NonMotor score, change from previous visit, and cumulative change from baseline.\n"
        "2. Which symptom cluster drove the change — autonomic/cognitive burden "
        "(sleep, cognition, pain, urinary, hallucinations) or mood/affect "
        "(depression, anxiety, apathy) — cite specific items by name only, not their scores.\n"
        "3. Flag any item scoring 3 or 4 as HIGH BURDEN and note its clinical significance.\n\n"

        "End with a 2-sentence overall trajectory summary.\n\n"

        "Rules:\n"
        "- Do NOT print item score tables or lists.\n"
        "- Do NOT use phrases like 'based on the provided data' or 'the following items'.\n"
        "- Do NOT invent scores or visits.\n"
        "- Higher NonMotor = worse non-motor burden.\n"
    )



    user = (
        f"Scale Reference:\n{NONMOTOR_SCALE_CONTEXT}\n\n"
        f"Non-Motor Domain Facts:\n{facts}\n\n"
        f"Query: {query}\n"
        "Non-Motor Progression:"
    )

    response = call_llm(system, user)

    print(f"[NONMOTOR AGENT] {len(response)} chars")

    return {
        "nonmotor_response": response,
        "messages": [AIMessage(content=f"NonMotor:\n{response}")]
    }    