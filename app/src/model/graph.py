from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AIMessage,
    trim_messages,
)
from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator

_llm = None
_tools = None
_tools_names = []


class State(TypedDict):
    """Represents the state of the chatbot.
    Specifies what type of information will flow between different nodes and edges in a graph.
    """

    messages: Annotated[list[AnyMessage], operator.add]


def run_llm(state: State):
    messages = state["messages"]
    message = _llm.invoke(messages)
    return {"messages": [message]}


def execute_tools(state: State):
    """
    Function that executes whenever an agent decides to call one or more tools
    """
    tool_calls = state["messages"][-1].tool_calls
    results = []
    for t in tool_calls:

        if not t["name"] in _tools_names:
            result = "Error: There's no such tool, please try again"
        else:
            result = _tools_names[t["name"]].invoke(t["args"])

            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )

    return {"messages": results}


def tool_exists(state: State):
    """
    Checks whether the agent's latest state contains tool calls.
    This function is used to create a conditional edge, 
    which decides whether to go to the execute_tools() function or 
    the END node and returns the agent’s final response. 
    """
    result = state['messages'][-1]
    return len(result.tool_calls) > 0


def init_state_graph(llm, tools):
    """
    Initializes the state graph for the chatbot.
    """
    global _llm, _tools, _tools_names
    _llm = llm
    _tools = tools
    _tools_names = {t.name: t for t in tools}

    graph_builder=StateGraph(State)
    graph_builder.add_node("llm", run_llm)
    graph_builder.add_node("tools", execute_tools)
    graph_builder.add_conditional_edges(
    "llm",
     tool_exists,
    {True: "tools", False: END}
    )

    graph_builder.add_edge("tools", "llm")

    graph_builder.set_entry_point("llm")
    return graph_builder.compile()
