from langchain_core.tools import tool
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from pydantic import BaseModel, Field
from utils.time import get_current_local_time, get_current_time, get_local_time_zone
from langchain_google_community import GoogleSearchAPIWrapper
import os
import logging

log = logging.getLogger(__name__)

@tool
def current_utc_time():
    """
    Returns the current UTC time in the ISO 8601 format.
    """
    now = get_current_time()
    return now

@tool
def current_local_time():
    """
    Returns the current local date and time. Use to get time in the current timezone.
    """
    # Get current local time (based on system timezone)
    local_now = get_current_local_time()
    return local_now

@tool
def local_time_zone():
    """
    Returns the current local timezone.
    """
    local_tz = get_local_time_zone()
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
    _tools = [current_utc_time, current_local_time, local_time_zone,
             arxiv_search, wikipedia_search
    ]

    # Initialize Google search tool with API key and CSE ID
    _google_api_key = os.getenv("GOOGLE_API_KEY")
    _google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if _google_api_key and _google_cse_id:
        log.info("Google API key and CSE ID found - activating Google search tool.")
        _tools.append(google_web_search)
    else:
        log.warning("Google API key and CSE ID must be set in environment variables. Google search tool will not be available.")
    
    log.info(f"Tools initialized: {_tools}")
    return _tools

tools = init_tools()
