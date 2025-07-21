import json
import gradio as gr
import threading
from flask import Flask, jsonify
from flask_cors import CORS

# Flask setup
flask_app = Flask(__name__)
CORS(flask_app)

def load_job_data():
    """Helper function to load job data"""
    try:
        with open("linkedin_jobs.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except:
        return {"job_links": []}

@flask_app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """API endpoint to get all job links"""
    try:
        data = load_job_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Failed to read job data'}), 500

@flask_app.route('/api/jobs/count', methods=['GET'])
def get_job_count():
    """API endpoint to get job count"""
    try:
        data = load_job_data()
        return jsonify({
            'total_jobs': len(data.get('job_links', [])),
            'newly_added': len(data.get('newly_added', []))
        })
    except Exception as e:
        return jsonify({'error': 'Failed to read job data'}), 500


def display_job_cards():
    try:
        with open("linkedin_jobs.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            job_links = data.get("job_links", [])
    except:
        job_links = []

    if not job_links:
        return "<p>No jobs found. Try clicking 'Refresh Job Links'.</p>"

    # Add job count here
    header = f"<h2 style='margin-bottom:20px;'>Total Jobs Found: {len(job_links)}</h2>"

    cards = ""
    for url in job_links:
        job_title = url.split("/")[-2].replace("-", " ").title()
        cards += f"""
        <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
            <h3>{job_title}</h3>
            <a href="{url}" target="_blank">{url}</a>
        </div>
        """

    return header + cards

def run_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()


gr.Interface(
    fn=display_job_cards,
    inputs=[],
    outputs=gr.HTML(),
    title="LinkedIn Job Cards",
    description="Displays job links scraped from LinkedIn in card format."
).launch(server_port=7860)