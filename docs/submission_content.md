# Project Title
ZERA AI

# Tagline
Because switching off is not the same as proving zero energy.

# Description (150 words)
ZERA AI (Zero-Energy Release Assurance) is a multi-agent decision-support platform designed to protect industrial workers from hazardous residual energy. While traditional Lockout/Tagout (LOTO) relies heavily on manual compliance and static checklists, ZERA AI dynamically analyzes real-time sensor readings and retrieves historical near-misses to verify that a machine is truly at zero energy. 

Using Google ADK and Gemini, ZERA deploys a six-agent architecture that parses maintenance tasks, fetches procedures from Qdrant vector memory, generates an isolation plan, deterministically evaluates safety thresholds, independently criticizes the findings, and compiles an auditable Permit Report. ZERA ensures that fatal omissions—like unblocked gravitational loads or pressure rebounds—are flagged before maintenance begins. ZERA does not autonomously authorize work; rather, it provides an airtight readiness report for authorized human review.

# Problem Statement
Industrial machines retain hazardous stored energy even when disconnected from power. Relying on paper LOTO checklists often fails to account for dynamic risks like pressure rebound or human error, leading to preventable injuries.

# Existing Solution
Current solutions are static, non-intelligent digital forms that lack context-awareness and do not logically cross-verify sensor data against safety requirements or historical incidents.

# Proposed Solution
An agentic safety layer that synthesizes maintenance context, historical near-misses, and live sensor readings to rigorously verify isolation before human approval.

# Innovation and X-factors
- **Agentic Segregation of Duties**: Separate agents for Planning and Criticizing ensure robust self-correction.
- **Deterministic + Generative Hybrid**: Generative AI plans and retrieves, while critical safety limits (e.g. Voltage <= 5V) are enforced purely via deterministic Python rules.
- **Semantic Safety Memory**: Contextualizes current tasks with past incidents using Qdrant.

# Agent Architecture
Six distinct agents orchestrate the workflow: Intake, Memory, Planning, Residual Energy Analyst, Safety Critic, and Permit Report.

# Technology Stack
- Google ADK / Gemini
- Qdrant
- Streamlit
- Pydantic
- Graphviz
- Python

# GitHub Repository Description
Multi-agent industrial safety assurance platform built with Google ADK, Gemini and Qdrant to detect residual hazardous energy before machine maintenance.

# Prototype Video Description
A three-minute demonstration of ZERA AI blocking unsafe maintenance, retrieving a near-miss incident from Qdrant, executing a six-agent review trace, and successfully generating a human-review permit report.

# Hashtags
#GoogleADK #AgenticAI #IndustrialSafety #Gemini #Hackathon
