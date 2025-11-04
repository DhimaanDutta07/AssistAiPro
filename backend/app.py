from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.email_drafter import auto_email_agent
from agents.meeting_scheduler import meeting_scheduler_agent
from agents.policy_chatbot import policy_chatbot_agent
from agents.resume_screener import resume_screener_agent
from agents.performance_analyzer import performance_analyzer_agent
from agents.leave_processor import leave_processor_agent

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/email-drafter', methods=['POST'])
def route_email_drafter():
    data = request.get_json(force=True)
    result = auto_email_agent(data)
    return jsonify(result), 200

@app.route('/meeting-scheduler', methods=['POST'])
def route_meeting_scheduler():
    data = request.get_json(force=True)
    result = meeting_scheduler_agent(data)
    return jsonify(result), 200

@app.route('/policy-chatbot', methods=['POST'])
def route_policy_chatbot():
    data = request.get_json(force=True)
    result = policy_chatbot_agent(data)
    return jsonify(result), 200

@app.route('/resume-screener', methods=['POST'])
def route_resume_screener():
    resume_file = request.files.get('resume_file')
    if not resume_file:
        return jsonify({"error": "Missing resume_file"}), 400
    result = resume_screener_agent({"resume_file": resume_file})
    return jsonify(result), 200

@app.route('/performance-analyzer', methods=['POST'])
def route_performance_analyzer():
    data = request.get_json(force=True)
    result = performance_analyzer_agent(data)
    return jsonify(result), 200

@app.route('/leave-processor', methods=['POST'])
def route_leave_processor():
    data = request.get_json(force=True)
    result = leave_processor_agent(data)
    return jsonify(result), 200
