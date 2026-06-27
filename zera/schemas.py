from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator

class Verdict(str, Enum):
    RED = "RED"
    AMBER = "AMBER"
    GREEN = "GREEN"

class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    MISSING = "MISSING"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class EnergyType(str, Enum):
    ELECTRICAL = "Electrical"
    HYDRAULIC = "Hydraulic"
    PNEUMATIC = "Pneumatic"
    GRAVITATIONAL = "Gravitational"
    MECHANICAL = "Mechanical"

class AgentExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

class MaintenanceRequest(BaseModel):
    machine: str = Field(..., min_length=1)
    component: str = Field(..., min_length=1)
    maintenance_task: str = Field(..., min_length=1)
    worker_name: str = Field(..., min_length=1)
    worker_role: str = Field(..., min_length=1)

class SensorReading(BaseModel):
    electrical_voltage: float
    hydraulic_pressure: float
    pneumatic_pressure: float
    ram_position: str
    mechanical_block_installed: bool
    breaker_lock_verified: bool
    hydraulic_isolation_valve_verified: bool
    try_start_completed: bool
    movement_detected: bool
    supervisor_approval: bool

    @validator("electrical_voltage", "hydraulic_pressure", "pneumatic_pressure")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v

    @validator("ram_position")
    def validate_ram_position(cls, v):
        if v.lower() not in ["raised", "lowered", "unknown"]:
            raise ValueError("Unknown ram state")
        return v

class SensorTimeSeries(BaseModel):
    hydraulic_pressure_series: List[float]

class EnergySource(BaseModel):
    id: str
    name: str
    type: EnergyType
    isolation_point: str

class IsolationStep(BaseModel):
    step_number: int
    hazard: str
    energy_type: EnergyType
    isolation_point: str
    required_action: str
    required_evidence: str
    verification_method: str
    source_document: str

class EvidenceItem(BaseModel):
    item_name: str
    is_present: bool

class RetrievedMemory(BaseModel):
    source_id: str
    title: str
    content: str
    similarity_score: float

class SafetyCheck(BaseModel):
    check_name: str
    status: CheckStatus
    severity: Severity
    observed_evidence: str
    expected_condition: str
    explanation: str
    required_action: str

class CriticResult(BaseModel):
    result: str # PASS, FAIL, NEEDS_EVIDENCE
    explanation: str

class AgentTrace(BaseModel):
    order: int
    agent: str
    status: AgentExecutionStatus
    input_summary: str
    output_summary: str
    tools_used: List[str]
    start_time: str
    completion_time: str
    duration: float
    error: Optional[str] = None

class AssessmentResult(BaseModel):
    verdict: Verdict
    blocking_hazards: List[str]
    completed_controls: List[str]
    missing_evidence: List[str]
    recommended_actions: List[str]
    safety_critic_result: CriticResult
    human_approval_status: str
    disclaimer: str

class PermitReport(BaseModel):
    assessment_id: str
    timestamp: str
    machine: str
    worker: str
    maintenance_task: str
    assessment_result: AssessmentResult
    near_miss_references: List[RetrievedMemory]
    agent_trace: List[AgentTrace]
