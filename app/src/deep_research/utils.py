import requests
import logging
from datetime import datetime
from typing import List
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from markdownify import markdownify as md
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


def get_current_date():
    """
    Returns the current date in "Month Day, Year" format.
    """
    return datetime.now().strftime("%B %d, %Y")

def html_to_markdown(html: str) -> str:
    """
    Converts HTML content to markdown format.
    Args:
        html: The HTML content as a string.
    Returns:
        The markdown content as a string.
    """

    class CustomConverter(MarkdownConverter):
        def convert_style(self, el, text, parent_tags):
            return '' # remove style tags entirely
        def convert_script(self, el, text, parent_tags):
            return '' # remove script tags entirely
        def convert_a(self, el, text, parent_tags):
            return f"[{text}]({el.get('href')})"  # just return the link text, not the URL
        def convert_img(self, el, text, parent_tags):
            return ''  # remove images entirely
        def convert_title(self, el, text, parent_tags):
            return "Title: " + text  # convert title
        
    options = dict(
        heading_style="ATX",
        bullets="-",
        escape_asterisks=False,
        autolinks=False,
    )

    try:
        log.info("Size of HTML content: %d characters", len(html))
        markdown = CustomConverter(**options).convert(html)
        log.info("Converted HTML to Markdown, size: %d characters", len(markdown))
        return markdown
    except Exception as e:
        log.error(f"Unexpected error converting HTML to Markdown: {e}")
        return f"Unexpected error converting HTML to Markdown: {e}"

def html_to_text(html: str) -> str:
    """
    Converts HTML content to plain text.
    Args:
        html: The HTML content as a string.
    Returns:
        The plain text content as a string.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        log.info(f"Converted HTML to Text, size: {len(text)} characters")
        return text
    except Exception as e:
        log.error(f"Unexpected error converting HTML to Text: {e}")
        return f"Unexpected error converting HTML to Text: {e}"

def url_to_markdown(url: str) -> str:
    
    """
    Fetches the content of a URL and converts it to markdown format.
    Uses the requests library to fetch the HTML content and markdownify to convert it to markdown.
    Args:
        url: The URL to fetch and convert.
    Returns:
        The markdown content as a string.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # throws exception on errors (eg. 404/500)
        log.info("Fetched URL: %s with status code %s", url, response.status_code)
        html = response.text
        markdown = html_to_markdown(html)
        return markdown
    except requests.RequestException as e:
        log.error("Error fetching URL %s: %s", url, e)
        return f"Error fetching URL {url}: {e}"
    except Exception as e:
        log.error("Unexpected error processing URL %s: %s", url, e)
        return f"Unexpected error processing URL {url}: {e}"
    
if __name__ == "__main__":
    test_url = "https://www.espn.com/f1/schedule"
    print(url_to_markdown(test_url))