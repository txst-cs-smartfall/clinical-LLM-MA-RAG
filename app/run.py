# app/run.py
from langchain_core.messages import HumanMessage
from app.graph import build_agent

agent = build_agent()

def run_query(query: str):
    return agent.invoke({
        "query": query,
        "messages": [HumanMessage(content=query)],
        "retrieved_contexts": [],
        "extracted_facts": "",
        "motor_facts": "",
        "adl_facts": "",
        "nonmotor_facts": "",
        "qol_facts": "",
        "analysis_plan": "",
        "motor_response": "",
        "adl_response": "",
        "nonmotor_response": "",
        "qol_response": "",
        "comparison_response": "",
        "cohort_response": "",
        "final_answer": ""
    })
    
    