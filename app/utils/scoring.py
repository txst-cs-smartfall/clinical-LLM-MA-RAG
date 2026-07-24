
import re
import statistics
from typing import Any, Dict, List, Optional, Tuple
from app.context.scale_contexts import COMPARISON_SCALE_CONTEXT
from app.llm import call_llm

# --- domain score helper ---

def compute_domain_score(domain_line):

            if not domain_line:
                return 0

            score = 0

            items = domain_line.split(",")

            for item in items:

                if "=" not in item:
                    continue

                try:
                    val = int(item.split("=")[1])
                except:
                    continue

                score += val

            return score
        
# ---------- Domain progression ----------
def progression(domain_data):

            if len(domain_data) < 2:
                return None

            first_v, first_s = domain_data[0]
            last_v, last_s = domain_data[-1]

            increase = last_s - first_s
            visit_diff = last_v - first_v
            slope = increase / visit_diff if visit_diff else 0

            return increase, slope
        
# ------------
def compute_cohort_statistics(facts: str):

    patients = {}
    current_patient = None

    for line in facts.split("\n"):

        line = line.strip()

        if line.startswith("PATIENT"):
            try:
                current_patient = int(line.split("PATIENT")[1].strip())
                patients[current_patient] = {
                    "motor": [],
                    "adl": [],
                    "nonmotor": [],
                    "total": [],
                    "pdq8": []
                }
            except:
                current_patient = None
            continue

        if current_patient is None:
            continue

        visit_match = re.search(r"Visit (\d+)", line)
        visit = int(visit_match.group(1)) if visit_match else None

        if visit is None:
            continue


        # ---------- Extract domains ----------

        motor = None
        adl = None
        nonmotor = None

        m = re.search(r"Motor=(\d+)", line)
        if m:
            motor = int(m.group(1))

        m = re.search(r"ADL=(\d+)", line)
        if m:
            adl = int(m.group(1))

        m = re.search(r"NonMotor=(\d+)", line)
        if m:
            nonmotor = int(m.group(1))


        # ---------- Store domains ----------

        if motor is not None:
            patients[current_patient]["motor"].append((visit, motor))

        if adl is not None:
            patients[current_patient]["adl"].append((visit, adl))

        if nonmotor is not None:
            patients[current_patient]["nonmotor"].append((visit, nonmotor))


        # ---------- Total disease burden ----------

        if motor is not None or adl is not None or nonmotor is not None:

            total = (motor or 0) + (adl or 0) + (nonmotor or 0)
            patients[current_patient]["total"].append((visit, total))


        # ---------- PDQ8 ----------

        m = re.search(r"PDQ8=(\d+)", line)
        if m:
            score = int(m.group(1))
            patients[current_patient]["pdq8"].append((visit, score))


    stats = {

        "max_total_burden": {"patient": None, "value": -1},
        "min_total_burden": {"patient": None, "value": 999},

        "max_pdq8": {"patient": None, "value": -1},
        "min_pdq8": {"patient": None, "value": 999},

        "largest_motor_increase": {"patient": None, "value": -999},
        "largest_adl_increase": {"patient": None, "value": -999},
        "largest_nonmotor_increase": {"patient": None, "value": -999},
        "largest_pdq8_increase": {"patient": None, "value": -999},

        "fastest_motor_deterioration": {"patient": None, "slope": -999},
        "fastest_adl_deterioration": {"patient": None, "slope": -999},
        "fastest_nonmotor_deterioration": {"patient": None, "slope": -999},
        "fastest_qol_worsening": {"patient": None, "slope": -999},

        "most_stable_motor": {"patient": None, "slope": 999},
        "most_stable_qol": {"patient": None, "slope": 999},

        "most_stable_overall": {"patient": None, "score": 999},

        "avg_motor": 0,
        "avg_adl": 0,
        "avg_nonmotor": 0,
        "avg_pdq8": 0
    }


    motor_values = []
    adl_values = []
    nonmotor_values = []
    pdq8_values = []


    for pid, data in patients.items():

        motor = sorted(data["motor"], key=lambda x: x[0])
        adl = sorted(data["adl"], key=lambda x: x[0])
        nonmotor = sorted(data["nonmotor"], key=lambda x: x[0])
        total = sorted(data["total"], key=lambda x: x[0])
        pd = sorted(data["pdq8"], key=lambda x: x[0])


        for _, s in motor:
            motor_values.append(s)

        for _, s in adl:
            adl_values.append(s)

        for _, s in nonmotor:
            nonmotor_values.append(s)

        for _, s in pd:
            pdq8_values.append(s)


        # ---------- Max / Min total burden ----------

        if total:

            scores = [s for _, s in total]

            max_val = max(scores)
            if max_val > stats["max_total_burden"]["value"]:
                stats["max_total_burden"] = {"patient": pid, "value": max_val}

            min_val = min(scores)
            if min_val < stats["min_total_burden"]["value"]:
                stats["min_total_burden"] = {"patient": pid, "value": min_val}


        # ---------- QoL max/min ----------

        if pd:

            scores = [s for _, s in pd]

            max_val = max(scores)
            if max_val > stats["max_pdq8"]["value"]:
                stats["max_pdq8"] = {"patient": pid, "value": max_val}

            min_val = min(scores)
            if min_val < stats["min_pdq8"]["value"]:
                stats["min_pdq8"] = {"patient": pid, "value": min_val}


        p = progression(motor)
        if p:
            inc, slope = p

            if inc > stats["largest_motor_increase"]["value"]:
                stats["largest_motor_increase"] = {"patient": pid, "value": inc}

            if slope > stats["fastest_motor_deterioration"]["slope"]:
                stats["fastest_motor_deterioration"] = {"patient": pid, "slope": round(slope,2)}

            if abs(slope) < abs(stats["most_stable_motor"]["slope"]):
                stats["most_stable_motor"] = {"patient": pid, "slope": round(slope,2)}


        p = progression(adl)
        if p:
            inc, slope = p

            if inc > stats["largest_adl_increase"]["value"]:
                stats["largest_adl_increase"] = {"patient": pid, "value": inc}

            if slope > stats["fastest_adl_deterioration"]["slope"]:
                stats["fastest_adl_deterioration"] = {"patient": pid, "slope": round(slope,2)}


        p = progression(nonmotor)
        if p:
            inc, slope = p

            if inc > stats["largest_nonmotor_increase"]["value"]:
                stats["largest_nonmotor_increase"] = {"patient": pid, "value": inc}

            if slope > stats["fastest_nonmotor_deterioration"]["slope"]:
                stats["fastest_nonmotor_deterioration"] = {"patient": pid, "slope": round(slope,2)}


        # ---------- QoL progression ----------

        if len(pd) >= 2:

            first_v, first_s = pd[0]
            last_v, last_s = pd[-1]

            increase = last_s - first_s
            visit_diff = last_v - first_v
            slope = increase / visit_diff if visit_diff else 0

            if increase > stats["largest_pdq8_increase"]["value"]:
                stats["largest_pdq8_increase"] = {"patient": pid, "value": increase}

            if slope > stats["fastest_qol_worsening"]["slope"]:
                stats["fastest_qol_worsening"] = {"patient": pid, "slope": round(slope,2)}

            if abs(slope) < abs(stats["most_stable_qol"]["slope"]):
                stats["most_stable_qol"] = {"patient": pid, "slope": round(slope,2)}


        # ---------- Overall stability ----------

        if total and pd:

            t_first_v, t_first_s = total[0]
            t_last_v, t_last_s = total[-1]

            t_slope = (t_last_s - t_first_s) / (t_last_v - t_first_v) if (t_last_v - t_first_v) else 0

            p_first_v, p_first_s = pd[0]
            p_last_v, p_last_s = pd[-1]

            p_slope = (p_last_s - p_first_s) / (p_last_v - p_first_v) if (p_last_v - p_first_v) else 0

            overall = abs(t_slope) + abs(p_slope)

            if overall < stats["most_stable_overall"]["score"]:
                stats["most_stable_overall"] = {
                    "patient": pid,
                    "score": round(overall,2)
                }


    if motor_values:
        stats["avg_motor"] = round(sum(motor_values) / len(motor_values), 2)

    if adl_values:
        stats["avg_adl"] = round(sum(adl_values) / len(adl_values), 2)

    if nonmotor_values:
        stats["avg_nonmotor"] = round(sum(nonmotor_values) / len(nonmotor_values), 2)

    if pdq8_values:
        stats["avg_pdq8"] = round(sum(pdq8_values) / len(pdq8_values), 2)


    return stats

# ----------------------------------------------
def detect_patient_risk(facts: str, query: str):

    patients = {}
    current_patient = None

    for line in facts.split("\n"):

        line = line.strip()

        if line.startswith("PATIENT"):
            try:
                current_patient = int(line.split("PATIENT")[1].strip())
                patients[current_patient] = {
                    "updrs": [],
                    "pdq8": []
                }
            except:
                current_patient = None
            continue

        if current_patient is None:
            continue

        motor = None
        adl = None
        nonmotor = None

        m = re.search(r"Motor=(\d+)", line)
        if m:
            motor = int(m.group(1))

        m = re.search(r"ADL=(\d+)", line)
        if m:
            adl = int(m.group(1))

        m = re.search(r"NonMotor=(\d+)", line)
        if m:
            nonmotor = int(m.group(1))

        # --- UPDRS total ---
        if motor is not None or adl is not None or nonmotor is not None:
            up = (motor or 0) + (adl or 0) + (nonmotor or 0)
            patients[current_patient]["updrs"].append(up)

        # --- PDQ8 ---
        m = re.search(r"PDQ8=(\d+)", line)
        if m:
            patients[current_patient]["pdq8"].append(int(m.group(1)))


    q = query.lower()

    if "high risk" in q or "danger" in q or "extra care" in q:
        target = "HIGH"
    elif "moderate" in q or "monitor" in q:
        target = "MODERATE"
    elif "low risk" in q or "doing well" in q or "stable" in q:
        target = "LOW"
    else:
        target = "ALL"


    risk_report = []

    for pid, data in patients.items():

        up = data["updrs"]
        pd = data["pdq8"]

        last_up = up[-1] if up else None
        last_pd = pd[-1] if pd else None

        # ---- compute slopes ----
        up_slope = 0
        pd_slope = 0

        if len(up) >= 2:
            up_slope = (up[-1] - up[0]) / (len(up) - 1)

        if len(pd) >= 2:
            pd_slope = (pd[-1] - pd[0]) / (len(pd) - 1)

        # ---- risk scoring ----
        risk_score = 0

        # severity component
        if last_up is not None:
            if last_up >= 40:
                risk_score += 2
            elif last_up >= 25:
                risk_score += 1

        if last_pd is not None:
            if last_pd >= 15:
                risk_score += 2
            elif last_pd >= 10:
                risk_score += 1

        # progression component
        if up_slope > 2:
            risk_score += 2
        elif up_slope > 0.5:
            risk_score += 1

        if pd_slope > 2:
            risk_score += 2
        elif pd_slope > 0.5:
            risk_score += 1


        # ---- classify risk ----
        if risk_score >= 5:
            level = "HIGH RISK – rapid progression and high severity"

        elif risk_score >= 3:
            level = "MODERATE RISK – worsening symptoms, monitor closely"

        else:
            level = "LOW RISK – relatively stable condition"


        if target == "ALL" or level.startswith(target):

            risk_report.append(
                f"Patient {pid}: "
                f"UPDRS={last_up}, PDQ8={last_pd}, "
                f"UPDRS slope={round(up_slope,2)}, PDQ8 slope={round(pd_slope,2)} "
                f"→ {level}"
            )


    if not risk_report:
        return "No patients match the requested risk category."

    return "\n".join(risk_report)   

def interpret_cohort_stats(query, stats, metric):

    system = (
        "You are a clinical Parkinson's disease progression analyst.\n\n"
        "Baseline Rule:\n"
        "Visit 1 is always the BASELINE visit for every patient. All progression metrics "
        "(slopes, increases, deterioration rates) must be computed from and referenced "
        "against each patient's Visit 1 baseline scores.\n\n"

        "Use the cohort statistics to explain clinical progression.\n"
        "Rules:\n"
        "- Higher UPDRS means worse symptoms.\n"
        "- Higher PDQ8 means worse quality of life.\n"
        "- Use only the numbers provided.\n"
        "- Do not invent values."
    )

    user = (
        f"Scale Reference:\n{COMPARISON_SCALE_CONTEXT}\n\n"
        f"User question:\n{query}\n\n"
        f"Cohort statistics:\n{stats}\n\n"
        f"Primary metric requested:\n{metric}\n\n"
        "Explain clearly:\n"
        "- which patient is clinically highest risk\n"
        "- what evidence from UPDRS or PDQ8 trajectory supports it\n"
        "- which patient is most stable\n"
        "- what the overall cohort trend suggests\n\n"
        "Keep the explanation concise and clinical."
    )

    response = call_llm(system, user)

    return response
                