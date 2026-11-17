from pydantic import BaseModel

from incident_agent.application.tool_registry import ToolRegistry, ToolSpec
from incident_agent.domain.enums import Risk


class EchoInput(BaseModel):
    message: str


def echo(message: str) -> dict:
    return {"success": True, "message": message}


def test_registry_executes_valid_tool():
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo",
            description="Echo a message",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=EchoInput,
            handler=echo,
        )
    )

    result = registry.execute("echo", {"message": "hello"})

    assert result.success is True
    assert result.data["message"] == "hello"


def test_registry_rejects_invalid_arguments():
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo",
            description="Echo a message",
            risk=Risk.LOW,
            mutating=False,
            requires_approval=False,
            input_model=EchoInput,
            handler=echo,
        )
    )

    result = registry.execute("echo", {})

    assert result.success is False
    assert "Invalid arguments" in result.error
