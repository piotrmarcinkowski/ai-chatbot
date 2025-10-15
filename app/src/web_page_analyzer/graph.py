from langgraph.graph import StateGraph
from langgraph.graph import START, END

from web_page_analyzer.state import (
    AnalyserState,
)
from web_page_analyzer.nodes import (
    web_scraping,
    web_content_analysis,
)

builder = StateGraph(AnalyserState)

builder.add_node("web_scraping", web_scraping)
builder.add_node("web_content_analysis", web_content_analysis)

builder.add_edge(START, "web_scraping")
builder.add_edge("web_scraping", "web_content_analysis")
builder.add_edge("web_content_analysis", END)

graph = builder.compile(name="web_page_analyzer")