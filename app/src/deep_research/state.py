from __future__ import annotations

import operator

from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated

class SearchQueryState(TypedDict):
    """
    State to hold search queries.
    """
    search_query: Annotated[list, operator.add, "List of search queries generated to gather more information for answering the user's query."]

class SearchResultState(TypedDict):
    """
    State to hold search results.
    """
    web_research_result: Annotated[list, operator.add, "List of web research results gathered from web searches."]
    web_scraping_result: Annotated[list, operator.add, "List of web scraping results gathered from scraping web pages."]

class OverallState(SearchQueryState, SearchResultState):
    """
    Main state of the deep research agent.
    """
    messages: Annotated[list, add_messages]
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


class Query(TypedDict):
    """
    A single search query with rationale.
    """
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """
    State for generating search queries.
    """
    search_query: list[Query]


class WebSearchState(TypedDict):
    """
    State for conducting web searches and gathering results.
    """
    search_query: str
    id: str

class WebSearchResultsState(TypedDict):
    """
    State for web search results.
    """
    web_research_result: list[str]
    web_scraping_result: list[str]


class WebScrapingState(TypedDict):
    """
    State for scraping web pages.
    """
    url: str
    id: str

@dataclass(kw_only=True)
class SearchStateOutput:
    """
    Output state after conducting web searches.
    """
    running_summary: str = field(default=None)  # Final report
