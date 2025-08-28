import os
import logging
from datetime import datetime, date
from langchain_core.tools import tool
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from pydantic import BaseModel, Field
from utils.time import current_local_time, current_utc_time, local_time_zone
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_tavily import TavilySearch

log = logging.getLogger(__name__)

@tool("current_datetime", return_direct=True)
def get_current_datetime() -> str:
    """
    Returns the current date and time in ISO format.
    Useful when reasoning about upcoming events, schedules, or time-dependent calculations.
    """
    return current_local_time()

@tool
def get_current_utc_time():
    """
    Returns the current UTC time in the ISO 8601 format.
    """
    now = current_utc_time()
    return now

@tool("date_difference", return_direct=True)
def date_difference(target_date: str) -> str:
    """
    Calculates the number of days between today and a given target date.
    Input must be in the format 'YYYY-MM-DD'.
    Returns a human-readable difference (past or future).
    """
    try:
        today = date.today()
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        delta = (target - today).days

        if delta > 0:
            return f"There are {delta} days until {target}."
        elif delta < 0:
            return f"{abs(delta)} days have passed since {target}."
        else:
            return f"Today is {target}."
    except Exception as e:
        return f"Error: invalid date format. Please provide 'YYYY-MM-DD'. ({str(e)})"

@tool("local_time_zone", return_direct=True)
def get_local_time_zone():
    """
    Returns the current local timezone.
    """
    local_tz = local_time_zone()
    return str(local_tz)

class ArxivTopic(BaseModel):
    topic: str = Field(description="The topic of the article to search on arxiv.")

@tool (args_schema=ArxivTopic)
def arxiv_search(topic: str) -> str:
    """Returns the information about research papers from arxiv"""
    arxiv_api=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    arxiv_tool=ArxivQueryRun(api_wrapper=arxiv_api)
    log.debug("Tool: arxiv_search - query: %s", topic)
    result = arxiv_tool.invoke(topic)
    log.debug("Tool: arxiv_search - result: %s", result)
    return result


class WikipediaTopic(BaseModel):
    topic: str = Field(description="The wikipedia article topic to search")

@tool(args_schema = WikipediaTopic)
def wikipedia_search(topic: str) -> str:
    """Returns the summary of wikipedia page of the passed topic"""
    api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    wiki_tool=WikipediaQueryRun(api_wrapper=api_wrapper)
    log.debug("Tool: get_wiki_data - query: %s", topic)
    result = wiki_tool.invoke(topic)
    log.debug("Tool: get_wiki_data - result: %s", result)
    return result

@tool
def google_web_search(query: str) -> str:
    """
    Searches the web using Google Custom Search Engine (CSE) and returns the top results.
    """

    google_search = GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID")
    )
    results = google_search.results(query=query, num_results=5)
    log.debug("Google search results for query '%s': %s", query, results)
    return results

def init_tools():
    """
    Initializes and returns a list of tools.
    """
    log.info("Initializing tools...")
    _tools = [get_current_datetime, date_difference, get_current_utc_time, get_local_time_zone,
             arxiv_search, wikipedia_search
    ]

    init_tavily_search_tool(_tools)
    init_google_search_tool(_tools)
    
    log.info("Tools initialized: %s", _tools)
    return _tools

def init_tavily_search_tool(tools_list):
    """
    Initialize Tavily search tool with API key
    """
    _tavily_api_key = os.getenv("TAVILY_API_KEY")
    if _tavily_api_key:
        log.info("Tavily API key found - activating Tavily search tool.")
        tools_list.append(TavilySearch(max_results=2, include_answer=True, include_raw_content=False, auto_parameters=True))
    else:
        log.warning("Tavily API key must be set in environment variables. Tavily search tool will not be available.")

def init_google_search_tool(tools_list):
    """
    Initialize Google search tool with API key and CSE ID
    """
    _google_api_key = os.getenv("GOOGLE_API_KEY")
    _google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if _google_api_key and _google_cse_id:
        log.info("Google API key and CSE ID found - activating Google search tool.")
        tools_list.append(google_web_search)
    else:
        log.warning("Google API key and CSE ID must be set in environment variables. Google search tool will not be available.")

tools = init_tools()
