import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from agent.state import AgentState
from agent.nodes import (
    node_user_query_input,
    node_process_query,
    node_route_after_processing,
    node_collect_knowledge,
    continue_to_knowledge_collection,
    node_web_search,
    node_memory_access,
    node_knowledge_collected,
    node_finalize_answer,
    tool_node,
    tool_call_exists,
)
from persistence.memory import store, checkpointer

class GraphConfig(TypedDict):
    """
    Configuration for the graph.
    """
    model_name: Literal["anthropic", "openai"]


workflow=StateGraph(AgentState, context_schema=GraphConfig)

workflow.add_node("user_query_input", node_user_query_input)
workflow.add_node("process_query", node_process_query)
workflow.add_node("route_after_processing", node_route_after_processing)
workflow.add_node("tools", tool_node)
workflow.add_node("collect_knowledge", node_collect_knowledge)
workflow.add_node("web_search", node_web_search)
workflow.add_node("memory_search", node_memory_access)
workflow.add_node("knowledge_collected", node_knowledge_collected)
workflow.add_node("finalize_answer", node_finalize_answer)

workflow.add_edge(START, "user_query_input")
workflow.add_edge("user_query_input", "process_query")
workflow.add_edge("process_query", "route_after_processing")

# collect knowledge and analyze again
workflow.add_conditional_edges(
    "collect_knowledge", continue_to_knowledge_collection, ["web_search", "memory_search"]
)
workflow.add_edge("web_search", "knowledge_collected")
workflow.add_edge("memory_search", "knowledge_collected")
workflow.add_edge("knowledge_collected", "finalize_answer")

# Tool calling loop for finalize_answer
workflow.add_conditional_edges(
    "finalize_answer",
    tool_call_exists,
    {True: "tools", False: END}
)
workflow.add_edge("tools", "finalize_answer")

graph: StateGraph = None
# When running via 'langgraph dev', use the default store and checkpointer
if os.getenv("LANGSMITH_LANGGRAPH_API_VARIANT") == "local_dev":
    print("Running via 'langgraph dev', not using custom checkpointer and store")
    graph = workflow.compile()
else:
    graph = workflow.compile(checkpointer=checkpointer, store=store)
print("Graph compiled successfully")