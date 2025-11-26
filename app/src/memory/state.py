import operator
from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class MemoryState(TypedDict):
    """
    State for memory operations.
    """
    messages: Annotated[list[BaseMessage], add_messages, "The list of messages exchanged so far."]

class MemoryAccessQueriesState(MemoryState):
    """
    State for generating memory access queries.
    """ 
    memory_access_queries: Annotated[list, operator.add, "List of memory access queries generated to retrieve relevant information from long-term memory."]

class MemoryReadResultsState(MemoryAccessQueriesState):
    """
    State for holding memory read results.
    """
    memory_read_results: Annotated[list, operator.add, "List of results obtained from memory read operations."]
