import time
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, CriticResult, CheckStatus

class SafetyCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("Safety Critic Agent", 5)

    def execute(self, plan: list, energy_results: dict, **kwargs) -> tuple[CriticResult, AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        checks = energy_results.get("checks", [])
        
        # Critic Logic
        missing = [c for c in checks if c.status == CheckStatus.MISSING]
        failed = [c for c in checks if c.status == CheckStatus.FAIL]
        
        if failed:
            result = "FAIL"
            explanation = "Critical safety checks failed. Residual hazardous energy detected."
        elif missing:
            result = "NEEDS_EVIDENCE"
            explanation = "Required verification evidence is missing (e.g., Locks, Valves, Try-Start)."
        else:
            result = "PASS"
            explanation = "All required evidence is present and sensors are within safe limits."

        critic_res = CriticResult(result=result, explanation=explanation)

        out_summary = f"Critic result: {result}"
        if self.is_local:
            out_summary += " (Local deterministic logic)"

        trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary="Isolation plan and energy analysis results",
            output_summary=out_summary,
            tools_used=["Independent Verification Engine"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        return critic_res, trace
