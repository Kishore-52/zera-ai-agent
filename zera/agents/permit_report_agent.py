import time
import uuid
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, AssessmentResult, PermitReport, CheckStatus
from zera.tools.risk_engine import determine_verdict

class PermitReportAgent(BaseAgent):
    def __init__(self):
        super().__init__("Permit Report Agent", 6)

    def execute(self, request, memories, plan, energy_results, critic_result, traces, **kwargs) -> tuple[PermitReport, AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        checks = energy_results.get("checks", [])
        rebound_detected = energy_results.get("rebound_detected", False)
        
        verdict = determine_verdict(checks, critic_result.result, rebound_detected)
        
        blocking = [c.explanation for c in checks if c.status == CheckStatus.FAIL]
        if rebound_detected:
            blocking.append("Pressure rebound detected after initial pressure decay. A leaking or incomplete isolation condition may exist.")
            
        completed = [c.check_name for c in checks if c.status == CheckStatus.PASS]
        missing = [c.check_name for c in checks if c.status == CheckStatus.MISSING]
        actions = [c.required_action for c in checks if c.status != CheckStatus.PASS]
        
        # De-duplicate actions
        actions = list(set(actions))
        
        assessment_res = AssessmentResult(
            verdict=verdict,
            blocking_hazards=blocking,
            completed_controls=completed,
            missing_evidence=missing,
            recommended_actions=actions,
            safety_critic_result=critic_result,
            human_approval_status="Pending",
            disclaimer="Mock manufacturer-approved limits for prototype simulation only. These are not universal industrial safety limits."
        )
        
        # Include this agent's trace as pending to self-register
        my_trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary="Workflow results",
            output_summary=f"Final Verdict: {verdict.value}",
            tools_used=["Report Generator"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        traces.append(my_trace)
        
        report = PermitReport(
            assessment_id=f"ZERA-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now().isoformat(),
            machine=request.machine,
            worker=request.worker_name,
            maintenance_task=request.maintenance_task,
            assessment_result=assessment_res,
            near_miss_references=memories,
            agent_trace=traces
        )

        return report, my_trace
