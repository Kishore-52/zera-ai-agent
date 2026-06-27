import time
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, SensorReading, SensorTimeSeries, SafetyCheck
from zera.tools.risk_engine import evaluate_safety_checks
from zera.tools.pressure_analysis import detect_pressure_rebound

class ResidualEnergyAgent(BaseAgent):
    def __init__(self):
        super().__init__("Residual Energy Analyst Agent", 4)

    def execute(self, sensor_data: SensorReading, time_series: SensorTimeSeries, **kwargs) -> tuple[dict, AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        # 1. Deterministic safety checks
        checks = evaluate_safety_checks(sensor_data, time_series)
        
        # 2. Time-series pressure rebound detection
        rebound_detected = False
        if time_series and time_series.hydraulic_pressure_series:
            rebound_detected = detect_pressure_rebound(time_series.hydraulic_pressure_series)
            
        results = {
            "checks": checks,
            "rebound_detected": rebound_detected
        }

        out_summary = f"Evaluated {len(checks)} checks. Rebound detected: {rebound_detected}"
        if self.is_local:
            out_summary += " (Local deterministic calculation)"

        trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary="Sensor data and time series",
            output_summary=out_summary,
            tools_used=["Deterministic Risk Engine", "Pressure Rebound Detection"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        return results, trace
