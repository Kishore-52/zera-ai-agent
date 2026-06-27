# ZERA AI Multi-Agent Workflow

This document explains the agent architecture of the ZERA AI platform.

The system utilizes six agents to perform a verifiable safety review:
1. **Maintenance Intake Agent**: Structures the raw maintenance request.
2. **Safety Memory Agent**: Embeds and searches the Qdrant database for LOTO procedures and near-misses.
3. **Isolation Planning Agent**: Drafts the step-by-step required safety procedure.
4. **Residual Energy Analyst Agent**: Deterministically compares real-time sensor streams to safety thresholds.
5. **Safety Critic Agent**: Reviews the combined plan and sensor readings to highlight contradictions or missing evidence.
6. **Permit Report Agent**: Generates a tamper-evident audit report for human review.
