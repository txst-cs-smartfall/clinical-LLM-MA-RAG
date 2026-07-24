# app/state.py
from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    query: str
    analysis_plan: str
    intent: str
    domains: List[str]
    scales: List[str]
    retrieved_contexts: List[str]
    extracted_facts: str
    motor_facts: str
    adl_facts: str
    nonmotor_facts: str
    qol_facts: str
    motor_response: str
    adl_response: str
    nonmotor_response: str
    qol_response: str
    comparison_response: str
    cohort_response: str
    final_answer: str
    messages: Annotated[List, operator.add]
    