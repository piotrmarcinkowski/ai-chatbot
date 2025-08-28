from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from agent.state import AgentState
from agent.nodes import call_model, tool_node, tool_call_exists
from persistence.memory import store, checkpointer

class GraphConfig(TypedDict):
    """
    Configuration for the graph.
    """
    model_name: Literal["anthropic", "openai"]


workflow=StateGraph(AgentState, context_schema=GraphConfig)

workflow.add_node("llm", call_model)
workflow.add_node("tools", tool_node)

workflow.add_conditional_edges(
    "llm",
    tool_call_exists,
    {True: "tools", False: END}
)

workflow.add_edge(START, "llm")
workflow.add_edge("tools", "llm")

#graph = workflow.compile(checkpointer=checkpointer, store=store)
graph = workflow.compile(store=store)
