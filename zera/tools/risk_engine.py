from zera.schemas import SensorReading, SensorTimeSeries, SafetyCheck, CheckStatus, Severity, Verdict
import json
import os

def load_thresholds():
    # Fallback thresholds
    default = {
        "electrical_voltage_safe_threshold": 5,
        "hydraulic_pressure_safe_threshold": 1,
        "pneumatic_pressure_safe_threshold": 1
    }
    
    # Try to load from machine_profile.json
    profile_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'machine_profile.json')
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
                return data.get("mock_safety_thresholds", default)
        except Exception:
            return default
    return default

def evaluate_safety_checks(sensor_data: SensorReading, time_series: SensorTimeSeries = None):
    thresholds = load_thresholds()
    checks = []
    
    # 1. Electrical voltage
    v_thresh = thresholds.get("electrical_voltage_safe_threshold", 5)
    if sensor_data.electrical_voltage <= v_thresh:
        checks.append(SafetyCheck(
            check_name="Electrical Voltage Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence=f"{sensor_data.electrical_voltage} V",
            expected_condition=f"<= {v_thresh} V",
            explanation="Voltage is within safe limits.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Electrical Voltage Verification",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            observed_evidence=f"{sensor_data.electrical_voltage} V",
            expected_condition=f"<= {v_thresh} V",
            explanation="Dangerous electrical voltage detected.",
            required_action="Follow approved electrical isolation procedure."
        ))

    # 2. Hydraulic pressure
    h_thresh = thresholds.get("hydraulic_pressure_safe_threshold", 1)
    if sensor_data.hydraulic_pressure <= h_thresh:
        checks.append(SafetyCheck(
            check_name="Hydraulic Pressure Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence=f"{sensor_data.hydraulic_pressure} bar",
            expected_condition=f"<= {h_thresh} bar",
            explanation="Hydraulic pressure is within safe limits.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Hydraulic Pressure Verification",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            observed_evidence=f"{sensor_data.hydraulic_pressure} bar",
            expected_condition=f"<= {h_thresh} bar",
            explanation="Hazardous hydraulic pressure remains.",
            required_action="Follow the approved hydraulic pressure-release procedure."
        ))

    # 3. Pneumatic pressure
    p_thresh = thresholds.get("pneumatic_pressure_safe_threshold", 1)
    if sensor_data.pneumatic_pressure <= p_thresh:
        checks.append(SafetyCheck(
            check_name="Pneumatic Pressure Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence=f"{sensor_data.pneumatic_pressure} bar",
            expected_condition=f"<= {p_thresh} bar",
            explanation="Pneumatic pressure is within safe limits.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Pneumatic Pressure Verification",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            observed_evidence=f"{sensor_data.pneumatic_pressure} bar",
            expected_condition=f"<= {p_thresh} bar",
            explanation="Hazardous pneumatic pressure remains.",
            required_action="Follow the approved pneumatic isolation procedure."
        ))

    # 4. Ram position and mechanical block
    if sensor_data.ram_position.lower() == "raised":
        if sensor_data.mechanical_block_installed:
            checks.append(SafetyCheck(
                check_name="Mechanical Ram Safety Block",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                observed_evidence="Ram Raised, Block Installed",
                expected_condition="Block Installed if Ram Raised",
                explanation="Gravitational hazard is mechanically restrained.",
                required_action="None"
            ))
        else:
            checks.append(SafetyCheck(
                check_name="Mechanical Ram Safety Block",
                status=CheckStatus.FAIL,
                severity=Severity.CRITICAL,
                observed_evidence="Ram Raised, Block Missing",
                expected_condition="Block Installed if Ram Raised",
                explanation="Raised ram creates a gravitational hazard.",
                required_action="Install the rated mechanical ram safety block."
            ))

    # 5. Breaker lock verified
    if sensor_data.breaker_lock_verified:
        checks.append(SafetyCheck(
            check_name="Breaker Lock Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence="Lock Verified",
            expected_condition="Lock Verified",
            explanation="Main breaker is locked out.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Breaker Lock Verification",
            status=CheckStatus.MISSING,
            severity=Severity.HIGH,
            observed_evidence="Lock Missing/Unverified",
            expected_condition="Lock Verified",
            explanation="Physical lock on main breaker is required.",
            required_action="Verify physical lockout on main breaker."
        ))

    # 6. Hydraulic isolation valve verified
    if sensor_data.hydraulic_isolation_valve_verified:
        checks.append(SafetyCheck(
            check_name="Hydraulic Isolation Valve Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence="Valve Verified",
            expected_condition="Valve Verified",
            explanation="Hydraulic isolation valve is verified closed.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Hydraulic Isolation Valve Verification",
            status=CheckStatus.MISSING,
            severity=Severity.HIGH,
            observed_evidence="Valve Unverified",
            expected_condition="Valve Verified",
            explanation="Physical verification of closed hydraulic valve is required.",
            required_action="Verify hydraulic isolation valve is closed."
        ))

    # 7. Try-start completed
    if sensor_data.try_start_completed:
        checks.append(SafetyCheck(
            check_name="Try-Start Verification",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence="Try-Start Completed",
            expected_condition="Try-Start Completed",
            explanation="Try-start verification has been completed.",
            required_action="None"
        ))
    else:
        checks.append(SafetyCheck(
            check_name="Try-Start Verification",
            status=CheckStatus.MISSING,
            severity=Severity.HIGH,
            observed_evidence="Try-Start Incomplete",
            expected_condition="Try-Start Completed",
            explanation="Try-start verification is incomplete.",
            required_action="Complete the approved try-start verification."
        ))

    # 8. Movement during try-start
    if sensor_data.try_start_completed:
        if sensor_data.movement_detected:
            checks.append(SafetyCheck(
                check_name="Try-Start Movement Detection",
                status=CheckStatus.FAIL,
                severity=Severity.CRITICAL,
                observed_evidence="Movement Detected",
                expected_condition="No Movement",
                explanation="Machine moved during try-start. Energy is not isolated.",
                required_action="Abort maintenance. Re-evaluate energy isolation."
            ))
        else:
            checks.append(SafetyCheck(
                check_name="Try-Start Movement Detection",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                observed_evidence="No Movement",
                expected_condition="No Movement",
                explanation="No unexpected movement detected during try-start.",
                required_action="None"
            ))

    # 9. Supervisor approval (kept outside AI control, but we flag it)
    if not sensor_data.supervisor_approval:
        checks.append(SafetyCheck(
            check_name="Human Authorization",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            observed_evidence="Pending",
            expected_condition="Approved",
            explanation="Human authorization is pending.",
            required_action="Submit the evidence to an authorized supervisor."
        ))

    return checks

def determine_verdict(checks: list[SafetyCheck], critic_result: str = "PASS", rebound_detected: bool = False) -> Verdict:
    if rebound_detected:
        return Verdict.RED
        
    for check in checks:
        if check.status == CheckStatus.FAIL:
            return Verdict.RED
            
    if critic_result == "FAIL":
        return Verdict.RED
        
    for check in checks:
        if check.status == CheckStatus.MISSING:
            return Verdict.AMBER
            
    if critic_result == "NEEDS_EVIDENCE":
        return Verdict.AMBER
        
    return Verdict.GREEN
