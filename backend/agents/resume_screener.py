from langgraph.graph import StateGraph, END
from langchain_cohere import ChatCohere
from langchain_community.document_loaders import PyPDFLoader
from typing import Dict, TypedDict, List
import os, tempfile, json

llm = ChatCohere(cohere_api_key=os.getenv("COHERE_API_KEY"))

class ResumeState(TypedDict, total=False):
    resume_bytes: bytes
    resume_text: str
    metrics: List[Dict]
    valuation: str
    error: str

def extract_text(state: ResumeState) -> ResumeState:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(state["resume_bytes"])
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        text = "\n".join(p.page_content for p in pages)
        os.unlink(tmp_path)

        return {"resume_text": text}
    except Exception as e:
        return {"error": f"PDF extraction failed: {str(e)}"}

def analyze_resume(state: ResumeState) -> ResumeState:
    if state.get("error"):
        return state

    prompt = f"""
You are an expert resume evaluation system. Analyze the following resume and return only valid JSON using this exact structure:

{{
  "metrics": [
    {{"name": "Years of Experience", "value": "5+", "icon": "experience"}},
    {{"name": "Key Skills", "value": "Python, Flask, AI Agents", "icon": "skills"}},
    {{"name": "Education Level", "value": "Bachelor’s in Computer Science", "icon": "education"}},
    {{"name": "Certifications", "value": "AWS Certified, Data Science Pro", "icon": "certifications"}},
    {{"name": "Languages Known", "value": "English, Hindi, French", "icon": "languages"}},
    {{"name": "Projects Completed", "value": "12+", "icon": "projects"}},
    {{"name": "Technical Proficiency", "value": "Advanced", "icon": "tech"}},
    {{"name": "Soft Skills", "value": "Leadership, Communication", "icon": "softskills"}},
    {{"name": "Industry Domain", "value": "Software Development", "icon": "domain"}},
    {{"name": "Achievements", "value": "Best Developer 2023", "icon": "achievements"}}
  ],
  "valuation": "A 4–5 line professional summary including an estimated salary range, market worth, and career growth outlook."
}}

Resume Text:
{state["resume_text"]}
"""

    try:
        resp = llm.invoke(prompt)
        raw = getattr(resp, "content", None)
        if not raw or not raw.strip():
            return {"error": "Empty response from LLM"}

        json_start = raw.find('{')
        json_end = raw.rfind('}') + 1
        json_str = raw[json_start:json_end].strip()
        data = json.loads(json_str)

        return {
            "metrics": data.get("metrics", []),
            "valuation": data.get("valuation", "")
        }
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON returned by model: {e}"}
    except Exception as e:
        return {"error": f"LLM parsing failed: {str(e)}"}

graph = StateGraph(ResumeState)
graph.add_node("extract", extract_text)
graph.add_node("analyze", analyze_resume)
graph.add_edge("extract", "analyze")
graph.add_edge("analyze", END)
graph.set_entry_point("extract")
resume_screener_workflow = graph.compile()

def resume_screener_agent(payload: Dict) -> Dict:
    resume_file = payload.get("resume_file")
    if not resume_file:
        return {"error": "Missing resume_file"}

    initial_state = {"resume_bytes": resume_file.read()}
    try:
        result = resume_screener_workflow.invoke(initial_state)
        if result.get("error"):
            return {"error": result["error"]}
        return {
            "metrics": result.get("metrics", []),
            "valuation": result.get("valuation", "")
        }
    except Exception as e:
        return {"error": str(e)}
