from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import ADL_SCALE_CONTEXT

# ── ADL Agent ───────────────────────────────────────        
def adl_agent(state: AgentState) -> AgentState:

    facts      = state["adl_facts"]
    query      = state["query"]
    
    if not facts.strip():
        return {"adl_response": ""}

    system = (
        "You are a Parkinson disease clinical specialist analyzing ADL (Activities of Daily Living) "
        "scores from UPDRS Part II.\n\n"

        "The raw scores and individual item values are already displayed separately. "
        "DO NOT restate, reprint, or list the item scores. "
        "Use exact item names as provided, do not paraphrase or substitute. "
        "Your job is to write ONLY clinical interpretation and commentary.\n\n"

        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE. For every subsequent visit, report the change "
        "from the previous visit AND the cumulative change from Visit 1 baseline.\n\n"
        
        "Cumulative change calculation rule:\n"
        "Cumulative change from baseline = current visit score MINUS Visit 1 score. "
        "Do NOT compute cumulative change as a running sum of visit-to-visit differences. "
        "Example: if Visit 1=13, Visit 2=22, Visit 3=3 — cumulative change at Visit 3 = 3-13 = -10, NOT -16.\n"

        "For each visit, write 2-3 sentences covering:\n"
        "1. The total ADL score, change from previous visit, and cumulative change from baseline.\n"
        "2. Which functional domains drove the change (fine motor/communication, tremor/eating, "
        "gross motor/mobility) — cite specific items by name only, not their scores.\n"
        "3. Clinical significance: what does this change mean for the patient's independence?\n\n"

        "End with a 2-sentence overall trajectory summary.\n\n"

        "Rules:\n"
        "- Do NOT print item score tables or lists.\n"
        "- Do NOT use phrases like 'based on the provided data' or 'the following items'.\n"
        "- Do NOT invent scores or visits.\n"
        "- Higher ADL = worse daily functioning.\n"
    )

    user = (
        f"Scale Reference:\n{ADL_SCALE_CONTEXT}\n\n"
        f"ADL Domain Facts:\n{facts}\n\n"
        f"Query: {query}\n"
        "ADL Progression:"
    )

    response = call_llm(system, user)

    print(f"[ADL AGENT] {len(response)} chars")

    return {
        "adl_response": response,
        "messages": [AIMessage(content=f"ADL:\n{response}")]
    }