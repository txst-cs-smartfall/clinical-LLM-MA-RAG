
from langchain_core.messages import AIMessage
from app.state import AgentState
from app.llm import call_llm
from app.context.scale_contexts import COMPARISON_SCALE_CONTEXT
from app.utils.scoring import compute_domain_score, progression
import re


# ── Comparison Agent ───────────────────────────────────────
def comparison_agent(state: AgentState) -> AgentState:
    query = state["query"]
    facts = state.get("extracted_facts", "")

    if state.get("intent") != "comparison":
        return {"comparison_response": ""}

    if not facts.strip():
        return {"comparison_response": "No patient data found for comparison."}

    instrument = state.get("instrument", "")
    if not instrument:
        q = query.lower()
        if "updrs + pdq-8" in q or "updrs+pdq-8" in q:
            instrument = "UPDRS + PDQ-8"
        elif "pdq-8" in q or "pdq8" in q:
            instrument = "PDQ-8"
        else:
            instrument = "UPDRS"

    patients = {}
    current_pid = None

    for line in facts.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("PATIENT"):
            current_pid = line.replace("PATIENT", "").strip()
            patients[current_pid] = []
            continue
        if current_pid and line.startswith("Visit"):
            patients[current_pid].append(line)

    structured_breakdown = ""

    for pid, visits in patients.items():
        structured_breakdown += f"Patient {pid}:\n"
        prev = {}

        for visit_line in visits:
            visit_match = re.match(r"(Visit \d+) \(([^)]+)\):", visit_line)
            if not visit_match:
                continue

            visit_label = visit_match.group(1)
            visit_date = visit_match.group(2)

            scores = {}
            for domain, key in [
                ("Motor", "Motor"),
                ("ADL", "ADL"),
                ("NonMotor", "NonMotor"),
                ("PDQ8", "PDQ8"),
            ]:
                m = re.search(rf"\b{key}=(\d+)", visit_line)
                if m:
                    scores[domain] = int(m.group(1))

            structured_breakdown += f"  {visit_label} ({visit_date}):\n"

            for domain, val in scores.items():
                if domain in prev:
                    diff = val - prev[domain]
                    if diff > 0:
                        direction = f"worsened (+{diff})"
                    elif diff < 0:
                        direction = f"improved ({diff})"
                    else:
                        direction = "stable (no change)"
                else:
                    direction = "baseline"

                structured_breakdown += f"    {domain}: {val} — {direction}\n"
                prev[domain] = val

            for domain in ["Motor", "ADL", "NonMotor", "PDQ8"]:
                if domain not in scores:
                    structured_breakdown += f"    {domain}: not recorded\n"

        structured_breakdown += "\n"

    if instrument == "UPDRS":
        task_text = (
            "Your task:\n"
            "Compare only the UPDRS-related domains across all patients in this exact order:\n"
            "1. Motor Domain\n"
            "2. ADL Domain\n"
            "3. NonMotor Domain\n\n"
        )
        domain_rules_text = (
            "Focus only on Motor, ADL, and NonMotor findings.\n"
            "Do NOT mention PDQ8 or quality-of-life findings unless the user explicitly asked for PDQ8.\n"
            "If PDQ8 appears in the structured data, ignore it.\n\n"
        )
    elif instrument == "PDQ-8":
        task_text = (
            "Your task:\n"
            "Compare only the PDQ8 domain across all patients.\n\n"
        )
        domain_rules_text = (
            "Focus only on PDQ8 findings.\n"
            "Do NOT discuss Motor, ADL, or NonMotor unless the user explicitly asked for them.\n"
            "If Motor, ADL, or NonMotor data appears in the structured data, ignore it.\n\n"
        )
    else:
        task_text = (
            "Your task:\n"
            "Compare all four domains across all patients in this exact order:\n"
            "1. Motor Domain\n"
            "2. ADL Domain\n"
            "3. NonMotor Domain\n"
            "4. PDQ8 Domain\n\n"
        )
        domain_rules_text = (
            "Discuss both UPDRS-related domains and PDQ8.\n"
            "Highlight any concordance or discordance between symptom burden and quality of life.\n\n"
        )

    system = (
        "You are a Parkinson disease clinician performing a side-by-side "
        "comparison of multiple patients.\n\n"

        "You are given a structured per-visit breakdown already computed with "
        "exact scores and directions of change.\n\n"

        f"Selected instrument: {instrument}\n\n"

        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE visit for each patient. All cross-patient "
        "comparisons must anchor to each patient's Visit 1 as the starting reference. "
        "When comparing progression, always state the cumulative change from each "
        "patient's Visit 1 baseline in addition to visit-to-visit changes.\n\n"

        f"{task_text}"

        "For each included domain:\n"
        "- State which patient has greater burden or faster progression.\n"
        "- Cite specific visit numbers and scores to support the claim.\n"
        "- If data is missing for a patient in a domain, explicitly state it.\n"
        "- Keep each domain summary to 3-4 sentences maximum.\n\n"

        "Rules:\n"
        "- Do NOT re-list the per-visit data as it is already shown.\n"
        "- Do NOT use vague language.\n"
        "- Do NOT invent scores or visits.\n"
        "- Higher UPDRS (Motor, ADL, NonMotor) = worse symptoms.\n"
        "- Higher PDQ8 = worse quality of life.\n"
        f"{domain_rules_text}"
    )

    user = (
        f"Query:\n{query}\n\n"
        f"Scale Reference:\n{COMPARISON_SCALE_CONTEXT}\n\n"
        f"Structured Per-Visit Breakdown:\n{structured_breakdown}\n"
        "Domain-by-Domain Cross-Patient Comparison:"
    )

    llm_comparison = call_llm(system, user).strip()

    full_response = (
        "=== Per-Patient Visit Breakdown ===\n\n"
        f"{structured_breakdown}\n"
        "=== Domain-by-Domain Comparison ===\n\n"
        f"{llm_comparison}"
    )

    print(f"[COMPARISON AGENT] {len(full_response)} chars")

    return {
        "comparison_response": full_response,
        "messages": [AIMessage(content=f"Comparison:\n{full_response}")]
    }