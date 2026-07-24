# app/graph.py
from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.agents.planner import plan_node
from app.retrieval.loader import retrieve_node
from app.agents.router import route_after_retrieve
from app.agents.motor import motor_agent
from app.agents.adl import adl_agent
from app.agents.nonmotor import nonmotor_agent
from app.agents.qol import qol_agent
from app.agents.comparison import comparison_agent
from app.agents.cohort import cohort_agent
from app.agents.final import final_agent

def build_agent():
    # ── Compile Graph ──────────────────────────────────────────
    workflow = StateGraph(AgentState)

    workflow.add_node("plan", plan_node)
    workflow.add_node("retrieve", retrieve_node)

    workflow.add_node("motor_agent", motor_agent)
    workflow.add_node("adl_agent", adl_agent)
    workflow.add_node("nonmotor_agent", nonmotor_agent)

    workflow.add_node("qol_agent", qol_agent)

    workflow.add_node("comparison_agent", comparison_agent)
    workflow.add_node("cohort_agent", cohort_agent)

    workflow.add_node("final_agent", final_agent)

    workflow.set_entry_point("plan")

    # ── Workflow Edges ──────────────────────────────────────────
    # Planning → Retrieve
    workflow.add_edge("plan", "retrieve")

    # Conditional routing after retrieve
    workflow.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "motor_agent": "motor_agent",
            "nonmotor_agent": "nonmotor_agent",
            "adl_agent": "adl_agent",
            "qol_agent": "qol_agent",
            "comparison_agent": "comparison_agent",
            "cohort_agent": "cohort_agent",
        },
    )

    # Domain agents → Final
    workflow.add_edge("motor_agent","adl_agent")
    workflow.add_edge("adl_agent","nonmotor_agent")
    workflow.add_edge("nonmotor_agent","qol_agent")
    workflow.add_edge("qol_agent","final_agent")

    # Other pipelines → Final
    workflow.add_edge("comparison_agent", "final_agent")
    workflow.add_edge("cohort_agent", "final_agent")

    # Final → END
    workflow.add_edge("final_agent", END)

    agent = workflow.compile()
    print("Agent compiled.")
    
    return workflow.compile()