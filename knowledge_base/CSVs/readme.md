# Clinician Summary CSVs

This folder contains raw clinician-generated summaries exported as CSV files. The files are organized by instrument and by comparison type.

## Folder layout

```text
CSVs/
├── PDQ-8/
│   ├── PDQ8_UPDRS_one2one_summaries.csv
│   └── PDQ8_UPDRS_one2all_summaries.csv
└── UPDRS/
    ├── UPDRS_one2one_summaries.csv
    └── UPDRS_one2all_summaries.csv
```

## File descriptions

- `UPDRS/UPDRS_one2one_summaries.csv`  
  Contains clinician summaries based **only on UPDRS** data for one patient at a time (non‑motor, ADL, and motor domains).  
  Columns include individual UPDRS item scores and their corresponding domain totals.

- `UPDRS/UPDRS_one2all_summaries.csv`  
  Contains longitudinal UPDRS‑only summaries comparing one patient to the rest of the cohort.  
  Columns include per‑visit UPDRS item scores, domain totals, and cohort‑level comparison metrics.

- `PDQ-8/PDQ8_UPDRS_one2one_summaries.csv`  
  Contains one‑to‑one summaries that include **both UPDRS and PDQ‑8** for a single patient.  
  Columns include:
  - UPDRS item scores and domain totals (non‑motor, ADL, motor).  
  - PDQ‑8 item scores and the PDQ‑8 total quality‑of‑life score.

- `PDQ-8/PDQ8_UPDRS_one2all_summaries.csv`  
  Contains longitudinal summaries where **UPDRS and PDQ‑8 are jointly analyzed** for one patient versus all others.  
  Columns include:
  - Per‑visit UPDRS item scores and domain totals.  
  - Per‑visit PDQ‑8 item scores and PDQ‑8 totals.  
  - Combined analysis summaries describing joint UPDRS–PDQ‑8 trajectories and cohort comparisons.

## Column label maps
For deterministic reasoning, these column labels are mapped exactly as specified in `app/context/label_maps.py`, ensuring a one‑to‑one correspondence  in the retrieved records.

### UPDRS columns

UPDRS item columns use the following labels:

- **Non‑motor (13 items)**  
  - `COGNITION`: Cognition  
  - `HALLUCINATION`: Hallucinations and psychosis  
  - `DEPRESSED`: Depressed mood  
  - `ANXIOUS`: Anxiety  
  - `APATHY`: Apathy  
  - `DYSREGULATION`: Impulse control / dysregulation  
  - `SLEEP_PROB`: Sleep problems  
  - `DAY_SLEEPY`: Daytime sleepiness  
  - `PAIN`: Pain  
  - `URINARY_PROB`: Urinary problems  
  - `CONSTIPATION_PROB`: Constipation  
  - `LIGHT_HEADED`: Lightheadedness  
  - `FATIGUE`: Fatigue  

- **ADL (15 items)**  
  - `SPEECH_PROB`: Speech difficulty  
  - `SALIVA_PROB`: Excess saliva / drooling  
  - `CHEW_SWALLOW_PROB`: Chewing and swallowing difficulty  
  - `EATING_PROB`: Eating difficulty  
  - `DRESSING_PROB`: Dressing difficulty  
  - `SALIVATION_PROB`: Salivation problems  
  - `SWALLOW_PROB`: Swallowing problems  
  - `HANDWRITING_PROB`: Handwriting difficulty  
  - `CUT_FOOD_PROB`: Cutting food difficulty  
  - `DRESS_PROB`: Dressing problems  
  - `HYGIENE_PROB`: Personal hygiene difficulty  
  - `BED_TURN_PROB`: Turning in bed difficulty  
  - `FALL_PROB`: Falls  
  - `FREEZE_GAIT_PROB`: Freezing of gait  
  - `WALKING_PROB`: Walking difficulty  

- **Motor examination (16 items)**  
  - `TREMOR_PROB`: Rest tremor  
  - `SENSITIVITY_PROB`: Sensory complaints  
  - `SPEECH_PROB.1`: Speech impairment (motor exam)  
  - `FACIAL_PROB`: Facial expression (hypomimia)  
  - `RESTING_TREMOR_PROB`: Resting tremor  
  - `POSTURAL_TREMOR`: Postural tremor  
  - `RIGIDITY_PROB`: Rigidity  
  - `FINGER_TAP_PROB`: Finger tapping  
  - `HAND_MOVEMENT_PROB`: Hand movements  
  - `RA_OD_ALT_PROB`: Rapid alternating movements of hands  
  - `LEG_AGILITY_PROB`: Leg agility  
  - `CHAIR_RISE_PROB`: Rising from chair  
  - `POSTURE_PROB`: Posture  
  - `GAIT_PROB`: Gait  
  - `POS_STABILITY_PROB`: Postural stability  
  - `BRADYKINESIA_PROB`: Bradykinesia  

Each CSV includes corresponding domain total columns (e.g., non‑motor total, ADL total, motor total).

### PDQ‑8 columns

PDQ‑8 item and total columns use:

- `DIFF_PUB`: Difficulty going out in public  
- `DIFF_DRESS`: Difficulty dressing  
- `DEPRESSED`: Feeling depressed  
- `PROB_RELATE`: Problems with close relationships  
- `PROB_CONCENTRATION`: Problems with concentration  
- `PROB_COMMUNICATE`: Problems with communication  
- `MS_PROB_SPASMS`: Painful muscle spasms  
- `EMBARESSED`: Embarrassment in social situations  
- `PDQ_8_TOTAL`: PDQ‑8 total quality of life score  