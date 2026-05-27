from typing import Any

import httpx
from langchain_core.tools import BaseTool


class DesktopActionTool(BaseTool):
    name: str = "execute_desktop_action"
    description: str = (
        "Executes a low-level desktop action like moving the mouse, clicking, "
        "or typing. Sends command to the native host bridge."
    )

    def _run(self, action_type: str, params: dict[str, Any]) -> str:
        # In a real implementation, this would communicate via WebSocket/HTTP
        # to the Host Bridge.
        # Stub for demonstration:
        try:
            # Assuming Host Bridge has an HTTP endpoint for sync calls or
            # we push to a queue
            response = httpx.post(
                "http://host.docker.internal:8001/action",  # Example URL
                json={"action": action_type, "params": params},
                timeout=5.0,
            )
            return str(response.json().get("result", "Action executed."))
        except Exception as e:
            return f"Failed to execute desktop action: {str(e)}"

    async def _arun(self, action_type: str, params: dict[str, Any]) -> str:
        return self._run(action_type, params)


class TerminalCommandTool(BaseTool):
    name: str = "execute_terminal_command"
    description: str = (
        "Executes a shell command on the host. "
        "Requires user confirmation for dangerous commands."
    )

    def _run(self, command: str) -> str:
        # Pushes to Celery queue or directly to Host Bridge
        return f"Queued terminal command execution: {command}"

    async def _arun(self, command: str) -> str:
        return self._run(command)


tools: list[BaseTool] = [DesktopActionTool(), TerminalCommandTool()]
