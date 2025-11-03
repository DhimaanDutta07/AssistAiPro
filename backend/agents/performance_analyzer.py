from langgraph.graph import StateGraph, START
from pydantic import BaseModel
from typing import Dict
from utils.cohere_integration import get_llm
import random
import datetime

llm = get_llm()

class PerformanceState(BaseModel):
    query: str
    metrics: dict = {}
    scores: dict = {}
    feedback: str = ""

def generate_metrics(state: PerformanceState) -> dict:
    prompt = f"Generate realistic performance metrics for an employee based on this query: {state.query}. Output as JSON with keys: kpi (0-100), attendance (0-100), leaves_taken (0-30), tasks_assigned (10-50), tasks_done (0-tasks_assigned), on_time_tasks (0-tasks_done), quality_score (0-100), team_feedback (0-100), training_hours (0-50), client_satisfaction (0-100), innovation_ideas (0-10), overtime_hours (0-50)."
    response = llm.invoke(prompt)
    try:
        metrics = eval(response.content if hasattr(response, 'content') else str(response))
    except:
        # Fallback to random realistic values if LLM fails
        metrics = {
            "kpi": random.randint(60, 95),
            "attendance": random.randint(80, 100),
            "leaves_taken": random.randint(0, 15),
            "tasks_assigned": random.randint(20, 40),
            "tasks_done": random.randint(15, 35),
            "on_time_tasks": random.randint(10, 30),
            "quality_score": random.randint(70, 95),
            "team_feedback": random.randint(65, 90),
            "training_hours": random.randint(5, 30),
            "client_satisfaction": random.randint(70, 95),
            "innovation_ideas": random.randint(0, 5),
            "overtime_hours": random.randint(0, 20)
        }
    return {"metrics": metrics}

def analyze_scores(state: PerformanceState) -> dict:
    metrics = state.metrics
    completion_rate = (metrics["tasks_done"] / metrics["tasks_assigned"] * 100) if metrics["tasks_assigned"] > 0 else 0
    on_time_rate = (metrics["on_time_tasks"] / metrics["tasks_done"] * 100) if metrics["tasks_done"] > 0 else 0
    leaves_penalty = max(0, metrics["leaves_taken"] - 5) * 2
    training_bonus = min(metrics["training_hours"] / 10, 5)
    innovation_bonus = min(metrics["innovation_ideas"] * 2, 10)
    overtime_penalty = max(0, metrics["overtime_hours"] - 20) * 0.5

    overall_score = (metrics["kpi"] * 0.3) + (metrics["attendance"] * 0.15) + (completion_rate * 0.1) + (on_time_rate * 0.1) + (metrics["quality_score"] * 0.1) + (metrics["team_feedback"] * 0.05) + (metrics["client_satisfaction"] * 0.05) + training_bonus + innovation_bonus - leaves_penalty - overtime_penalty
    overall_score = max(0, min(100, round(overall_score, 2)))

    rating = "Excellent" if overall_score >= 90 else "Good" if overall_score >= 70 else "Average" if overall_score >= 50 else "Needs Improvement"

    scores = {
        "completion_rate": round(completion_rate, 2),
        "on_time_rate": round(on_time_rate, 2),
        "overall_score": overall_score,
        "rating": rating
    }
    return {"scores": scores}

def generate_feedback(state: PerformanceState) -> dict:
    prompt = f"Generate professional, constructive feedback based on these metrics and scores: {state.metrics}, {state.scores}. Include strengths, areas for improvement, and suggestions. Keep it concise, around 100-150 words."
    response = llm.invoke(prompt)
    return {"feedback": response.content if hasattr(response, 'content') else str(response)}

def create_performance_graph():
    graph = StateGraph(PerformanceState)
    graph.add_node("generate_metrics", generate_metrics)
    graph.add_node("analyze_scores", analyze_scores)
    graph.add_node("generate_feedback", generate_feedback)
    graph.add_edge(START, "generate_metrics")
    graph.add_edge("generate_metrics", "analyze_scores")
    graph.add_edge("analyze_scores", "generate_feedback")
    return graph.compile()

_performance_graph = None

def get_performance_graph():
    global _performance_graph
    if _performance_graph is None:
        _performance_graph = create_performance_graph()
    return _performance_graph

def performance_analyzer_agent(payload: Dict) -> Dict:
    query = payload.get("query", "")
    if not query:
        raise ValueError("Missing 'query' in payload")

    state = PerformanceState(query=query)
    app = get_performance_graph()
    result = app.invoke(state.dict())

    return {
        **result["metrics"],
        **result["scores"],
        "feedback": result["feedback"]
    }