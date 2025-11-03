from langgraph.graph import StateGraph, START
from schemas import MeetingInput
from typing import Dict, List
from utils.tools import now_iso

class MeetingState(MeetingInput):
    schedule: str = ""
    metadata: dict | None = None

def planner(state: MeetingState) -> dict:
    return {
        "title": state.title,
        "agenda": state.agenda or "General",
        "participants": state.participants or [],
        "date": state.date or "TBD"
    }

def scheduler(state: MeetingState) -> dict:
    participants_str = ", ".join(state.participants) if state.participants else "No attendees"
    schedule = f"{state.title} - {state.agenda} on {state.date} with {participants_str}"
    return {"schedule": schedule}

def add_metadata(state: MeetingState) -> dict:
    return {"metadata": {"scheduled_at": now_iso()}}

def create_meeting_scheduler():
    graph = StateGraph(MeetingState)
    graph.add_node("planner", planner)
    graph.add_node("scheduler", scheduler)
    graph.add_node("finalize", add_metadata)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "scheduler")
    graph.add_edge("scheduler", "finalize")
    return graph.compile()

_scheduler = None

def get_meeting_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = create_meeting_scheduler()
    return _scheduler

def meeting_scheduler_agent(payload: Dict) -> Dict:
    MeetingInput(**payload)
    app = get_meeting_scheduler()
    result = app.invoke(payload)
    return {
        "title": result.get("title", "Team Meeting"),
        "agenda": result.get("agenda", "General"),
        "participants": result.get("participants", []),
        "date": result.get("date", "TBD"),
        "schedule": result["schedule"],
        "metadata": result.get("metadata", {})
    }