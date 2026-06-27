# ZERA AI Demo Script (3 Minutes)

**0:00–0:20 | The Problem**
"Industrial machinery may retain hazardous stored energy—like hydraulic pressure or gravitational potential—even after the main power is switched off. Traditional Lockout/Tagout relies on paper checklists, and often misses latent risks. Because switching off is not the same as proving zero energy."

**0:20–0:40 | The Solution & Architecture**
"Enter ZERA AI: Zero-Energy Release Assurance Agent. It’s an agentic decision-support layer built with Google ADK, Gemini, and Qdrant. ZERA uses a six-agent architecture to synthesize task requirements, retrieve historical near-misses, generate an isolation plan, evaluate sensor readings deterministically, and conduct an independent safety review."

**0:40–1:25 | Unsafe Scenario**
"Let's run a new assessment on Hydraulic Press HP-01. In this Unsafe Scenario, the hydraulic pressure is dangerously high at 42 bar, the ram is raised without a mechanical block, and a try-start was omitted. We run the Agentic Safety Assessment... and as expected, ZERA blocks the maintenance. It provides a RED status and clearly lists the blocking hazards and recommended corrective actions."

**1:25–1:50 | Memory & Retrieval**
"How did ZERA know what to check? We navigate to the Safety Memory tab. ZERA’s Safety Memory Agent retrieved crucial near-misses from Qdrant, such as Incident HM-2025-07, where a leaking valve caused a pressure rebound. ZERA integrates these past lessons into the current isolation plan."

**1:50–2:10 | Execution Trace**
"In the Agent Execution Trace tab, we can verify exactly how ZERA reached its conclusion. You can see all six agents—Intake, Memory, Planning, Analyst, Critic, and Reporter—executing sequentially, ensuring the decision is transparent and auditable."

**2:10–2:40 | Corrective Actions & Re-run**
"Now, let's apply the recommended corrective actions. We relieve the pressure to 0.5 bar, install the mechanical block, and complete the try-start verification. We rerun the workflow..."

**2:40–2:55 | Success Status**
"The system evaluates the new sensor data and returns a GREEN status. However, notice it says: 'READY FOR AUTHORIZED HUMAN REVIEW'. ZERA does not autonomously approve maintenance—it prepares a verified, tamper-evident Permit Report for the supervisor."

**2:55–3:00 | Tagline**
"ZERA AI. Because switching off is not the same as proving zero energy."
