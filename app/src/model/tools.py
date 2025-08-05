from langchain_core.tools import tool
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from pydantic import BaseModel, Field
from datetime import datetime, timezone

@tool
def current_utc_time():
    """
    Returns the current UTC time in the ISO 8601 format.
    """
    now = datetime.now(tz=timezone.utc).isoformat()
    return now

@tool
def current_local_time():
    """
    Returns the current local date and time. Use to get time in the current timezone.
    """
    # Get current local time (based on system timezone)
    local_now = datetime.now().astimezone()
    return local_now

@tool
def local_time_zone():
    """
    Returns the current local timezone.
    """
    local_tz = datetime.now().astimezone().tzinfo
    return str(local_tz)

@tool
def search_context_in_chat_history(input_query: str):
    """
    Searches the chat history for relevant context to the input query.
    Returns a list of relevant messages.
    """
    print(f"[tool] search_context_in_chat_history: Searching chat history for context related to: {input_query}")
    return _chatbot.search_memory_for_context(input_query, top_k=5)


class ArxivTopic(BaseModel):
    topic: str = Field(description="The topic of the article to search on arxiv.")

@tool (args_schema=ArxivTopic)
def arxiv_search(topic: str) -> str:
    """Returns the information about research papers from arxiv"""
    arxiv_api=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    arxiv_tool=ArxivQueryRun(api_wrapper=arxiv_api)
    print("Tool: arxiv_search - query: ", topic)
    result = arxiv_tool.invoke(topic)
    print("Tool: arxiv_search - result: ", result)    


class WikipediaTopic(BaseModel):
    topic: str = Field(description="The wikipedia article topic to search")

@tool(args_schema = WikipediaTopic)
def wikipedia_search(topic: str) -> str:
    """Returns the summary of wikipedia page of the passed topic"""
    api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    wiki_tool=WikipediaQueryRun(api_wrapper=api_wrapper)
    print("Tool: get_wiki_data - query: ", topic)
    result = wiki_tool.invoke(topic)
    print("Tool: get_wiki_data - result: ", result)
    return result


_chatbot = None

def init_tools(chatbot):
    """
    Initializes and returns a list of tools.
    """
    print("Initializing tools...")
    global _chatbot
    _chatbot = chatbot
    tools = [current_utc_time, current_local_time, local_time_zone,
             search_context_in_chat_history,
             arxiv_search, wikipedia_search]
    
    print(f"Tools initialized: {tools}")
    return tools