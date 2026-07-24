# app/context/label_maps.py

# ─────────────────────────────────────────────────────────────
# STEP 1: Label Maps (paste once near top of inference script,
#         after imports, before any functions)
# ─────────────────────────────────────────────────────────────

UPDRS_LABEL_MAP = {
    # Non-motor: 13 total
    "COGNITION":           "Cognition",
    "HALLUCINATION":       "Hallucinations and psychosis",
    "DEPRESSED":           "Depressed mood",
    "ANXIOUS":             "Anxiety",
    "APATHY":              "Apathy",
    "DYSREGULATION":       "Impulse control / dysregulation",
    "SLEEP_PROB":          "Sleep problems",
    "DAY_SLEEPY":          "Daytime sleepiness",
    "PAIN":                "Pain",
    "URINARY_PROB":        "Urinary problems",
    "CONSTIPATION_PROB":   "Constipation",
    "LIGHT_HEADED":        "Lightheadedness",
    "FATIGUE":             "Fatigue",
    # ADL: 15 total
    "SPEECH_PROB":         "Speech difficulty",
    "SALIVA_PROB":         "Excess saliva / drooling",
    "CHEW_SWALLOW_PROB":   "Chewing and swallowing difficulty",
    "EATING_PROB":         "Eating difficulty",
    "DRESSING_PROB":       "Dressing difficulty",
    "SALIVATION_PROB":     "Salivation problems",
    "SWALLOW_PROB":        "Swallowing problems",
    "HANDWRITING_PROB":    "Handwriting difficulty",
    "CUT_FOOD_PROB":       "Cutting food difficulty",
    "DRESS_PROB":          "Dressing problems",
    "HYGIENE_PROB":        "Personal hygiene difficulty",
    "BED_TURN_PROB":       "Turning in bed difficulty",
    "FALL_PROB":           "Falls",
    "FREEZE_GAIT_PROB":    "Freezing of gait",
    "WALKING_PROB":        "Walking difficulty",
    # Motor: 16 total
    "TREMOR_PROB":         "Rest tremor",
    "SENSITIVITY_PROB":    "Sensory complaints",
    "SPEECH_PROB.1":       "Speech impairment (motor exam)",
    "FACIAL_PROB":         "Facial expression (hypomimia)",
    "RESTING_TREMOR_PROB": "Resting tremor",
    "POSTURAL_TREMOR":     "Postural tremor",
    "RIGIDITY_PROB":       "Rigidity",
    "FINGER_TAP_PROB":     "Finger tapping",
    "HAND_MOVEMENT_PROB":  "Hand movements",
    "RA_OD_ALT_PROB":      "Rapid alternating movements of hands",
    "LEG_AGILITY_PROB":    "Leg agility",
    "CHAIR_RISE_PROB":     "Rising from chair",
    "POSTURE_PROB":        "Posture",
    "GAIT_PROB":           "Gait",
    "POS_STABILITY_PROB":  "Postural stability",
    "BRADYKINESIA_PROB":   "Bradykinesia",
}

PDQ8_LABEL_MAP = {
    # QoL: 8 items in total excluding the total
    "DIFF_PUB":            "Difficulty going out in public",
    "DIFF_DRESS":          "Difficulty dressing",
    "DEPRESSED":           "Feeling depressed",
    "PROB_RELATE":         "Problems with close relationships",
    "PROB_CONCENTRATION":  "Problems with concentration",
    "PROB_COMMUNICATE":    "Problems with communication",
    "MS_PROB_SPASMS":      "Painful muscle spasms",
    "EMBARESSED":          "Embarrassment in social situations",
    "PDQ_8_TOTAL":         "PDQ-8 total quality of life score",
}

# Inverse maps — derived once, never recomputed inside functions
UPDRS_LABEL_TO_COL = {v: k for k, v in UPDRS_LABEL_MAP.items()}
PDQ8_LABEL_TO_COL  = {v: k for k, v in PDQ8_LABEL_MAP.items()}