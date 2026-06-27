import time
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, IsolationStep, EnergyType

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__("Isolation Planning Agent", 3)

    def execute(self, request, memories, **kwargs) -> tuple[list[IsolationStep], AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        # Deterministic generation for prototype. In full mode, uses Gemini + memories.
        plan = [
            IsolationStep(
                step_number=1,
                hazard="Electrical Power",
                energy_type=EnergyType.ELECTRICAL,
                isolation_point="Main Breaker",
                required_action="Turn off and lock out main breaker.",
                required_evidence="Breaker Lock Verified",
                verification_method="Visual",
                source_document="LOTO-HP-01"
            ),
            IsolationStep(
                step_number=2,
                hazard="Hydraulic Pressure",
                energy_type=EnergyType.HYDRAULIC,
                isolation_point="Main Hydraulic Valve",
                required_action="Close and lock hydraulic isolation valve. Relieve pressure.",
                required_evidence="Hydraulic Valve Verified",
                verification_method="Visual & Sensor",
                source_document="LOTO-HP-01"
            ),
            IsolationStep(
                step_number=3,
                hazard="Gravitational Energy",
                energy_type=EnergyType.GRAVITATIONAL,
                isolation_point="Raised Ram",
                required_action="Install mechanical safety block.",
                required_evidence="Mechanical Block Installed",
                verification_method="Visual & Sensor",
                source_document="HM-2025-08"
            ),
            IsolationStep(
                step_number=4,
                hazard="Mechanical Energy",
                energy_type=EnergyType.MECHANICAL,
                isolation_point="Machine Controls",
                required_action="Attempt to start the machine to verify isolation.",
                required_evidence="Try-Start Completed, No Movement",
                verification_method="Functional",
                source_document="HM-2025-10"
            )
        ]

        out_summary = f"Generated {len(plan)} isolation steps."
        if self.is_local:
            out_summary += " (Local deterministic plan)"

        trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary="Task details and retrieved memories",
            output_summary=out_summary,
            tools_used=["Procedure Generator"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        return plan, trace
