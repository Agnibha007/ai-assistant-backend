import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_id: int
    status: str  # "planning", "executing", "waiting_for_user", "completed"
    pending_actions: list[dict]
