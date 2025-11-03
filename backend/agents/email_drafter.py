from langgraph.graph import StateGraph, START
from pydantic import BaseModel
from typing import Dict
from utils.cohere_integration import get_llm

llm = get_llm()

class EmailState(BaseModel):
    query: str
    plan: str = ""
    draft: str = ""
    polished: str = ""

def planner(state: EmailState) -> dict:
    response = llm.invoke(f"Create a short plan for writing an email about: {state.query}")
    return {"plan": response.content if hasattr(response, 'content') else str(response)}

def drafter(state: EmailState) -> dict:
    response = llm.invoke(f"Write an email according to this plan:\n{state.plan}")
    return {"draft": response.content if hasattr(response, 'content') else str(response)}

def polisher(state: EmailState) -> dict:
    response = llm.invoke(f"Polish this email professionally:\n{state.draft}")
    return {"polished": response.content if hasattr(response, 'content') else str(response)}

def create_email_graph():
    graph = StateGraph(EmailState)
    graph.add_node("planner", planner)
    graph.add_node("drafter", drafter)
    graph.add_node("polisher", polisher)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "drafter")
    graph.add_edge("drafter", "polisher")
    return graph.compile()

_email_graph = None

def get_email_graph():
    global _email_graph
    if _email_graph is None:
        _email_graph = create_email_graph()
    return _email_graph

def auto_email_agent(payload: Dict) -> Dict:
    query = payload.get("query", "")
    if not query:
        raise ValueError("Missing 'query' in payload")

    state = EmailState(query=query)
    app = get_email_graph()
    result = app.invoke(state.dict())

    return {
        "polished": result["polished"]
    }
