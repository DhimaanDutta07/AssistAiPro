from langgraph.graph import StateGraph, START
from schemas import LeaveInput
from typing import Dict
from utils.tools import now_iso

class LeaveState(LeaveInput):
    approved: bool = False
    metadata: dict | None = None

def verify_balance(state: LeaveState) -> dict:
    return {"balance": state.balance, "days_requested": state.days_requested}

def approve_leave(state: LeaveState) -> dict:
    return {"approved": state.days_requested <= state.balance}

def add_metadata(state: LeaveState) -> dict:
    return {"metadata": {"processed_at": now_iso()}}

def create_leave_processor():
    graph = StateGraph(LeaveState)
    graph.add_node("verify", verify_balance)
    graph.add_node("approve", approve_leave)
    graph.add_node("finalize", add_metadata)
    graph.add_edge(START, "verify")
    graph.add_edge("verify", "approve")
    graph.add_edge("approve", "finalize")
    return graph.compile()

_processor = None

def get_leave_processor():
    global _processor
    if _processor is None:
        _processor = create_leave_processor()
    return _processor

def leave_processor_agent(payload: Dict) -> Dict:
    LeaveInput(**payload)
    app = get_leave_processor()
    result = app.invoke(payload)
    return {
        "balance": result["balance"],
        "days_requested": result["days_requested"],
        "approved": result["approved"],
        "metadata": result.get("metadata", {})
    }