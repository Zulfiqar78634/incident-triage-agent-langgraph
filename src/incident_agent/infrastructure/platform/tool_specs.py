"""Tool specifications and default registry construction."""

from __future__ import annotations

from pydantic import BaseModel, Field

from incident_agent.application.tool_registry import ToolRegistry, ToolSpec
from incident_agent.domain.enums import Risk
from incident_agent.infrastructure.platform.mock_platform import MockPlatform


class SearchLogsInput(BaseModel):
    service: str
    query: str = ""
    limit: int = Field(default=10, ge=1, le=100)


class QueryMetricsInput(BaseModel):
    service: str
    window_minutes: int = Field(default=15, ge=1, le=1440)


class ServiceInput(BaseModel):
    service: str


class DeploymentHistoryInput(BaseModel):
    service: str
    limit: int = Field(default=5, ge=1, le=20)


class RunbookSearchInput(BaseModel):
    query: str


class RollbackInput(BaseModel):
    service: str
    to_version: str
    idempotency_key: str


class RestartInput(BaseModel):
    service: str
    idempotency_key: str


def build_default_registry(platform: MockPlatform) -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="search_logs",
            description="Search recent application logs for a service.",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=SearchLogsInput,
            handler=platform.search_logs,
        )
    )

    registry.register(
        ToolSpec(
            name="query_metrics",
            description="Query service health metrics.",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=QueryMetricsInput,
            handler=platform.query_metrics,
        )
    )

    registry.register(
        ToolSpec(
            name="get_service_status",
            description="Get current service and dependency health.",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=ServiceInput,
            handler=platform.get_service_status,
        )
    )

    registry.register(
        ToolSpec(
            name="get_deployment_history",
            description="Get recent deployments for change correlation.",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=DeploymentHistoryInput,
            handler=platform.get_deployment_history,
        )
    )

    registry.register(
        ToolSpec(
            name="search_runbooks",
            description="Search approved operational runbooks.",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=RunbookSearchInput,
            handler=platform.search_runbooks,
        )
    )

    registry.register(
        ToolSpec(
            name="rollback_deployment",
            description="Roll a service back to a previous version.",
            risk=Risk.HIGH,
            mutating=True,
            requires_approval=True,
            input_model=RollbackInput,
            handler=platform.rollback_deployment,
        )
    )

    registry.register(
        ToolSpec(
            name="restart_service",
            description="Restart a degraded service.",
            risk=Risk.HIGH,
            mutating=True,
            requires_approval=True,
            input_model=RestartInput,
            handler=platform.restart_service,
        )
    )

    return registry
