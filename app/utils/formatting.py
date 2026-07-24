import re
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# STEP 2: Helper functions
# ─────────────────────────────────────────────────────────────

def fmt_items(d: dict, label_map: dict) -> str:
    return ", ".join(
        f"{label_map.get(col, col)}={v}"
        for col, v in d.items()
    )
    
# ───────────────────────────────────────── 
def build_score_table(facts: str) -> str:
    """
    Parses extracted_facts and returns a compact per-visit cross-domain
    score table with pre-computed incongruence flags.
    Used by _final_domain_summary and _final_single_session_summary.
    """
    lines = ["VISIT-BY-VISIT SCORE SUMMARY (use this to verify all cross-domain claims):"]
    lines.append(f"{'Visit':<8}{'Date':<14}{'Motor':<8}{'ADL':<8}{'NonMotor':<11}{'PDQ8':<6}  Flags")
    lines.append("-" * 70)

    current_pid = None

    for line in facts.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("PATIENT"):
            current_pid = line
            lines.append(f"\n{current_pid}")
            continue

        visit_m  = re.search(r"Visit (\d+) \(([^)]+)\)", line)
        motor_m  = re.search(r"\bMotor=(\d+)", line)
        adl_m    = re.search(r"\bADL=(\d+)", line)
        nm_m     = re.search(r"\bNonMotor=(\d+)", line)
        pdq8_m   = re.search(r"\bPDQ8=(\d+)", line)

        if not visit_m:
            continue

        vnum  = visit_m.group(1)
        vdate = visit_m.group(2)
        motor = int(motor_m.group(1)) if motor_m else "N/A"
        adl   = int(adl_m.group(1))   if adl_m   else "N/A"
        nm    = int(nm_m.group(1))     if nm_m    else "N/A"
        pdq8  = int(pdq8_m.group(1))  if pdq8_m  else "N/A"

        flags = []

        # Incongruence: PDQ8=0 while UPDRS domains are elevated
        if pdq8 == 0 and all(isinstance(x, int) for x in [motor, adl, nm]):
            updrs_total = motor + adl + nm
            if updrs_total > 15:
                flags.append(
                    f"⚠ INCONGRUENCE: PDQ8=0 while UPDRS total={updrs_total} "
                    f"(Motor={motor}, ADL={adl}, NonMotor={nm}) — "
                    f"possible under-reporting or measurement artifact"
                )

        # Floor effect: all UPDRS domains = 0
        if all(x == 0 for x in [motor, adl, nm] if isinstance(x, int)):
            flags.append("⚠ FLOOR EFFECT: Motor=ADL=NonMotor=0 — complete resolution uncommon in PD")

        flag_str = "  |  ".join(flags) if flags else ""
        lines.append(
            f"V{vnum:<7}{vdate:<14}{str(motor):<8}{str(adl):<8}"
            f"{str(nm):<11}{str(pdq8):<6}  {flag_str}"
        )

    return "\n".join(lines)

# ── ─────────────────────
def split_facts_by_domain(facts: str):
    motor_lines    = []
    adl_lines      = []
    nonmotor_lines = []
    qol_lines      = []

    for line in facts.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("PATIENT"):
            motor_lines.append(line)
            adl_lines.append(line)
            nonmotor_lines.append(line)
            qol_lines.append(line)
            continue

        visit_match = re.search(r"(Visit\s+\d+\s*\([^)]+\)):", line)
        if not visit_match:
            continue

        prefix = visit_match.group(1) + ":"

        motor    = re.search(r"\bMotor=(\d+)", line)
        adl      = re.search(r"\bADL=(\d+)", line)
        nonmotor = re.search(r"\bNonMotor=(\d+)", line)
        pdq8     = re.search(r"\bPDQ8=(\d+)", line)

        motor_raw_match    = re.search(r"\|\s*(MotorItems=[^|]+)", line)
        adl_raw_match      = re.search(r"\|\s*(ADLItems=[^|]+)", line)
        nonmotor_raw_match = re.search(r"\|\s*(NonMotorItems=[^|]+)", line)
        pdq8_items_match   = re.search(r"\|\s*(PDQ8Items=[^|]+)", line)

        if motor:
            detail = f" | {motor_raw_match.group(1).strip()}" if motor_raw_match else ""
            motor_lines.append(f"{prefix} Motor={motor.group(1)}{detail}")

        if adl:
            detail = f" | {adl_raw_match.group(1).strip()}" if adl_raw_match else ""
            adl_lines.append(f"{prefix} ADL={adl.group(1)}{detail}")

        if nonmotor:
            detail = f" | {nonmotor_raw_match.group(1).strip()}" if nonmotor_raw_match else ""
            nonmotor_lines.append(f"{prefix} NonMotor={nonmotor.group(1)}{detail}")

        if pdq8:
            detail = f" | {pdq8_items_match.group(1).strip()}" if pdq8_items_match else ""
            qol_lines.append(f"{prefix} PDQ8={pdq8.group(1)}{detail}")

    return (
        "\n".join(motor_lines),
        "\n".join(adl_lines),
        "\n".join(nonmotor_lines),
        "\n".join(qol_lines),
    )
    
# ----------------------------------------------------
def apply_visit_filter(facts: str, filter_type: str):

    if filter_type == "none":
        return facts

    patients = {}
    current_patient = None

    for line in facts.split("\n"):

        line = line.strip()

        if line.startswith("PATIENT"):
            current_patient = line
            patients[current_patient] = []
            continue

        if current_patient and line.startswith("Visit"):
            patients[current_patient].append(line)

    output = []

    for p, visits in patients.items():

        output.append(p)

        if not visits:
            output.append("")
            continue

        if filter_type == "baseline":
            output.append(visits[0])

        elif filter_type == "latest_visit":
            output.append(visits[-1])

        elif filter_type == "baseline_vs_latest":
            output.append(visits[0])
            if len(visits) > 1:
                output.append(visits[-1])

        # ---- Dynamic first_N_visits ----
        elif re.match(r"^first_(\d+)_visits$", filter_type):
            n = int(re.match(r"^first_(\d+)_visits$", filter_type).group(1))
            output.extend(visits[:n])

        # ---- Dynamic last_N_visits ----
        elif re.match(r"^last_(\d+)_visits$", filter_type):
            n = int(re.match(r"^last_(\d+)_visits$", filter_type).group(1))
            output.extend(visits[-n:])

        else:
            output.extend(visits)

        output.append("")

    return "\n".join(output)    

def split_facts_by_domain(facts: str):
    motor_lines    = []
    adl_lines      = []
    nonmotor_lines = []
    qol_lines      = []

    for line in facts.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("PATIENT"):
            motor_lines.append(line)
            adl_lines.append(line)
            nonmotor_lines.append(line)
            qol_lines.append(line)
            continue

        visit_match = re.search(r"(Visit\s+\d+\s*\([^)]+\)):", line)
        if not visit_match:
            continue

        prefix = visit_match.group(1) + ":"

        motor    = re.search(r"\bMotor=(\d+)", line)
        adl      = re.search(r"\bADL=(\d+)", line)
        nonmotor = re.search(r"\bNonMotor=(\d+)", line)
        pdq8     = re.search(r"\bPDQ8=(\d+)", line)

        motor_raw_match    = re.search(r"\|\s*(MotorItems=[^|]+)", line)
        adl_raw_match      = re.search(r"\|\s*(ADLItems=[^|]+)", line)
        nonmotor_raw_match = re.search(r"\|\s*(NonMotorItems=[^|]+)", line)
        pdq8_items_match   = re.search(r"\|\s*(PDQ8Items=[^|]+)", line)

        if motor:
            detail = f" | {motor_raw_match.group(1).strip()}" if motor_raw_match else ""
            motor_lines.append(f"{prefix} Motor={motor.group(1)}{detail}")

        if adl:
            detail = f" | {adl_raw_match.group(1).strip()}" if adl_raw_match else ""
            adl_lines.append(f"{prefix} ADL={adl.group(1)}{detail}")

        if nonmotor:
            detail = f" | {nonmotor_raw_match.group(1).strip()}" if nonmotor_raw_match else ""
            nonmotor_lines.append(f"{prefix} NonMotor={nonmotor.group(1)}{detail}")

        if pdq8:
            detail = f" | {pdq8_items_match.group(1).strip()}" if pdq8_items_match else ""
            qol_lines.append(f"{prefix} PDQ8={pdq8.group(1)}{detail}")

    return (
        "\n".join(motor_lines),
        "\n".join(adl_lines),
        "\n".join(nonmotor_lines),
        "\n".join(qol_lines),
    )
    
    