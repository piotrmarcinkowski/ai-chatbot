from typing import TypedDict
from typing_extensions import Annotated


class InputState(TypedDict):
    """
    State to hold search results.
    """
    search_query: Annotated[str, ..., "Query to answer by analyzing web page content."]
    url: Annotated[str, ..., "Url of the web page to analyze."]

class ScrapingState(InputState):
    """
    State for scraping web pages.
    """
    page_content: Annotated[str, ..., "Downloaded web page, stores filtered content in markdown."]

class AnalyserState(ScrapingState):
    """
    State for scraped web page content analysis.
    """
    analysis_result: Annotated[str, ..., "Result of web content analysis with answer to the query."]
