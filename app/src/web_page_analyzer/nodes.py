import os
import logging
from langchain_openai import ChatOpenAI
from web_page_analyzer.state import (
    InputState,
    ScrapingState,
    AnalyserState,
)
from web_page_analyzer.prompts import (
    web_content_analyzer_instructions,
)
from web_page_analyzer.utils import (
    url_to_markdown,
    get_current_date,
)

log = logging.getLogger(__name__)

def web_scraping(state: InputState) -> ScrapingState:
    """
    LangGraph node that performs web scraping to extract content from a given URL.
    Fetches the content of the specified URL and converts it to markdown format for 
    easier processing.
    """
    return {
        "page_content": url_to_markdown(state["url"]),
    }

def web_content_analysis(state: ScrapingState) -> AnalyserState:
    """
    LangGraph node that analyzes the content of a scraped web page and provides an answer 
    to the user's query.
    """

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = web_content_analyzer_instructions.format(
        search_query=state["search_query"],
        current_date=current_date,
        scraped_page=state["page_content"],
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    result = llm.invoke(formatted_prompt)

    return {
        "analysis_result": result.content
    }
