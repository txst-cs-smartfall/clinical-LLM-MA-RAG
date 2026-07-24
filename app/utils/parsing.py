import re
from typing import Any, Dict, List, Tuple

from app.context.label_maps import PDQ8_LABEL_MAP, UPDRS_LABEL_MAP, UPDRS_LABEL_TO_COL, PDQ8_LABEL_TO_COL
from app.utils.formatting import fmt_items


def parse_domain_line(line_value: str, label_to_col: dict) -> dict:
    result = {}
    for item in line_value.split(","):
        item = item.strip()
        if "=" not in item:
            continue
        label, _, raw_val = item.partition("=")
        label = label.strip()
        col   = label_to_col.get(label, label)
        try:
            result[col] = int(raw_val.strip())
        except ValueError:
            pass
    return result

# ─────────────────────────────────────────────────────────────
# STEP 3: Main function
# ─────────────────────────────────────────────────────────────
def extract_key_facts(contexts: list, single_session: bool = False):

    patientdata = {}

    for ctx in contexts:
        match = re.search(r'PATIENT\s+(\w+)', ctx)
        pid = match.group(1) if match else "UNKNOWN"
        doc = ctx.split("\n", 1)[1] if "\n" in ctx else ctx

        if pid not in patientdata:
            patientdata[pid] = {}

        lines = {}
        for line in doc.split("\n"):
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            lines[key.strip()] = val.strip()

        visit = lines.get("Visit Number", "")
        date  = lines.get("Visit Date", "").split(" ")[0]
        try:
            visitid = int(visit)
        except:
            continue

        motor_items    = parse_domain_line(lines.get("Motor", ""),     UPDRS_LABEL_TO_COL)
        adl_items      = parse_domain_line(lines.get("ADL", ""),       UPDRS_LABEL_TO_COL)
        nonmotor_items = parse_domain_line(lines.get("Non-Motor", ""), UPDRS_LABEL_TO_COL)
        pdq8_items     = parse_domain_line(lines.get("PDQ8", ""),      PDQ8_LABEL_TO_COL)
        pdq8_items.pop("PDQ_8_TOTAL", None)

        motor    = sum(motor_items.values())
        adl      = sum(adl_items.values())
        nonmotor = sum(nonmotor_items.values())

        pdq8 = None
        for key in ["PDQ8 Total", "PDQ_8_TOTAL"]:
            if key in lines:
                try:
                    pdq8 = int(lines[key])
                    break
                except ValueError:
                    pass
        if pdq8 is None and pdq8_items:
            pdq8 = sum(pdq8_items.values())

        if pdq8 is None and not pdq8_items:
            print(f"[DEBUG] PID={pid} Visit={visitid} — no PDQ8 field found in record")
        else:
            print(f"[DEBUG] PID={pid} Visit={visitid} — PDQ8={pdq8}")

        if visitid not in patientdata[pid]:
            patientdata[pid][visitid] = {
                "date":          date,
                "motor":         motor,    "motor_items":    motor_items,
                "adl":           adl,      "adl_items":      adl_items,
                "nonmotor":      nonmotor, "nonmotor_items": nonmotor_items,
                "pdq8":          pdq8,     "pdq8_items":     pdq8_items,
            }
        else:
            existing = patientdata[pid][visitid]
            if pdq8 is not None:
                existing["pdq8"] = pdq8
            if pdq8_items:
                existing["pdq8_items"] = pdq8_items
            if motor > 0 and existing["motor"] == 0:
                existing["motor"]       = motor
                existing["motor_items"] = motor_items
            if adl > 0 and existing["adl"] == 0:
                existing["adl"]         = adl
                existing["adl_items"]   = adl_items
            if nonmotor > 0 and existing["nonmotor"] == 0:
                existing["nonmotor"]       = nonmotor
                existing["nonmotor_items"] = nonmotor_items

    output = []
    for pid, visits in patientdata.items():
        output.append(f"PATIENT {pid}")
        for v in sorted(visits.keys()):
            item = visits[v]
            line = (
                f"Visit {v} ({item['date']}): "
                f"Motor={item['motor']} ADL={item['adl']} NonMotor={item['nonmotor']}"
            )

            # ── Always emit item-level detail for all three UPDRS domains ──
            if item.get("motor_items"):
                line += f" | MotorItems={fmt_items(item['motor_items'], UPDRS_LABEL_MAP)}"
            if item.get("adl_items"):
                line += f" | ADLItems={fmt_items(item['adl_items'], UPDRS_LABEL_MAP)}"
            if item.get("nonmotor_items"):
                line += f" | NonMotorItems={fmt_items(item['nonmotor_items'], UPDRS_LABEL_MAP)}"

            if item["pdq8"] is not None:
                line += f" | PDQ8={item['pdq8']}"

            # ── PDQ8 items: always emit if available ──
            if item.get("pdq8_items"):
                line += f" | PDQ8Items={fmt_items(item['pdq8_items'], PDQ8_LABEL_MAP)}"

            output.append(line)
        output.append("")

    return "\n".join(output)

# ── Slimmed-down domain/scale detector ──────────────────────
# Only responsible for motor/adl/nonmotor/qol sub-domain detection,
# since intent classification is now sourced from the plan.
def detect_domains_and_scales(query: str, plan: str = ""):

    q = query.lower()
    domains = []

    if "motor" in q:
        domains.append("motor")
    if "adl" in q or "daily living" in q:
        domains.append("adl")
    if "non motor" in q or "cognition" in q or "psychiatric" in q:
        domains.append("nonmotor")
    if "qol" in q or "quality of life" in q or "pdq8" in q:
        domains.append("qol")

    if "updrs" in q:
        domains = ["motor", "adl", "nonmotor"]

    if not domains:
        domains = ["motor", "adl", "nonmotor", "qol"]

    scales = []

    if "pdq8" in q or "quality of life" in q:
        scales.append("pdq8")
    if "updrs" in q:
        scales.append("updrs")

    if ("motor" in domains or "adl" in domains or "nonmotor" in domains) and "updrs" not in scales:
        scales.append("updrs")
    if "qol" in domains and "pdq8" not in scales:
        scales.append("pdq8")

    if not scales:
        scales = ["updrs", "pdq8"]

    return domains, scales


# ------------------------------------------------------
def interpret_clinical_query(query: str, plan: str = ""):
    """
    Determine intent, domains, and scales required for the query.
    """

    q = query.lower()

    # -------------------------
    # Intent detection
    # -------------------------

    if "compare" in q or "vs" in q:
        intent = "comparison"

    elif "highest" in q or "lowest" in q or "average" in q or "fastest" in q:
        intent = "cohort"

    elif "risk" in q or "danger" in q or "monitor" in q:
        intent = "risk"

    elif "baseline" in q or "latest" in q or "session" in q:
        intent = "single_session"

    else:
        intent = "trajectory"


    # -------------------------
    # Domain detection
    # -------------------------

    domains = []

    if "motor" in q:
        domains.append("motor")

    if "adl" in q or "daily living" in q:
        domains.append("adl")

    if "non motor" in q or "cognition" in q or "psychiatric" in q:
        domains.append("nonmotor")

    if "qol" in q or "quality of life" in q or "pdq8" in q:
        domains.append("qol")

    # If user explicitly says UPDRS
    if "updrs" in q:
        domains = ["motor", "adl", "nonmotor"]

    # Default trajectory request → all UPDRS domains
    if not domains:
        domains = ["motor", "adl", "nonmotor", "qol"]


    # -------------------------
    # Scale detection
    # -------------------------

    scales = []

    if "pdq8" in q or "quality of life" in q:
        scales.append("pdq8")

    if "updrs" in q:
        scales.append("updrs")

    # domain-based scale inference
    if "motor" in domains or "adl" in domains:
        if "updrs" not in scales:
            scales.append("updrs")

    if "nonmotor" in domains:
        if "updrs" not in scales:
            scales.append("updrs")

    if "qol" in domains:
        if "pdq8" not in scales:
            scales.append("pdq8")

    if not scales:
        scales = ["updrs", "pdq8"]

    return {
        "intent": intent,
        "domains": domains,
        "scales": scales
    }
    
# --------------------------------
def detect_cohort_intent(query: str):

    q = query.lower()

    # ---- Highest / Lowest burden ----

    if ("highest" in q or "most severe" in q or "worst" in q):
        return "max_total_burden"

    if ("lowest" in q or "least severe" in q or "best" in q):
        return "min_total_burden"


    # ---- QoL extremes ----

    if "pdq8" in q and ("highest" in q or "worst" in q):
        return "max_pdq8"

    if "pdq8" in q and ("lowest" in q or "best" in q):
        return "min_pdq8"


    # ---- Largest increase ----

    if "motor" in q and "increase" in q:
        return "largest_motor_increase"

    if "adl" in q and "increase" in q:
        return "largest_adl_increase"

    if "nonmotor" in q and "increase" in q:
        return "largest_nonmotor_increase"

    if "pdq8" in q and "increase" in q:
        return "largest_pdq8_increase"


    # ---- Fastest deterioration ----

    if "motor" in q and "deterioration" in q:
        return "fastest_motor_deterioration"

    if "adl" in q and "deterioration" in q:
        return "fastest_adl_deterioration"

    if "nonmotor" in q and "deterioration" in q:
        return "fastest_nonmotor_deterioration"

    if ("qol" in q or "pdq8" in q) and "deterioration" in q:
        return "fastest_qol_worsening"


    # ---- Stability ----

    if "stable" in q and "motor" in q:
        return "most_stable_motor"

    if "stable" in q and ("pdq8" in q or "quality of life" in q):
        return "most_stable_qol"

    if "stable" in q:
        return "most_stable_overall"


    # ---- Averages ----

    if "average" in q and "motor" in q:
        return "avg_motor"

    if "average" in q and "adl" in q:
        return "avg_adl"

    if "average" in q and "nonmotor" in q:
        return "avg_nonmotor"

    if "average" in q and ("pdq8" in q or "qol" in q):
        return "avg_pdq8"


    # ---- Risk queries ----

    if "extra care" in q or "danger" in q or "high risk" in q:
        return "high_risk_patient"

    if "moderate" in q or "monitor" in q:
        return "moderate_risk_patient"

    if "doing well" in q or "stable patient" in q or "low risk" in q:
        return "low_risk_patient"


    return "general_cohort"

    