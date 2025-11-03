from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agents.email_drafter import auto_email_agent
from agents.meeting_scheduler import meeting_scheduler_agent
from agents.policy_chatbot import policy_chatbot_agent
from agents.resume_screener import resume_screener_agent
from agents.performance_analyzer import performance_analyzer_agent
from agents.leave_processor import leave_processor_agent

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

@app.route('/email-drafter')
def email_drafter_page():
    return send_from_directory('../frontend', 'email-drafter.html')

@app.route('/meeting-scheduler')
def meeting_scheduler_page():
    return send_from_directory('../frontend', 'meeting-scheduler.html')

@app.route('/policy-chatbot')
def policy_chatbot_page():
    return send_from_directory('../frontend', 'policy-chatbot.html')

@app.route('/resume-screener')
def resume_screener_page():
    return send_from_directory('../frontend', 'resume-screener.html')

@app.route('/performance-analyzer')
def performance_analyzer_page():
    return send_from_directory('../frontend', 'performance-analyzer.html')

@app.route('/leave-processor')
def leave_processor_page():
    return send_from_directory('../frontend', 'leave-processor.html')

@app.route('/login')
def login_page():
    return send_from_directory('../frontend', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('../frontend', 'register.html')

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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return {"error": "Email and password are required"}, 400
    return {"message": "Implement Firebase registration here"}, 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return {"error": "Email and password are required"}, 400
    return {"message": "Implement Firebase login here"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
