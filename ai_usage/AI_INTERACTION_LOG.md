# AI Interaction Log

This repository was built with AI assistance. AI was used to accelerate scaffolding, implementation, documentation, and test design. All architectural decisions, production trade-offs, and safety boundaries were reviewed as part of the implementation.

## How AI was used

- Generated the initial repository structure and FastAPI/LangGraph scaffold.
- Drafted LangGraph node implementations and SQLite persistence code.
- Created mock platform tool fixtures for a self-contained local demo.
- Produced the operator UI and API integration.
- Drafted README, architecture documentation, and test cases.

## Human engineering decisions

- Selected incident triage and safe remediation as the use case because it naturally requires autonomy, tool use, evidence, human approval, and verification.
- Kept the core workflow deterministic so the project runs without external API credentials.
- Treated LLM output as advisory; deterministic policy and approval gates remain authoritative for production mutations.
- Used SQLite checkpointing for local durable execution, with a clear path to Postgres for multi-instance production deployment.
- Made the approval boundary explicit in the graph rather than relying on prompt instructions.
- Added event persistence so an operator can inspect what the agent did and why.

## What would be improved with more time

- Add a real vector retrieval layer with citation-level grounding.
- Add LangSmith or Langfuse tracing.
- Add Postgres-backed checkpointing and background workers.
- Add comprehensive evaluation scenarios and CI quality gates.
- Add fine-grained RBAC and audit export.
