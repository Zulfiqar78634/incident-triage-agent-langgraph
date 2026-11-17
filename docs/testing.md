# Testing

The project uses tests to validate both agent behavior and safety boundaries.

The most important tests are not merely “does the LLM respond?” They verify that the agent investigates, pauses for approval, executes only approved actions, verifies recovery, and refuses to execute rejected actions.

## Run tests

From the repository root:

```bash
pip install -r requirements.txt
pytest -q
```

For verbose output:

```bash
pytest -v
```

## Testing philosophy

The tests focus on observable behavior:

- The API starts correctly.
- An incident creates a run.
- The agent reaches the approval state.
- Approval resumes the workflow.
- Rejection prevents execution.
- A successful rollback updates platform state.
- Verification detects recovery.
- The run reaches a final state.

This approach tests the safety-critical workflow rather than relying only on mocked internals.

## Test layers

| Layer | Purpose | Examples |
|---|---|---|
| Unit tests | Validate focused logic | Classification, context building, policies, tool validation |
| Integration tests | Validate end-to-end API and workflow behavior | Create run, approve rollback, verify recovery |
| Safety tests | Validate human-in-the-loop boundaries | Rejection prevents execution; approval is required before mutation |
| Contract tests | Validate adapter interfaces | Platform, LLM, and repository ports |

## Current integration coverage

The integration suite covers the main local demo path:

```text
Create incident
→ Agent triages and investigates
→ Agent diagnoses deployment-related DB regression
→ Agent proposes rollback
→ Agent pauses for approval
→ Operator approves
→ Rollback executes
→ Metrics and service health recover
→ Verification succeeds
→ Run completes
```

### Health check

Verifies that the FastAPI service is available and healthy.

### Approval interruption

Verifies that a checkout-service incident reaches `awaiting_approval` and proposes `rollback_deployment`.

### Approved rollback

Verifies that approval resumes the workflow, executes the rollback, updates mock metrics and service health, verifies recovery, and completes the run.

### Rejection safety

Verifies that rejection cancels the run and does not execute the proposed action.

## Safety assertions

The tests intentionally assert:

- A mutating rollback requires approval.
- The run pauses before execution.
- Rejection results in `cancelled`.
- Rejection does not execute the tool.
- Approval results in execution.
- Execution is followed by verification.
- Recovery is based on post-action metrics and service health.
- Successful verification produces a `completed` run.

## Future test roadmap

| Area | Future test |
|---|---|
| Tool validation | Invalid arguments are rejected before execution |
| Retry behavior | Transient tool failures retry according to policy |
| LLM failure | Gemini failure falls back to deterministic diagnosis |
| Persistence | Run state and events survive process restart |
| Concurrency | Multiple runs do not interfere with one another |
| Authorization | Only authorized operators can approve actions |
| Audit export | Event traces can be exported for compliance |

## Interview-ready explanation

> “I test the safety-critical workflow, not just the LLM output. The integration tests verify that the agent pauses for approval, executes only after approval, updates the mock platform, verifies recovery, and reaches a completed state. I also test rejection: if the operator rejects the action, the agent cancels the run and does not execute anything. This demonstrates that autonomy is controlled by deterministic policy and human oversight.”
