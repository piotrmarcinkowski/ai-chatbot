from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from agent.state import AgentState
from agent.nodes import (
    node_analyze_user_query,
    tool_node,
    tool_call_exists,
    node_generate_knowledge_search_query,
    continue_to_knowledge_collection,
    node_web_search,
    node_memory_search,
    node_knowledge_collected,
    node_continue_to_query_router,
    select_route
)
from persistence.memory import store, checkpointer

class GraphConfig(TypedDict):
    """
    Configuration for the graph.
    """
    model_name: Literal["anthropic", "openai"]


workflow=StateGraph(AgentState, context_schema=GraphConfig)

workflow.add_node("analyze_query", node_analyze_user_query)
workflow.add_node("tools", tool_node)
workflow.add_node("route_query", node_continue_to_query_router)
workflow.add_node("generate_search_queries", node_generate_knowledge_search_query)
workflow.add_node("web_search", node_web_search)
workflow.add_node("memory_search", node_memory_search)
workflow.add_node("knowledge_collected", node_knowledge_collected)

workflow.add_edge(START, "analyze_query")

workflow.add_conditional_edges(
    "analyze_query",
    tool_call_exists,
    {True: "tools", False: "route_query"}
)
workflow.add_edge("tools", "analyze_query")

workflow.add_conditional_edges(
    "route_query",
    select_route,
    {
        "knowledge_collection": "generate_search_queries", 
        "END": END
    }
)

workflow.add_conditional_edges(
    "generate_search_queries", continue_to_knowledge_collection, ["web_search", "memory_search"]
)
workflow.add_edge("web_search", "knowledge_collected")
workflow.add_edge("memory_search", "knowledge_collected")
workflow.add_edge("knowledge_collected", "analyze_query")


#graph = workflow.compile(checkpointer=checkpointer, store=store)
graph = workflow.compile(store=store)
