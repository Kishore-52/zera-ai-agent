from zera.agents.intake_agent import IntakeAgent
from zera.agents.memory_agent import MemoryAgent
from zera.agents.planning_agent import PlanningAgent
from zera.agents.residual_energy_agent import ResidualEnergyAgent
from zera.agents.safety_critic_agent import SafetyCriticAgent
from zera.agents.permit_report_agent import PermitReportAgent
from zera.schemas import SensorReading, SensorTimeSeries

class SafetyWorkflow:
    def __init__(self):
        self.intake = IntakeAgent()
        self.memory = MemoryAgent()
        self.planner = PlanningAgent()
        self.analyst = ResidualEnergyAgent()
        self.critic = SafetyCriticAgent()
        self.reporter = PermitReportAgent()
        
    def run(self, request_dict: dict, sensor_data: SensorReading, time_series: SensorTimeSeries):
        traces = []
        
        # 1. Intake
        req, t1 = self.intake.execute(request_dict)
        traces.append(t1)
        
        # 2. Memory
        memories, t2 = self.memory.execute(req)
        traces.append(t2)
        
        # 3. Planning
        plan, t3 = self.planner.execute(req, memories)
        traces.append(t3)
        
        # 4. Analyst
        results, t4 = self.analyst.execute(sensor_data, time_series)
        traces.append(t4)
        
        # 5. Critic
        critic_res, t5 = self.critic.execute(plan, results)
        traces.append(t5)
        
        # 6. Reporter
        report, _ = self.reporter.execute(req, memories, plan, results, critic_res, traces)
        # Note: the reporter appends its own trace to the list
        
        return report
