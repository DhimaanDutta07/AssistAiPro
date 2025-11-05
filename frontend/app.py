from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder=".")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/email-drafter")
def email_drafter():
    return send_from_directory(app.static_folder, "email-drafter.html")

@app.route("/leave-processor")
def leave_processor():
    return send_from_directory(app.static_folder, "leave-processor.html")

@app.route("/meeting-scheduler")
def meeting_scheduler():
    return send_from_directory(app.static_folder, "meeting-scheduler.html")

@app.route("/performance-analyzer")
def performance_analyzer():
    return send_from_directory(app.static_folder, "performance-analyzer.html")

@app.route("/policy-chatbot")
def policy_chatbot():
    return send_from_directory(app.static_folder, "policy-chatbot.html")

@app.route("/resume-screener")
def resume_screener():
    return send_from_directory(app.static_folder, "resume-screener.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
