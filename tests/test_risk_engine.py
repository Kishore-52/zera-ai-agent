import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.schemas import SensorReading, SensorTimeSeries, Verdict, CheckStatus
from zera.tools.risk_engine import evaluate_safety_checks, determine_verdict
from zera.tools.pressure_analysis import detect_pressure_rebound

def test_hydraulic_pressure_42_returns_red():
    sr = SensorReading(
        electrical_voltage=0,
        hydraulic_pressure=42,
        pneumatic_pressure=0,
        ram_position="Lowered",
        mechanical_block_installed=False,
        breaker_lock_verified=True,
        hydraulic_isolation_valve_verified=True,
        try_start_completed=True,
        movement_detected=False,
        supervisor_approval=False
    )
    ts = SensorTimeSeries(hydraulic_pressure_series=[42])
    checks = evaluate_safety_checks(sr, ts)
    verdict = determine_verdict(checks, "PASS", False)
    assert verdict == Verdict.RED

def test_raised_ram_no_block_returns_red():
    sr = SensorReading(
        electrical_voltage=0,
        hydraulic_pressure=0,
        pneumatic_pressure=0,
        ram_position="Raised",
        mechanical_block_installed=False,
        breaker_lock_verified=True,
        hydraulic_isolation_valve_verified=True,
        try_start_completed=True,
        movement_detected=False,
        supervisor_approval=False
    )
    checks = evaluate_safety_checks(sr)
    verdict = determine_verdict(checks, "PASS", False)
    assert verdict == Verdict.RED

def test_missing_try_start_returns_amber_or_red():
    sr = SensorReading(
        electrical_voltage=0,
        hydraulic_pressure=0,
        pneumatic_pressure=0,
        ram_position="Lowered",
        mechanical_block_installed=False,
        breaker_lock_verified=True,
        hydraulic_isolation_valve_verified=True,
        try_start_completed=False,
        movement_detected=False,
        supervisor_approval=False
    )
    checks = evaluate_safety_checks(sr)
    verdict = determine_verdict(checks, "PASS", False)
    assert verdict in [Verdict.AMBER, Verdict.RED]

def test_corrected_scenario_returns_green():
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
    checks = evaluate_safety_checks(sr)
    verdict = determine_verdict(checks, "PASS", False)
    assert verdict == Verdict.GREEN

def test_pressure_rebound_detected():
    series = [42, 28, 15, 7, 3, 5, 8]
    assert detect_pressure_rebound(series) == True

def test_safe_decay_not_rebound():
    series = [42, 31, 20, 11, 5, 1.8, 0.8, 0.5]
    assert detect_pressure_rebound(series) == False

def test_invalid_sensor_values():
    with pytest.raises(ValueError):
        sr = SensorReading(
            electrical_voltage=-5, # Invalid
            hydraulic_pressure=0,
            pneumatic_pressure=0,
            ram_position="Raised",
            mechanical_block_installed=True,
            breaker_lock_verified=True,
            hydraulic_isolation_valve_verified=True,
            try_start_completed=True,
            movement_detected=False,
            supervisor_approval=False
        )
        
    with pytest.raises(ValueError):
        sr = SensorReading(
            electrical_voltage=0,
            hydraulic_pressure=0,
            pneumatic_pressure=0,
            ram_position="Sideways", # Invalid
            mechanical_block_installed=True,
            breaker_lock_verified=True,
            hydraulic_isolation_valve_verified=True,
            try_start_completed=True,
            movement_detected=False,
            supervisor_approval=False
        )
