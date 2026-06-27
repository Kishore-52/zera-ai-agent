import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Path setups
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)

from zera.schemas import SensorReading, SensorTimeSeries, MaintenanceRequest
from zera.workflows.safety_workflow import SafetyWorkflow
from zera.ui.energy_graph import generate_energy_map
from zera.memory.qdrant_store import QdrantStore
from zera.services.report_generator import save_report, generate_markdown_report

# Setup page config
st.set_page_config(
    page_title="ZERA AI | Zero-Energy Release Assurance Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Scenarios
@st.cache_data
def load_scenarios():
    path = os.path.join(sys_path, 'zera', 'data', 'demo_scenarios.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

scenarios = load_scenarios()

# Sidebar
with st.sidebar:
    st.title("ZERA AI")
    st.markdown("*Zero-Energy Release Assurance Agent*")
    
    st.divider()
    
    # Status Indicators
    st.subheader("System Status")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        st.success("Google ADK / Gemini: Active")
        mode = "Full Google ADK agent mode"
    else:
        st.warning("Google ADK / Gemini: Local Fallback")
        mode = "Local deterministic demonstration mode — Gemini reasoning unavailable"
        
    store = QdrantStore()
    q_info = store.get_info()
    st.info(f"Qdrant: {q_info['mode']} ({q_info['count']} records)")
    
    if os.environ.get("LYZR_API_KEY"):
        st.success("Lyzr Supervisor: Active")
    else:
        st.info("Lyzr Supervisor: optional integration not configured.")
        
    st.divider()
    st.write(f"**Mode:** {mode}")
    if "assessment_id" in st.session_state:
        st.write(f"**Current ID:** {st.session_state.assessment_id}")
        
    st.divider()
    st.caption("Mock manufacturer-approved limits for prototype simulation only. These are not universal industrial safety limits.")

# Main Application
st.title("ZERA AI Dashboard")
st.markdown("Agentic verification for hazardous-energy isolation")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "New Safety Assessment",
    "Energy Hazard Graph",
    "Agent Execution Trace",
    "Safety Memory",
    "Permit Report",
    "Architecture"
])

# State initialization
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {}
if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Maintenance Request")
        machine = st.text_input("Machine", value="Hydraulic Press HP-01")
        component = st.text_input("Component", value="Press Cylinder")
        task = st.text_input("Maintenance Task", value="Replace hydraulic cylinder seal")
        worker_name = st.text_input("Worker Name", value="John Doe")
        worker_role = st.text_input("Worker Role", value="Maintenance Technician")
        
        st.divider()
        scenario_keys = list(scenarios.keys())
        scenario_names = [scenarios[k]["name"] for k in scenario_keys]
        scenario_options = ["Custom Sensor Inputs"] + scenario_names
        
        selected_scenario_name = st.selectbox("Scenario Selector", scenario_options)
        
    with col2:
        st.subheader("Sensor Simulator")
        
        # Load from scenario if not custom
        current_data = {}
        if selected_scenario_name != "Custom Sensor Inputs":
            idx = scenario_names.index(selected_scenario_name)
            current_data = scenarios[scenario_keys[idx]]
        else:
            current_data = st.session_state.sensor_data
            
        def safe_get(key, default):
            return current_data.get(key, default)
            
        c1, c2 = st.columns(2)
        with c1:
            elec_v = st.number_input("Electrical Voltage (V)", value=float(safe_get("electrical_voltage", 0)))
            hyd_p = st.number_input("Hydraulic Pressure (bar)", value=float(safe_get("hydraulic_pressure", 42)))
            pneu_p = st.number_input("Pneumatic Pressure (bar)", value=float(safe_get("pneumatic_pressure", 0)))
            ram_pos = st.selectbox("Ram Position", ["Raised", "Lowered", "Unknown"], index=["Raised", "Lowered", "Unknown"].index(safe_get("ram_position", "Raised")))
            
        with c2:
            mech_block = st.checkbox("Mechanical Safety Block Installed", value=bool(safe_get("mechanical_block_installed", False)))
            breaker_lock = st.checkbox("Breaker Lock Verified", value=bool(safe_get("breaker_lock_verified", True)))
            hyd_valve = st.checkbox("Hydraulic Isolation Valve Verified", value=bool(safe_get("hydraulic_isolation_valve_verified", True)))
            try_start = st.checkbox("Try-Start Completed", value=bool(safe_get("try_start_completed", False)))
            movement = st.checkbox("Movement Detected", value=bool(safe_get("movement_detected", False)))
            sup_app = st.checkbox("Supervisor Approval", value=bool(safe_get("supervisor_approval", False)))
            
        hyd_series_str = st.text_input("Hydraulic Pressure Time Series (comma separated)", 
                                       value=",".join(map(str, safe_get("hydraulic_pressure_series", [hyd_p, hyd_p, hyd_p]))))
                                       
    st.divider()
    b1, b2, b3, b4 = st.columns(4)
    
    with b1:
        if st.button("Run Agentic Safety Assessment", type="primary"):
            req_dict = {
                "machine": machine,
                "component": component,
                "maintenance_task": task,
                "worker_name": worker_name,
                "worker_role": worker_role
            }
            sensor_obj = SensorReading(
                electrical_voltage=elec_v,
                hydraulic_pressure=hyd_p,
                pneumatic_pressure=pneu_p,
                ram_position=ram_pos,
                mechanical_block_installed=mech_block,
                breaker_lock_verified=breaker_lock,
                hydraulic_isolation_valve_verified=hyd_valve,
                try_start_completed=try_start,
                movement_detected=movement,
                supervisor_approval=sup_app
            )
            series = [float(x.strip()) for x in hyd_series_str.split(",") if x.strip()]
            ts_obj = SensorTimeSeries(hydraulic_pressure_series=series)
            
            with st.spinner("Agents are analyzing the safety context..."):
                wf = SafetyWorkflow()
                report = wf.run(req_dict, sensor_obj, ts_obj)
                
                st.session_state.workflow_result = report
                st.session_state.sensor_obj = sensor_obj
                st.session_state.assessment_id = report.assessment_id
                
            res = report.assessment_result
            if res.verdict.value == "RED":
                st.error("RED — MAINTENANCE BLOCKED")
            elif res.verdict.value == "AMBER":
                st.warning("AMBER — MISSING EVIDENCE OR SENSOR ISSUES")
            else:
                st.success("GREEN — READY FOR AUTHORIZED HUMAN REVIEW")
                if not sup_app:
                    st.info("Supervisor authorization pending.")
                    
    with b2:
        if st.button("Apply Recommended Corrective Actions"):
            st.session_state.sensor_data = {
                "electrical_voltage": 0,
                "hydraulic_pressure": 0.5,
                "pneumatic_pressure": 0,
                "ram_position": "Raised",
                "mechanical_block_installed": True,
                "breaker_lock_verified": True,
                "hydraulic_isolation_valve_verified": True,
                "try_start_completed": True,
                "movement_detected": False,
                "supervisor_approval": False,
                "hydraulic_pressure_series": [42, 31, 20, 11, 5, 1.8, 0.8, 0.5]
            }
            st.rerun()

    with b3:
        if st.button("Reset Demo"):
            st.session_state.sensor_data = {}
            st.session_state.workflow_result = None
            st.rerun()
            
    with b4:
        if st.session_state.workflow_result:
            if st.button("Generate Permit Report"):
                save_report(st.session_state.workflow_result, 'json')
                save_report(st.session_state.workflow_result, 'md')
                st.success("Reports generated and saved to storage/audit/")


with tab2:
    st.subheader("Energy Hazard Graph")
    if "sensor_obj" in st.session_state:
        dot = generate_energy_map("Current", st.session_state.sensor_obj)
        st.graphviz_chart(dot)
    else:
        st.info("Run an assessment to generate the energy graph.")

with tab3:
    st.subheader("Agent Execution Trace")
    if st.session_state.workflow_result:
        trace_data = []
        for t in st.session_state.workflow_result.agent_trace:
            trace_data.append({
                "Order": t.order,
                "Agent": t.agent,
                "Status": t.status.value,
                "Duration (s)": round(t.duration, 3),
                "Input Summary": t.input_summary,
                "Output Summary": t.output_summary,
                "Tools": ", ".join(t.tools_used)
            })
        st.dataframe(pd.DataFrame(trace_data), use_container_width=True)
    else:
        st.info("Run an assessment to view the agent trace.")

with tab4:
    st.subheader("Safety Memory")
    st.write(f"**Connection:** {q_info['mode']}")
    st.write(f"**Collection:** {q_info['collection']}")
    st.write(f"**Total Indexed Records:** {q_info['count']}")
    
    if st.session_state.workflow_result:
        st.write("### Retrieved Memories for Current Assessment")
        for m in st.session_state.workflow_result.near_miss_references:
            with st.expander(f"{m.title} (ID: {m.source_id}) - Score: {m.similarity_score:.4f}"):
                st.write(m.content)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Seed Safety Memory"):
            # Execute seed script
            import subprocess
            subprocess.run(["python", os.path.join(sys_path, "scripts", "seed_qdrant.py")])
            st.success("Seeding complete.")
            st.rerun()

with tab5:
    st.subheader("Permit Report")
    if st.session_state.workflow_result:
        report = st.session_state.workflow_result
        res = report.assessment_result
        
        if res.verdict.value == "RED":
            st.error(f"Verdict: {res.verdict.value}")
        elif res.verdict.value == "AMBER":
            st.warning(f"Verdict: {res.verdict.value}")
        else:
            st.success(f"Verdict: {res.verdict.value} (READY FOR AUTHORIZED HUMAN REVIEW)")
            
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Assessment ID:** {report.assessment_id}")
            st.write(f"**Timestamp:** {report.timestamp}")
            st.write(f"**Machine:** {report.machine}")
        with col2:
            st.write(f"**Worker:** {report.worker}")
            st.write(f"**Task:** {report.maintenance_task}")
            
        st.divider()
        st.markdown("### Blocking Hazards")
        for bh in res.blocking_hazards:
            st.markdown(f"- 🚫 {bh}")
            
        st.markdown("### Completed Controls")
        for cc in res.completed_controls:
            st.markdown(f"- ✅ {cc}")
            
        st.markdown("### Missing Evidence")
        for me in res.missing_evidence:
            st.markdown(f"- ⚠️ {me}")
            
        st.markdown("### Recommended Next Actions")
        for ra in res.recommended_actions:
            st.markdown(f"- 🔧 {ra}")
            
        st.markdown("### Safety Critic Result")
        st.info(f"{res.safety_critic_result.result}: {res.safety_critic_result.explanation}")
        
        st.caption(res.disclaimer)
        
        # Download buttons
        json_data = report.model_dump_json(indent=2)
        md_data = generate_markdown_report(report)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("Download JSON Report", data=json_data, file_name=f"{report.assessment_id}.json", mime="application/json")
        with c2:
            st.download_button("Download Markdown Report", data=md_data, file_name=f"{report.assessment_id}.md", mime="text/markdown")
            
    else:
        st.info("Run an assessment to generate a report.")

with tab6:
    st.subheader("ZERA AI Architecture")
    st.markdown("""
    ### Six-Agent Architecture
    1. **Maintenance Intake Agent**: Parses request and validates scope.
    2. **Safety Memory Agent**: Retrieves near-misses and LOTO procedures from Qdrant.
    3. **Isolation Planning Agent**: Generates task-specific isolation plan.
    4. **Residual Energy Analyst Agent**: Evaluates sensor readings deterministically.
    5. **Safety Critic Agent**: Independently reviews findings and flags missing evidence.
    6. **Permit Report Agent**: Generates the final verifiable report.
    
    ### Technologies
    - **Google ADK** for Agentic orchestration (Local Mode Fallback implemented)
    - **Gemini** for generative planning (Local Mode Fallback implemented)
    - **Qdrant** for Semantic Memory (Local & Cloud)
    - **Streamlit** for the UI
    - **Graphviz** for the Energy Hazard Graph
    - **Pydantic** for typed data validation
    
    *Deterministic vs Generative:*
    Critical numeric limits and thresholds (e.g. Voltage <= 5V) are verified deterministically by Python to ensure absolute safety compliance, whereas text extraction and planning utilize generative capabilities.
    """)
