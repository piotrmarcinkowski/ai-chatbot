from langgraph.graph import StateGraph
from langgraph.graph import START, END

from deep_research.state import (
    OverallState,
)
from deep_research.configuration import Configuration
from deep_research.nodes import (
    generate_query,
    web_research,
    web_content_analysis,
    reflection,
    node_finalize_answer,
    continue_to_web_research,
    continue_to_web_content_analysis,
    evaluate_research,
)

builder = StateGraph(OverallState, config_schema=Configuration)

builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("web_content_analysis", web_content_analysis)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", node_finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
builder.add_conditional_edges(
    "web_research", continue_to_web_content_analysis, ["web_content_analysis"]
)
# Reflect on the web research
builder.add_edge("web_content_analysis", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="deep-research-agent")