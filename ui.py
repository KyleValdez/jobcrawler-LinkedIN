import json
import os
import gradio as gr
import threading
from flask import Flask, jsonify
from flask_cors import CORS

# FLASK -- API
flask_app = Flask(__name__)
CORS(flask_app)

def load_job_data(filename="linkedin_job_titles.json"):
    """
    Reads and returns a list of {url, title} dicts from JSON.
    Returns [] if file missing or malformed.
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []

@flask_app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Returns the full list of job entries as JSON."""
    return jsonify(load_job_data())

# Gradio UI
def display_job_cards():
    jobs = load_job_data()
    if not jobs:
        return "<p>No jobs found. Run the scraper first to generate linkedin_job_titles.json.</p>"

    html = f"<h2 style='margin-bottom:20px;'>Total Jobs Found: {len(jobs)}</h2>"
    for job in jobs:
        title = job.get("title", "No Title")
        url   = job.get("url", "#")
        html += f"""
        <div style="
            border:1px solid #ccc;
            border-radius:10px;
            padding:15px;
            margin:10px;
            box-shadow:0 2px 5px rgba(0,0,0,0.1);
        ">
            <h3 style="margin:0 0 5px;">{title}</h3>
            <a href="{url}" target="_blank">{url}</a>
        </div>
        """
    return html

# Run API and UI
def run_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Start Flask in a background thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Launch Gradio
    gr.Interface(
        fn=display_job_cards,
        inputs=[],
        outputs=gr.HTML(),
        title="LinkedIn Job Cards",
        description="Displays job titles and links scraped from LinkedIn."
    ).launch(server_port=7860)
