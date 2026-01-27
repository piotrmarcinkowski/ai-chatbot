"""
State definitions for the agent.
Follows this guide: https://python.langchain.com/docs/how_to/structured_output
"""
import operator
from typing import Optional, TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Represents the base state of the chatbot.
    Specifies what type of information will flow 
    between different nodes and edges in a graph.
    """
    user_query: Annotated[str, ..., "The original query provided by the user."]
    user: Annotated[str, ..., "The user name determined during the query processing."]
    messages: Annotated[list[BaseMessage], add_messages]

class CollectedKnowledgeState(AgentState):
    """
    State for holding collected knowledge.
    """
    knowledge_search_results: Annotated[list, operator.add]
    memory_access_registry: Annotated[list, operator.add]

class ProcessQueryState(CollectedKnowledgeState):
    """
    State for processing the user query.
    Extends CollectedKnowledgeState with processing-specific fields.
    This is the most complete state type and should be used by most nodes.
    """
    processing_iteration: Annotated[int, ..., "The current iteration of processing the query."]
    user_preferences: Annotated[Optional[dict], ..., "The user preferences that may influence the answer generation."]
    processing_summary: Annotated[str, ..., "A concise summary of the query processing and decisions made."]
    processing_answer: Annotated[str, ..., "The answer to the user's query from processing."]
    requires_web_search: Annotated[bool, ..., "Whether the query requires a web search to answer, eg. if user asks for current events (publicly known)"]
    requires_long_term_memory_access: Annotated[bool, ..., "Whether the query requires access to long-term memory to answer, eg user refers to past conversations or personal data. The user name is required to access long-term memory."]
    instructions_for_web_search: Annotated[Optional[str], ..., "Specific instructions or search queries for the web search agent."]
    instructions_for_long_term_memory_access: Annotated[Optional[str], ..., "Specific instructions for what to look for in long-term memory."]
