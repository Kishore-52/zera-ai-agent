import time
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, MaintenanceRequest

class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Maintenance Intake Agent", 1)

    def execute(self, request: dict, **kwargs) -> tuple[MaintenanceRequest, AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        # In full mode, this would use Gemini to structure unstructured text.
        # Here we just map it.
        req = MaintenanceRequest(
            machine=request.get("machine", "Unknown"),
            component=request.get("component", "Unknown"),
            maintenance_task=request.get("maintenance_task", "Unknown"),
            worker_name=request.get("worker_name", "Unknown"),
            worker_role=request.get("worker_role", "Unknown")
        )

        out_summary = f"Validated task: {req.maintenance_task} on {req.machine}"
        if self.is_local:
            out_summary += " (Local deterministic mode)"

        trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary=f"Raw input: {request.get('maintenance_task', '')[:20]}...",
            output_summary=out_summary,
            tools_used=["Pydantic Validation"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        return req, trace
