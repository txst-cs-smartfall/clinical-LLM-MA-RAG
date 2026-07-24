# app/context/scale_contexts.py
# ── Static clinical scale context — sourced from Goetz et al. (2008) UPDRS
# and Peto et al. (1995) PDQ-39 validation paper ──────────────────────────────

MOTOR_SCALE_CONTEXT = """
UPDRS Part III – Motor Examination:
- Each item rated 0–4: 0=Normal, 1=Slight, 2=Mild, 3=Moderate, 4=Severe.
  - Slight (1): symptoms present but no functional impact.
  - Mild (2): symptoms cause modest functional impact.
  - Moderate (3): symptoms impact function considerably but do not prevent it.
  - Severe (4): symptoms prevent function.
- Part III contains 33 scores derived from 18 items (several rated per limb/side).
- Higher scores = worse motor function. Parts should be reported separately; 
  a combined total UPDRS score is NOT recommended.
- Observed mean score in validation cohort (n=877): 36.8 (SD 18.4).
- Seven clinical factor domains identified by factor analysis:
  1. Midline function: Speech, Facial expression, Arising from chair, Gait,
     Freezing of gait, Postural stability, Posture, Global spontaneity of movement.
  2. Rest tremor: Rest tremor amplitude (RUE, LUE, RLE, LLE, lip/jaw),
     Constancy of rest tremor.
  3. Rigidity: Neck, RUE, LUE, RLE, LLE.
  4. Right upper limb bradykinesia: Finger tapping, Hand movements,
     Pronation/supination (right).
  5. Left upper limb bradykinesia: Finger tapping, Hand movements,
     Pronation/supination (left).
  6. Postural/kinetic tremor: Postural tremor (R/L), Kinetic tremor (R/L).
  7. Lower limb bradykinesia: Toe tapping (R/L), Leg agility (R/L).
- Internal consistency: Cronbach's alpha = 0.93.
"""

ADL_SCALE_CONTEXT = """
UPDRS Part II – Motor Aspects of Experiences of Daily Living:
- Each item rated 0–4: 0=Normal, 1=Slight, 2=Mild, 3=Moderate, 4=Severe.
  - Slight (1): symptoms present but no functional impact.
  - Mild (2): symptoms cause modest functional impact.
  - Moderate (3): symptoms impact function considerably but do not prevent it.
  - Severe (4): symptoms prevent function.
- Part II contains 13 items, completed by patient/caregiver without investigator input.
- Higher scores = worse daily functioning. Parts should be reported separately.
- Observed mean score in validation cohort (n=877): 16.0 (SD 10.0).
- Three clinical factor domains identified:
  1. Fine motor/communication: Speech, Saliva and drooling, Chewing and swallowing,
     Handwriting, Doing hobbies and other activities.
  2. Tremor/eating: Eating tasks, Tremor.
  3. Gross motor/mobility: Dressing, Hygiene, Turning in bed, Getting out of bed/car,
     Walking and balance, Freezing.
- Internal consistency: Cronbach's alpha = 0.90.
"""

NONMOTOR_SCALE_CONTEXT = """
UPDRS Part I – Non-Motor Experiences of Daily Living:
- Each item rated 0–4: 0=Normal, 1=Slight, 2=Mild, 3=Moderate, 4=Severe.
  - Slight (1): symptoms present but no functional impact.
  - Mild (2): symptoms cause modest functional impact.
  - Moderate (3): symptoms impact function considerably but do not prevent it.
  - Severe (4): symptoms prevent function.
- Part I contains 13 items. Some items completed by patient/caregiver; others
  require investigator interview (complex behaviors).
- Higher scores = worse non-motor burden. Parts should be reported separately.
- Observed mean score in validation cohort (n=877): 11.5 (SD 7.0).
- Two clinical factor domains identified:
  1. Autonomic/cognitive non-motor burden: Daytime sleepiness, Sleep problems,
     Cognitive impairment, Pain and other sensations, Hallucinations and psychosis,
     Urinary problems, Constipation problems, Features of dopamine dysregulation
     syndrome (DDS), Lightheadedness on standing, Fatigue.
  2. Mood/affect: Depressed mood, Anxious mood, Apathy.
- Internal consistency: Cronbach's alpha = 0.79.
"""

QOL_SCALE_CONTEXT = """
PDQ – Parkinson's Disease Questionnaire:
- NOTE: The PDQ-8 is a short-form derivative; the scoring method below applies to the PDQ-8 by analogy.
- Each item rated 0–4: 0=Never, 1=Occasionally, 2=Sometimes, 3=Often, 4=Always.
- Scale score formula: (sum of raw item scores / maximum possible raw score) × 100.
  - For PDQ-8: max possible raw score = 32 (8 items × 4).
  - Result expressed as a summary index from 0 (no problem) to 100 (maximum problem).
- Higher scores = WORSE quality of life.
- PDQ-8 items (derived from PDQ-39 dimensions):
  1. Difficulty going out in public (Mobility dimension)
  2. Difficulty dressing yourself (Activities of Daily Living dimension)
  3. Feeling depressed (Emotional Well-being dimension)
  4. Problems with close relationships (Social Support dimension)
  5. Problems with concentration (Cognitions dimension)
  6. Problems communicating with others (Communication dimension)
  7. Painful muscle cramps or spasms (Bodily Discomfort dimension)
  8. Feeling embarrassed in public (Stigma dimension)
- Internal consistency for PDQ-39 scales: Cronbach's alpha range 0.69–0.95.
- Test-retest reliability: all scales significant at p < 0.001 over a 36-day interval.
- A consistent pattern: higher PDQ scores are associated with more severe PD symptoms
  (tremor, stiffness, slowness) across all dimensions.
"""

COMPARISON_SCALE_CONTEXT = f"{MOTOR_SCALE_CONTEXT}\n{ADL_SCALE_CONTEXT}\n{NONMOTOR_SCALE_CONTEXT}\n{QOL_SCALE_CONTEXT}"