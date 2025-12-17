import operator
from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class MemoryState(TypedDict):
    """
    State for memory operations.
    """
    messages: Annotated[list[BaseMessage], add_messages, "The list of messages exchanged so far."]

    """
    State for holding memory access registry. 
    The registry holds precisely what was read from or written to long-term memory. 
    The memory access registry gets returned as graph output. 
    It can be also used as input in subsequent graph invocations. This is useful for maintaining 
    continuity in memory operations across multiple interactions within a single chat session.
    The registry caches the memory search results to avoid redundant memory accesses. 
    It also prevents the same memory entries from being written multiple times.
    """
    memory_access_registry: Annotated[list, operator.add, "List of results from memory access operations (reads and writes)."]

class MemoryAccessQueriesState(MemoryState):
    """
    State for generating memory access queries.
    """ 
    memory_access_queries: Annotated[list, operator.add, "List of memory access queries generated to retrieve relevant information from long-term memory."]    