# AI Interaction Log

This repository was built with AI assistance.

## How AI was used

- Generated the initial repository structure and FastAPI/LangGraph scaffold.
- Drafted LangGraph nodes, state model, and SQLite persistence.
- Created mock platform tool fixtures for a self-contained local demo.
- Produced the React TypeScript operator console.
- Drafted README, architecture, HLD/LLD, and test documentation.

## Human engineering decisions

- Selected incident triage and safe remediation as the use case because it naturally requires autonomy, tool use, evidence, human approval, and verification.
- Kept the core workflow deterministic so the project runs without external API credentials.
- Treated Gemini output as advisory; deterministic policy and approval gates remain authoritative for production mutations.
- Used SQLite checkpointing for local durable execution, with a clear path to Postgres for multi-instance deployment.
- Made the approval boundary explicit in the LangGraph workflow rather than relying on prompt instructions.
- Added event persistence so an operator can inspect what the agent did and why.
- Separated domain, application, agent, infrastructure, and API layers to apply SOLID principles.

## What would be improved with more time

- Add real vector retrieval with citation-level grounding.
- Add LangSmith or Langfuse tracing.
- Add Postgres-backed checkpointing and background workers.
- Add comprehensive evaluation scenarios and CI quality gates.
- Add fine-grained RBAC and audit export.
