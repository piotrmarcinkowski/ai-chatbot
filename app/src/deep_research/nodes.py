import os
import logging

from langchain_core.messages import AIMessage
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_google_community import GoogleSearchAPIWrapper

from deep_research.schema import SearchQueryList, Reflection
from deep_research.configuration import Configuration
from deep_research.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
    WebSearchResultsState,
    WebScrapingState,
)
from deep_research.prompts import (
    query_writer_instructions,
    reflection_instructions,
    answer_instructions,
)
from deep_research.utils import (
    get_research_topic,
    url_to_markdown,
    get_current_date,
)

log = logging.getLogger(__name__)

def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates search queries based on the User's question.

    Uses LLM model to create an optimized search queries for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries
    """
    if len(state.get("search_query", [])) > 0:
        # If we already have search queries, do not generate new ones.
        # This situation can happen when the agent was called from other 
        # agent that already generated search queries.
        log.info("Search queries already exist, skipping generation.")
        return {"search_query": state["search_query"]}

    configurable = Configuration.from_runnable_config(config)

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    llm = ChatOpenAI(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    return {"search_query": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using the native Google Search API tool.

    Executes a web search using the native Google Search API tool in combination with Gemini 2.0 Flash.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including research_loop_count, and web_research_results
    """
    configurable = Configuration.from_runnable_config(config)

    google_search = GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID")
    )
    results = google_search.results(
        query=state["search_query"],
        num_results=configurable.number_of_results_per_query
    )
    urls = [result["link"] for result in results]
    
    return {
        "search_query": [state["search_query"]],
        "web_research_result": urls,
    }

def continue_to_web_scraping(state: WebSearchResultsState):
    """LangGraph node that sends the web research results to the web scraping node.

    This is used to spawn n number of web scraping nodes, one for each url query.
    """
    num_of_urls = len(state["web_research_result"])
    num_of_scrapings = len(state.get("web_scraping_result", []))
    # only scraping urls that have not been scraped yet
    if num_of_urls <= num_of_scrapings:
        return []
    
    return [
        Send("web_scraping", {"url": url, "id": int(idx)})
        for idx, url in enumerate(state["web_research_result"][num_of_scrapings:])
    ]

def web_scraping(state: WebScrapingState) -> OverallState:
    """LangGraph node that performs web scraping to extract content from a given URL.

    Fetches the content of the specified URL and converts it to markdown format for easier processing.

    Args:
        state: Current graph state containing the URL to be scraped
        config: Configuration for the runnable (not used in this function)

    Returns:
        Dictionary with state update, including web_research_result key containing the scraped content in markdown format
    """
    return {
        "web_scraping_result": [url_to_markdown(state["url"])],
    }

def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model", configurable.reflection_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        research_topic=get_research_topic(state["messages"]),
        current_date=current_date,
        scraped_pages="\n\n---\n\n".join(str(state["web_scraping_result"])),
    )
    log.info(f"Reflection Prompt: {formatted_prompt}")
    # init Reasoning Model
    llm = ChatOpenAI(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        scraped_pages="\n---\n\n".join(str(state["web_scraping_result"])),
    )

    # init Reasoning Model
    llm = ChatOpenAI(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    result = llm.invoke(formatted_prompt)

    return {
        "messages": [AIMessage(content=result.content)],
    }
