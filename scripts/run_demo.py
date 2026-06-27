import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.schemas import SensorReading, SensorTimeSeries
from zera.workflows.safety_workflow import SafetyWorkflow

def run_demo():
    print("Running Demo Scenarios")
    print("======================")
    
    path = os.path.join(os.path.dirname(__file__), '..', 'zera', 'data', 'demo_scenarios.json')
    with open(path, 'r') as f:
        scenarios = json.load(f)
        
    req = {
        "machine": "HP-01",
        "component": "Press Cylinder",
        "maintenance_task": "Replace seal",
        "worker_name": "Test Worker",
        "worker_role": "Technician"
    }
    
    wf = SafetyWorkflow()
    
    for key, data in scenarios.items():
        print(f"\nEvaluating: {data['name']}")
        sr = SensorReading(**data)
        ts = SensorTimeSeries(hydraulic_pressure_series=data.get("hydraulic_pressure_series", []))
        report = wf.run(req, sr, ts)
        print(f"Verdict: {report.assessment_result.verdict.value}")

if __name__ == "__main__":
    run_demo()
