import json
import os
from zera.schemas import PermitReport

def save_report(report: PermitReport, file_format: str = 'json') -> str:
    storage_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'audit')
    os.makedirs(storage_dir, exist_ok=True)
    
    file_path = os.path.join(storage_dir, f"{report.assessment_id}.{file_format}")
    
    if file_format == 'json':
        with open(file_path, 'w') as f:
            f.write(report.model_dump_json(indent=2))
    elif file_format == 'md':
        with open(file_path, 'w') as f:
            f.write(generate_markdown_report(report))
            
    return file_path

def generate_markdown_report(report: PermitReport) -> str:
    md = f"# ZERA AI Permit Readiness Report\n\n"
    md += f"**Assessment ID**: {report.assessment_id}\n"
    md += f"**Timestamp**: {report.timestamp}\n"
    md += f"**Machine**: {report.machine}\n"
    md += f"**Worker**: {report.worker}\n"
    md += f"**Task**: {report.maintenance_task}\n\n"
    
    res = report.assessment_result
    md += f"## Verdict: {res.verdict.value}\n\n"
    
    md += f"### Human Approval Status\n{res.human_approval_status}\n\n"
    
    if res.blocking_hazards:
        md += "### Blocking Hazards\n"
        for bh in res.blocking_hazards:
            md += f"- {bh}\n"
        md += "\n"
        
    md += "### Completed Controls\n"
    for cc in res.completed_controls:
        md += f"- {cc}\n"
    md += "\n"
    
    if res.missing_evidence:
        md += "### Missing Evidence\n"
        for me in res.missing_evidence:
            md += f"- {me}\n"
        md += "\n"
        
    if res.recommended_actions:
        md += "### Recommended Next Actions\n"
        for ra in res.recommended_actions:
            md += f"- {ra}\n"
        md += "\n"
        
    md += "### Safety Critic Result\n"
    md += f"**Result**: {res.safety_critic_result.result}\n"
    md += f"**Explanation**: {res.safety_critic_result.explanation}\n\n"
    
    md += f"## Disclaimer\n*{res.disclaimer}*\n"
    
    return md
