import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.schemas import SensorReading, SensorTimeSeries
from zera.workflows.safety_workflow import SafetyWorkflow
from zera.services.report_generator import save_report

def export_report():
    print("Exporting sample report...")
    
    # Safe scenario
    sr = SensorReading(
        electrical_voltage=0,
        hydraulic_pressure=0.5,
        pneumatic_pressure=0,
        ram_position="Raised",
        mechanical_block_installed=True,
        breaker_lock_verified=True,
        hydraulic_isolation_valve_verified=True,
        try_start_completed=True,
        movement_detected=False,
        supervisor_approval=False
    )
    ts = SensorTimeSeries(hydraulic_pressure_series=[42, 31, 20, 11, 5, 1.8, 0.8, 0.5])
    
    req = {
        "machine": "HP-01",
        "component": "Press Cylinder",
        "maintenance_task": "Replace seal",
        "worker_name": "Test Worker",
        "worker_role": "Technician"
    }
    
    wf = SafetyWorkflow()
    report = wf.run(req, sr, ts)
    
    json_path = save_report(report, 'json')
    md_path = save_report(report, 'md')
    
    print(f"Exported JSON: {json_path}")
    print(f"Exported Markdown: {md_path}")

if __name__ == "__main__":
    export_report()
