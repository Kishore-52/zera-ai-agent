import os
import json
from flask import Flask, render_template, request, jsonify
from zera.schemas import SensorReading, SensorTimeSeries
from zera.workflows.safety_workflow import SafetyWorkflow
from zera.ui.energy_graph import generate_energy_map
from zera.memory.qdrant_store import QdrantStore
from zera.services.report_generator import save_report

app = Flask(__name__)

# Load Scenarios
def load_scenarios():
    path = os.path.join(os.path.dirname(__file__), 'zera', 'data', 'demo_scenarios.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

scenarios = load_scenarios()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    api_key = os.environ.get("GOOGLE_API_KEY")
    adk_status = "Full Google ADK Agent Mode" if api_key else "Local Fallback"
    
    store = QdrantStore()
    q_info = store.get_info()
    
    lyzr = "Active" if os.environ.get("LYZR_API_KEY") else "Not configured"
    
    return jsonify({
        "adk": adk_status,
        "qdrant": f"{q_info['mode']} ({q_info['count']} records)",
        "lyzr": lyzr
    })

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify(scenarios)

@app.route('/api/assess', methods=['POST'])
def assess():
    data = request.json
    
    req_dict = data.get('request', {})
    sensor_dict = data.get('sensors', {})
    
    sr = SensorReading(**sensor_dict)
    ts = SensorTimeSeries(hydraulic_pressure_series=sensor_dict.get('hydraulic_pressure_series', []))
    
    wf = SafetyWorkflow()
    report = wf.run(req_dict, sr, ts)
    
    # Save the reports
    save_report(report, 'json')
    save_report(report, 'md')
    
    global latest_assessment_id
    latest_assessment_id = report.assessment_id
    
    return jsonify({
        "report": report.model_dump(),
        "verdict": report.assessment_result.verdict.value,
        "disclaimer": report.assessment_result.disclaimer,
        "sensors": sr.model_dump()
    })

@app.route('/api/graphviz', methods=['POST'])
def graphviz():
    data = request.json
    sensor_dict = data.get('sensors', {})
    sr = SensorReading(**sensor_dict)
    
    dot = generate_energy_map("Current", sr)
    svg = dot.pipe(format='svg').decode('utf-8')
    return jsonify({"svg": svg})

@app.route('/api/seed', methods=['POST'])
def seed_memory():
    import subprocess
    sys_path = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["python", os.path.join(sys_path, "scripts", "seed_qdrant.py")])
    return jsonify({"status": "success"})

latest_assessment_id = None

@app.route('/api/download/<fmt>', methods=['GET'])
def download(fmt):
    global latest_assessment_id
    if not latest_assessment_id:
        return "No report generated yet", 404
    
    from flask import send_file
    storage_dir = os.path.join(os.path.dirname(__file__), 'storage', 'audit')
    file_path = os.path.join(storage_dir, f"{latest_assessment_id}.{fmt}")
    
    if not os.path.exists(file_path):
        return "File not found", 404
        
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
