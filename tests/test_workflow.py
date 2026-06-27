import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.workflows.safety_workflow import SafetyWorkflow
from zera.schemas import SensorReading, SensorTimeSeries, Verdict

def test_workflow_no_autonomous_approval():
    sr = SensorReading(
        electrical_voltage=0,
        hydraulic_pressure=0.5,
        pneumatic_pressure=0,
        ram_position="Lowered",
        mechanical_block_installed=False,
        breaker_lock_verified=True,
        hydraulic_isolation_valve_verified=True,
        try_start_completed=True,
        movement_detected=False,
        supervisor_approval=False
    )
    ts = SensorTimeSeries(hydraulic_pressure_series=[1.0, 0.5])
    
    req_dict = {
        "machine": "HP-01",
        "component": "Test",
        "maintenance_task": "Test Task",
        "worker_name": "Test",
        "worker_role": "Test"
    }
    
    wf = SafetyWorkflow()
    report = wf.run(req_dict, sr, ts)
    
    assert report.assessment_result.verdict == Verdict.GREEN
    assert report.assessment_result.human_approval_status == "Pending"
    assert "Mock manufacturer-approved limits for prototype simulation only" in report.assessment_result.disclaimer
    
    # Verify agent trace is in the report
    assert len(report.agent_trace) == 6
