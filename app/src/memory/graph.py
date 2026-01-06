import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from memory.state import MemoryState
from memory.nodes import (
    node_generate_memory_access_queries,
    node_access_memory,
    node_analyze_results,
)
from persistence.memory import store, checkpointer

class GraphConfig(TypedDict):
    """
    Configuration for the graph.
    """
    model_name: Literal["anthropic", "openai"]
    user: str


workflow = StateGraph(MemoryState, context_schema=GraphConfig)
workflow.add_node("generate_memory_access_queries", node_generate_memory_access_queries)
workflow.add_node("access_memory", node_access_memory)
workflow.add_node("analyze_results", node_analyze_results)

workflow.add_edge(START, "generate_memory_access_queries")
workflow.add_edge("generate_memory_access_queries", "access_memory")
workflow.add_edge("access_memory", "analyze_results")
workflow.add_edge("analyze_results", END)

graph: StateGraph = None
# When running via 'langgraph dev', use the default store and checkpointer
if os.getenv("LANGSMITH_LANGGRAPH_API_VARIANT") == "local_dev":
    print("Running via 'langgraph dev', not using custom checkpointer and store")
    graph = workflow.compile()
else:
    graph = workflow.compile(store=store, checkpointer=checkpointer)

