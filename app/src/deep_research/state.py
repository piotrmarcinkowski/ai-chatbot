import operator

from typing import TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import Annotated

class WebResearchQuery(TypedDict):
    """
    A single web research query with rationale.
    """
    user_query: Annotated[str, ..., "Condensed user query best describing the research topic and what the user wants"]  
    search_query: Annotated[str, ..., "Query to answer by analyzing web page content."]
    rationale: Annotated[str, ..., "Rationale for the web content analysis."]

class WebResearchResult(WebResearchQuery):
    """
    A single web research result.
    """
    url: Annotated[str, ..., "URL returned from web search."]

class GenerateQueryState(TypedDict):
    """
    State for generating web research queries.
    """
    user_query: Annotated[str, ..., "Condensed user query best describing the research topic and what the user wants"]
    web_research_queries: Annotated[list, operator.add]

class WebResearchResultState(GenerateQueryState):
    """
    State for holding web research results which include collected links from web research.
    """
    web_research_results: Annotated[list, operator.add]

class WebContentAnalysisResultState(WebResearchResultState):
    """
    State for holding web content analysis results.
    """
    web_content_analysis_results: Annotated[list, operator.add]

class OverallState(WebContentAnalysisResultState):
    """
    Main state of the deep research agent.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str

class ReflectionState(TypedDict):
    """
    State for reflection on the provided summaries about a research topic.
    """
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int