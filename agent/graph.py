from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

from agent.state import AgentState
from agent.tools import tools

# In a real implementation, keys would be fetched dynamically from
# the encrypted user vault
# We're using OpenRouter/Groq compatibility via ChatOpenAI
llm = ChatOpenAI(
    api_key=SecretStr("dummy_key"),
    base_url="https://openrouter.ai/api/v1",
    model="anthropic/claude-3-haiku",
)

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def execute_tools_node(state: AgentState) -> dict[str, Any]:
    messages = state["messages"]
    last_message = messages[-1]

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"messages": []}

    tool_responses: list[BaseMessage] = []
    # Simplified tool execution loop
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Dispatch to the actual tool
        for t in tools:
            if t.name == tool_name:
                result = t.invoke(tool_args)
                msg_content = f"Tool {tool_name} returned: {result}"
                tool_responses.append(AIMessage(content=msg_content))

    return {"messages": tool_responses}


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "execute_tools"
    return END


# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("execute_tools", execute_tools_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("execute_tools", "agent")

app = workflow.compile()
