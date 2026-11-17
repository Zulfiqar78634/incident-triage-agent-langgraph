"""Composition root and dependency-injection container."""

from __future__ import annotations

from dataclasses import dataclass

from incident_agent.agent.diagnosis.strategies import (
    DeterministicDiagnosisStrategy,
    DiagnosisSupervisor,
    GeminiDiagnosisStrategy,
)
from incident_agent.application.policies import ApprovalPolicy, RetryPolicy
from incident_agent.application.tool_registry import ToolRegistry
from incident_agent.core.settings import Settings, load_settings
from incident_agent.infrastructure.llm.gemini_client import GeminiClient
from incident_agent.infrastructure.llm.null_client import NullLLMClient
from incident_agent.infrastructure.persistence.sqlite_store import SQLiteRunRepository
from incident_agent.infrastructure.platform.mock_platform import MockPlatform
from incident_agent.infrastructure.platform.tool_specs import build_default_registry


@dataclass
class Runtime:
    settings: Settings
    platform: MockPlatform
    llm: object
    repository: SQLiteRunRepository
    tools: ToolRegistry
    approval_policy: ApprovalPolicy
    retry_policy: RetryPolicy
    diagnosis: DiagnosisSupervisor


def build_runtime() -> Runtime:
    settings = load_settings()
    platform = MockPlatform()

    if settings.gemini_api_key:
        llm = GeminiClient(settings)
        strategies: list = [GeminiDiagnosisStrategy(llm)]
    else:
        llm = NullLLMClient()
        strategies = []

    strategies.append(DeterministicDiagnosisStrategy())

    return Runtime(
        settings=settings,
        platform=platform,
        llm=llm,
        repository=SQLiteRunRepository(settings.db_path),
        tools=build_default_registry(platform),
        approval_policy=ApprovalPolicy(),
        retry_policy=RetryPolicy(),
        diagnosis=DiagnosisSupervisor(strategies),
    )
