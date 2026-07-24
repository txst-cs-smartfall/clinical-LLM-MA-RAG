from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.utils.formatting import build_score_table

# ── Final Agent Handlers ────────────────────────────────────────────

def _final_cohort_summary(query: str, cohort: str) -> str:

    system = (
        "You are a Parkinson disease clinician writing the final answer to a cohort analysis query.\n\n"
        "Rules:\n"
        "- Return ONLY one short paragraph.\n"
        "- Use ONLY the cohort analysis result provided.\n"
        "- Do NOT interpret domain trajectories.\n"
        "- Do NOT invent scores or visits.\n"
        "- Do NOT mention motor, ADL, non-motor, or PDQ8 trends.\n"
        "- Simply report the cohort finding in clinical language.\n"
    )

    user = (
        f"Clinical Query:\n{query}\n\n"
        f"Cohort Analysis Result:\n{cohort}\n\n"
        "Final Clinical Answer:"
    )

    response = call_llm(system, user).strip()
    print(f"[FINAL AGENT - COHORT MODE] {len(response)} chars")
    return response


# ──────────────────────────────────────────────────────────────────
def _final_comparison_summary(query, comparison, facts, score_table):

    system = (
        "You are a Parkinson disease clinician writing the final clinical interpretation "
        "of a multi-patient comparison.\n\n"

        "The detailed per-visit breakdown and domain comparisons have already been completed. "
        "Do NOT repeat or re-summarize them.\n\n"
        
        "Cross-Domain Pattern Analysis:\n"
        "After the per-domain comparison paragraphs, write one paragraph analyzing "
        "cross-domain patterns across the compared patients:\n"
        "- DISCORDANCE: Identify any domain where one patient improved while the other "
        "worsened across the same visits. State the clinical meaning.\n"
        "- DIVERGENCE POINT: Identify the visit where the two patients' trajectories "
        "diverged most significantly and which domain drove that divergence.\n"
        "- COMPENSATORY PATTERNS: Note if one patient shows worse motor but better QoL "
        "than the other — this may indicate better coping or treatment response.\n\n"

        "Domains Requiring Monitoring:\n"
        "Write one short paragraph stating, for EACH patient, which domain requires "
        "closest monitoring and why, based on the comparative trajectory. "
        "Cite specific visit numbers and scores.\n\n"


        "Your task — identify and articulate hidden clinical patterns:\n"
        "1. Are there synchronized worsening periods across patients suggesting "
        "shared disease milestones?\n"
        "2. Are there domains that diverge between patients — one worsening while "
        "the other improves?\n"
        "3. Is there a mismatch between UPDRS burden and PDQ8 quality of life "
        "for any patient?\n"
        "4. Are there visits where multiple domains worsen simultaneously, "
        "suggesting a clinical inflection point?\n"
        "5. Which patient shows faster overall disease velocity and what is the evidence?\n\n"

        "Rules:\n"
        "- Be specific — cite visit numbers, dates, and scores.\n"
        "- Do NOT use vague language like 'clinically variable' or 'fluctuating trends'.\n"
        "- Do NOT invent scores or visits.\n"
        "- Higher UPDRS = worse symptoms. Higher PDQ8 = worse quality of life.\n"
    )

    user = (
        f"Query:\n{query}\n\n"
        f"Score Table (verify ALL cross-domain claims against this):\n{score_table}\n\n"
        f"Extracted Facts:\n{facts}\n\n"
        f"Comparison Report:\n{comparison}\n\n"
        "Hidden Patterns and Clinical Interpretation:"
    )

    response = call_llm(system, user).strip()
    print(f"[FINAL AGENT - COMPARISON MODE] {len(response)} chars")
    return response

# ──────────────────────────────────────────────────────────────────
def _final_domain_summary(query, facts, score_table, motor, adl, nonmotor, qol):

    system = (
        "You are a Parkinson disease clinician writing the final interpretation "
        "of a single-patient clinical trajectory report. Write in natural clinical "
        "prose — no bullet points, no tables, no numbered lists.\n\n"

        "Rules:\n"
        "- Use ONLY the information provided in the domain reports and extracted facts.\n"
        "- Do NOT invent scores, visits, or dates.\n"
        "- Do NOT include generic introductions or conclusions.\n"
        "- Do NOT re-derive or re-label directions of change — use ONLY the pre-labeled "
        "directions provided in the structured facts.\n\n"

        "Baseline Rule:\n"
        "- Visit 1 is always the BASELINE visit. All subsequent visits must be interpreted "
        "relative to Visit 1.\n\n"

        "Write the report in the following structure:\n\n"

        "Paragraph 1 — Overall Trajectory Summary:\n"
        "In ONE concise paragraph, summarize the patient's trajectory across ALL visits "
        "from baseline to the most recent visit. State the baseline (Visit 1) scores for "
        "Motor, ADL, NonMotor, and PDQ8, then state the net change at the final visit for "
        "each domain relative to baseline, with correct clinical direction (for UPDRS "
        "Motor/ADL/NonMotor and for PDQ8, a decrease = improvement, an increase = "
        "worsening). Mention only the most clinically significant intermediate visits if "
        "they mark a notable inflection point (e.g., a sudden worsening or improvement); "
        "do not describe every visit individually. If any score is 0 at any point, flag "
        "this as clinically notable. Keep this paragraph brief and information-dense — "
        "avoid restating item-level detail already covered in the specialist reports.\n\n"

        "Paragraph 2 — Cross-Domain Pattern Analysis:\n"
        "Cross-domain analysis must be grounded STRICTLY in the score values provided. "
        "Do NOT describe a domain as 'stable' if its score changed by more than 1 point. "
        "Cover:\n"
        "- DISCORDANCE: Identify any visits where domains moved in opposite directions "
        "(e.g., UPDRS improved but PDQ-8 worsened, or vice versa). State the clinical "
        "meaning of each discordance explicitly.\n"
        "- LEADING INDICATORS: State which domain(s) tended to worsen first before "
        "others followed.\n"
        "- LAGGING INDICATORS: State which domain(s) recovered last or failed to recover.\n"
        "- FLOOR EFFECTS: If any domain reached a score of 0 at any visit, note whether "
        "complete resolution is clinically plausible given the other domains at that visit.\n\n"

        "Paragraph 3 — Domains Requiring Monitoring:\n"
        "State which domain(s) require closest clinical monitoring and why, based strictly "
        "on the trajectory patterns observed. Cite the visit numbers and score values that "
        "justify each monitoring recommendation. Do NOT use generic language like 'all "
        "domains should be monitored'. Verify every cited item score directly against the "
        "NonMotorItems and PDQ8Items in the extracted facts. Do NOT cite an item as "
        "'persisting' if its score at the final visit is 0.\n\n"

        "Clinical scale rules:\n"
        "- UPDRS scores (Motor, ADL, NonMotor): higher = worse symptoms.\n"
        "- PDQ8 scores: higher = worse quality of life.\n"
        "- A score of 0 for any domain at any visit is clinically notable and must be "
        "explicitly acknowledged in prose.\n\n"

        "Overall length target: three paragraphs total, concise and clinically precise, "
        "avoiding unnecessary repetition of item-level detail already reported by the "
        "specialist agents.\n"
    )

    user = (
        f"Query:\n{query}\n\n"
        f"Score Table (verify ALL cross-domain claims against this):\n{score_table}\n\n"
        f"Extracted Facts (item-level detail):\n{facts}\n\n"
        f"Motor Report:\n{motor}\n\n"
        f"ADL Report:\n{adl}\n\n"
        f"Non-Motor Report:\n{nonmotor}\n\n"
        f"QoL Report:\n{qol}\n\n"
        "Final Clinical Interpretation:"
    )

    response = call_llm(system, user).strip()
    print(f"[FINAL AGENT - DOMAIN MODE] {len(response)} chars")
    return response


def _final_single_session_summary(query, facts, score_table, motor, adl, nonmotor, qol):

    system = (
        "You are a Parkinson disease clinician writing a concise final summary "
        "of a single clinical session.\n\n"

        "The detailed per-domain breakdowns have already been completed by specialist agents. "
        "Do NOT repeat or re-list individual item scores.\n\n"
        
        "Baseline Rule:\n"
        "If the session being reported is Visit 1, explicitly identify it as the BASELINE "
        "visit and note that it serves as the clinical reference point for all future visits. "
        "If the session is any visit other than Visit 1, state the scores relative to the "
        "Visit 1 baseline if baseline data is available.\n\n"

        "Your task:\n"
        "1. State the visit number and date: Visit N (YYYY-MM-DD).\n"
        "2. For each domain, report ONLY the total score and the 2-3 most clinically "
        "significant items (highest scores or most impactful symptoms).\n"
        "3. End with one overall clinical interpretation sentence describing "
        "the patient's current status across all domains.\n\n"

        "Rules:\n"
        "- Use ONLY the domain reports provided.\n"
        "- Do NOT invent scores, visits, or dates.\n"
        "- Do NOT comment on progression — this is a single session.\n"
        "- Be concise. The summary should be readable in under 30 seconds.\n\n"

        "Cross-Domain Pattern Analysis:\n"
        "After the per-domain summaries, write one paragraph analyzing cross-domain "
        "patterns within this single session:\n"
        "- DISCORDANCE: Identify any domains that are moving in opposite directions of "
        "burden — e.g., low UPDRS Motor/ADL/NonMotor but high PDQ-8, or high objective "
        "motor burden but low subjective QoL impact. State the clinical meaning explicitly.\n"
        "- DISPROPORTIONATE BURDEN: Identify if any single domain is carrying "
        "disproportionately more burden than the others at this visit — this indicates "
        "where the patient's current disease expression is concentrated.\n"
        "- INCONGRUENCE FLAGS: If any domain score is 0 while others are elevated, "
        "flag this as potentially incongruent and note what it may indicate clinically "
        "(e.g., patient under-reporting, measurement timing, medication effect).\n\n"

        "Domains Requiring Monitoring:\n"
        "Write one short paragraph stating which domain(s) require closest follow-up "
        "at the next visit and why, based strictly on the current session's findings. "
        "Cite the specific items and scores that justify each recommendation. "
        "Do NOT use generic language like 'all domains should be monitored'.\n\n"
    )

    user = (
        f"Query:\n{query}\n\n"
        f"Score Table (verify ALL cross-domain claims against this):\n{score_table}\n\n"
        f"Extracted Facts (item-level detail):\n{facts}\n\n"
        f"Motor Report:\n{motor}\n\n"
        f"ADL Report:\n{adl}\n\n"
        f"Non-Motor Report:\n{nonmotor}\n\n"
        f"QoL Report:\n{qol}\n\n"
        "Concise Final Clinical Summary:"
    )

    response = call_llm(system, user).strip()
    print(f"[FINAL AGENT - SINGLE SESSION MODE] {len(response)} chars")
    return response



# ── Final Agent (dispatcher) ────────────────────────────────────────

def final_agent(state: AgentState) -> AgentState:

    query      = state["query"]
    facts      = state["extracted_facts"]
    plan       = state.get("analysis_plan", "")
    
    motor      = state.get("motor_response", "")
    adl        = state.get("adl_response", "")
    nonmotor   = state.get("nonmotor_response", "")
    qol        = state.get("qol_response", "")
    comparison = state.get("comparison_response", "")
    cohort     = state.get("cohort_response", "")
    
    # parse analysis_type directly from plan
    analysis_type = ""
    for line in plan.split("\n"):
        if "ANALYSIS_TYPE:" in line:
            analysis_type = line.split("ANALYSIS_TYPE:")[-1].strip().lower()
            break

    # final_agent dispatcher — correct calls
    score_table = build_score_table(facts)

    if cohort and cohort.strip():
        final = _final_cohort_summary(query, cohort)                               # no change needed

    elif comparison and comparison.strip():
        final = _final_comparison_summary(query, comparison, facts, score_table)   # add score_table

    elif analysis_type == "single-session":
        final = _final_single_session_summary(query, facts, score_table, motor, adl, nonmotor, qol)

    else:
        final = _final_domain_summary(query, facts, score_table, motor, adl, nonmotor, qol)

    return {
        "final_answer": final,
        "messages": [AIMessage(content=f"Final:\n{final}")]
    }