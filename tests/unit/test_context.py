from incident_agent.agent.context import estimate_tokens, select_evidence


def test_estimate_tokens_is_positive():
    assert estimate_tokens("hello world") > 0


def test_select_evidence_respects_budget():
    evidence = [
        {"id": "ev_01", "content": "short evidence"},
        {"id": "ev_02", "content": "another evidence item"},
    ]

    selected = select_evidence(evidence, budget=100)

    assert len(selected) == 2


def test_select_evidence_stops_when_budget_exceeded():
    evidence = [
        {"id": "ev_01", "content": "x" * 1000},
        {"id": "ev_02", "content": "small"},
    ]

    selected = select_evidence(evidence, budget=10)

    assert selected == []
