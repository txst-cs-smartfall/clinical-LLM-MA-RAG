from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import QOL_SCALE_CONTEXT

def qol_agent(state: AgentState) -> AgentState:

    facts = state["qol_facts"]
    query = state["query"]

    if not facts.strip():
        return {"qol_response": ""}

    system = (
        "You are a Parkinson disease quality-of-life specialist analyzing PDQ-8 scores by summarizing numerical assessment data only.\n\n"

        "The raw PDQ-8 scores and individual item values are already displayed separately. "
        "DO NOT restate, reprint, or list the item scores. "
        "When identifying driving symptoms, always lead with the highest-scoring items first. "
        "Your job is to write ONLY clinical interpretation and commentary.\n\n"

        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE. For every subsequent visit, report the change "
        "from the previous visit AND the cumulative change from Visit 1 baseline.\n\n"
        "At Visit 1 (baseline), cumulative change from baseline is always 0 by definition. "
        "Do NOT report the Visit 1 score itself as a cumulative change value.\n"

        "For each visit, write 2-3 sentences covering:\n"
        "1. The total PDQ-8 score, change from previous visit, and cumulative change from baseline.\n"
        "2. Which PDQ-8 dimensions drove the change — cite specific items by name only, "
        "not their scores. Flag any item scoring 3 or 4 as HIGH IMPACT.\n"
        "3. Overall quality-of-life interpretation: what does this mean for the patient's "
        "daily wellbeing and social functioning?\n\n"

        "End with a 2-sentence overall QoL trajectory summary.\n\n"

        "Rules:\n"
        "- Do NOT print item score tables or lists.\n"
        "- Do NOT use phrases like 'based on the provided data' or 'the following items'.\n"
        "- Do NOT invent scores or visits.\n"
    )

    user = (
        f"Scale Reference:\n{QOL_SCALE_CONTEXT}\n\n"
        f"PDQ8 Facts:\n{facts}\n\n"
        f"Query: {query}\n"
        "Report the PDQ8 total and ALL individual PDQ8 items for each visit:"
    )

    response = call_llm(system, user)

    print(f"[QoL AGENT] {len(response)} chars")

    return {
        "qol_response": response,
        "messages": [AIMessage(content=f"QoL:\n{response}")]
    }