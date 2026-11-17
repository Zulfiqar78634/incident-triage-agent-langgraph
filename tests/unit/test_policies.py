from incident_agent.application.policies import ApprovalPolicy


def test_read_only_tool_does_not_require_approval():
    policy = ApprovalPolicy()

    assert policy.requires_approval(
        mutating=False,
        default_requires_approval=False,
        environment="production",
    ) is False


def test_production_mutation_requires_approval():
    policy = ApprovalPolicy()

    assert policy.requires_approval(
        mutating=True,
        default_requires_approval=True,
        environment="production",
    ) is True
