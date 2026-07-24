from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.utils.parsing import interpret_clinical_query

# ── Plan Node (Automated Stage A + B) ─────────────────────
def plan_node(state: AgentState) -> AgentState:

    query = state["query"]

    system = (
        "You are a clinical query planner for a Parkinson disease analysis system.\n"
        "Convert the user's question into a structured analysis plan.\n\n"

        "Rules:\n"
        "1. PARTICIPANTS must be patient IDs mentioned in the query.\n"
        "2. If the question refers to all patients use PARTICIPANTS: ALL.\n"
        "3. ANALYSIS_TYPE must be one of: trajectory, comparison, cohort, single-session.\n"
        "4. METRICS must be one or both of: UPDRS, PDQ8.\n"
        "5. FILTER must be one of:\n"
        "   none | baseline | latest_visit | baseline_vs_latest | first_N_visits | last_N_visits\n"
        "   where N is the exact number specified by the user (e.g. first_2_visits, last_5_visits).\n\n"

        "ANALYSIS_TYPE Selection Rules:\n"
        "- Use 'comparison'     when the query contains: compare, vs, versus, difference between, contrast, side by side\n"
        "- Use 'trajectory'     when the query contains: trajectory, progression, over time, trend, how did, changed, visits\n"
        "- Use 'cohort'         when the query contains: highest, lowest, average, fastest, most, least, all patients, who has\n"
        "- Use 'single-session' when the query contains: baseline, latest, last visit, most recent, session\n\n"

        "FILTER Selection Rules:\n"
        "- Use 'none'               for trajectory or comparison queries (all visits needed)\n"
        "- Use 'baseline'           when the query asks about the first/baseline visit only\n"
        "- Use 'latest_visit'       when the query asks about the most recent/last visit only\n"
        "- Use 'baseline_vs_latest' when the query asks to compare first vs last visit\n"
        "- Use 'first_N_visits'     when the query asks about the first/earliest N visits — replace N with the user's number\n"
        "- Use 'last_N_visits'      when the query asks about the last/most recent N visits — replace N with the user's number\n\n"

        "METRICS Selection Rules:\n"
        "- Use 'UPDRS'        when motor, ADL, or non-motor domains are mentioned\n"
        "- Use 'PDQ8'         when quality of life, QoL, or PDQ8 is mentioned\n"
        "- Use 'UPDRS, PDQ8'  when the query is general (no specific metric mentioned)\n\n"

        "Examples:\n"
        "Query: compare trajectories of proj ids 2 and 1\n"
        "PARTICIPANTS: 2, 1\n"
        "ANALYSIS_TYPE: comparison\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: none\n\n"

        "Query: show me the motor progression of patient 3\n"
        "PARTICIPANTS: 3\n"
        "ANALYSIS_TYPE: trajectory\n"
        "METRICS: UPDRS\n"
        "FILTER: none\n\n"

        "Query: who has the highest PDQ8 score\n"
        "PARTICIPANTS: ALL\n"
        "ANALYSIS_TYPE: cohort\n"
        "METRICS: PDQ8\n"
        "FILTER: none\n\n"

        "Query: what is the baseline status of patient 5\n"
        "PARTICIPANTS: 5\n"
        "ANALYSIS_TYPE: single-session\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: baseline\n\n"

        "Query: compare the latest visit of patients 1 and 4\n"
        "PARTICIPANTS: 1, 4\n"
        "ANALYSIS_TYPE: comparison\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: latest_visit\n\n"

        "Query: show me the first 2 visits of patient 3\n"
        "PARTICIPANTS: 3\n"
        "ANALYSIS_TYPE: trajectory\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: first_2_visits\n\n"

        "Query: compare the last 4 visits of patients 1 and 2\n"
        "PARTICIPANTS: 1, 2\n"
        "ANALYSIS_TYPE: comparison\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: last_4_visits\n\n"

        "Query: show trajectory for patient 7 over the last 5 visits\n"
        "PARTICIPANTS: 7\n"
        "ANALYSIS_TYPE: trajectory\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: last_5_visits\n\n"
        
        "Query: what is the status of visit 5 for patient 1\n"
        "PARTICIPANTS: 1\n"
        "ANALYSIS_TYPE: single-session\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: visit_5\n\n"

        "Query: what is the status of visit 2 for patient 3\n"
        "PARTICIPANTS: 3\n"
        "ANALYSIS_TYPE: single-session\n"
        "METRICS: UPDRS, PDQ8\n"
        "FILTER: visit_2\n\n"

        "Return ONLY the plan using this exact format:\n"
        "PARTICIPANTS: ...\n"
        "ANALYSIS_TYPE: ...\n"
        "METRICS: ...\n"
        "FILTER: ...\n"
    )

    user = f"Query:\n{query}\n\nGenerate analysis plan."

    plan = call_llm(system, user)

    lines = []

    for l in plan.split("\n"):
        if any(k in l for k in ["PARTICIPANTS:", "ANALYSIS_TYPE:", "METRICS:", "FILTER:"]):
            lines.append(l.strip())

    if len(lines) >= 4:
        plan = "\n".join(lines[:4])

    # ---- fallback safety ----
    if "PARTICIPANTS:" not in plan:
        plan = (
            "PARTICIPANTS: UNKNOWN\n"
            "ANALYSIS_TYPE: trajectory\n"
            "METRICS: UPDRS, PDQ8\n"
            "FILTER: none"
        )

    print(f"[PLAN]\n{plan}")

    return {
        "analysis_plan": plan,
        "messages": [AIMessage(content=f"Plan:\n{plan}")]
    }
    
    