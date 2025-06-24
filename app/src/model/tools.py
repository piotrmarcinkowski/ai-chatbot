from langchain_core.tools import tool
from datetime import datetime

@tool
def current_date():
    """
    Returns the current date in ISO 8601 format.
    """
    # TODO: Don't use depracated datetime.utcnow() method
    return datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

@tool
def search_context_in_chat_history(input_query: str):
    """
    Searches the chat history for relevant context to the input query.
    Returns a list of relevant messages.
    """
    print(f"[tool] search_context_in_chat_history: Searching chat history for context related to: {input_query}")
    return _chatbot.search_memory_for_context(input_query, top_k=5)

_chatbot = None

def init_tools(chatbot):
    """
    Initializes and returns a list of tools.
    """
    print("Initializing tools...")
    _chatbot = chatbot
    tools = [current_date, search_context_in_chat_history]
    print(f"Tools initialized: {tools}")
    return tools