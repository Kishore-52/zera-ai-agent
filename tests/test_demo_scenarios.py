import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.schemas import SensorReading, SensorTimeSeries, Verdict
from zera.workflows.safety_workflow import SafetyWorkflow

@pytest.fixture
def scenarios():
    path = os.path.join(os.path.dirname(__file__), '..', 'zera', 'data', 'demo_scenarios.json')
    with open(path, 'r') as f:
        return json.load(f)

def test_unsafe_scenario_returns_red(scenarios):
    data = scenarios["scenario_1"]
    sr = SensorReading(**data)
    ts = SensorTimeSeries(hydraulic_pressure_series=data.get("hydraulic_pressure_series", []))
    wf = SafetyWorkflow()
    req = {"machine": "HP-01", "component": "C", "maintenance_task": "T", "worker_name": "W", "worker_role": "R"}
    report = wf.run(req, sr, ts)
    assert report.assessment_result.verdict == Verdict.RED

def test_corrected_scenario_returns_green(scenarios):
    data = scenarios["scenario_2"]
    sr = SensorReading(**data)
    ts = SensorTimeSeries(hydraulic_pressure_series=data.get("hydraulic_pressure_series", []))
    wf = SafetyWorkflow()
    req = {"machine": "HP-01", "component": "C", "maintenance_task": "T", "worker_name": "W", "worker_role": "R"}
    report = wf.run(req, sr, ts)
    assert report.assessment_result.verdict == Verdict.GREEN

def test_rebound_scenario_returns_red(scenarios):
    data = scenarios["scenario_3"]
    sr = SensorReading(**data)
    ts = SensorTimeSeries(hydraulic_pressure_series=data.get("hydraulic_pressure_series", []))
    wf = SafetyWorkflow()
    req = {"machine": "HP-01", "component": "C", "maintenance_task": "T", "worker_name": "W", "worker_role": "R"}
    report = wf.run(req, sr, ts)
    assert report.assessment_result.verdict == Verdict.RED
