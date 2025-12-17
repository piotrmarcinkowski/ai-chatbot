"""
State definitions for the agent.
Follows this guide: https://python.langchain.com/docs/how_to/structured_output
"""
import operator
from typing import Optional, TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class KnowledgeSearchQuery(TypedDict):
    """
    A single search query with rationale to be used for knowledge collection.
    """
    query: Annotated[str, ..., "The search query to be used for knowledge collection."]
    rationale: Annotated[str, ..., "The rationale for why this search query was generated."]


class UserQueryAnalyzerState(TypedDict):
    """State returned by the user query analyzer node.
    """
    answer: Optional[Annotated[str, ..., "The answer to the user's query. If the query is simple and can be answered directly, provide the answer here."]]
    follow_up_questions: Optional[Annotated[list[str], ..., "List of follow-up questions to clarify the user's intent if the initial query is ambiguous or incomplete."]]
    user_query_interpretation: Annotated[str, ..., "Interpretation of the user's query. A concise summary of what the user is asking."]
    user_query_complexity: Annotated[int, ..., "Complexity level of the query, higher means more complex, use fibonacci scale 1-2-3-5-8-13-21 where 1 is extremely easy question to answer that doesn't require any reasoning and can be given directly in one sentence"]
    requires_web_search: Annotated[bool, ..., "Whether the query requires a web search to answer, eg. if user asks for current events (publicly known)"]
    requires_long_term_memory_access: Annotated[bool, ..., "Whether the query requires access to long-term memory to answer, eg user refers to past conversations or personal data"]

class CollectedKnowledgeState(UserQueryAnalyzerState):
    """
    State for holding collected knowledge.
    """
    knowledge_search_results: Annotated[list, operator.add, "List of results obtained from knowledge search queries."]
    memory_access_registry: Annotated[list, operator.add, "List of memory access records, including reads and writes."]

class AgentState(CollectedKnowledgeState):
    """Represents the state of the chatbot.
    Specifies what type of information will flow 
    between different nodes and edges in a graph.
    """
    messages: Annotated[list[BaseMessage], add_messages, "The list of messages exchanged so far."]
    
