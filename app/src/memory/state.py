import operator
from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class MemoryState(TypedDict):
    """
    State for memory operations.
    """
    messages: Annotated[list[BaseMessage], add_messages]

    """
    State for holding memory access registry. 
    The registry holds precisely what was read from or written to long-term memory. 
    The memory access registry gets returned as graph output. 
    It can be also used as input in subsequent graph invocations. This is useful for maintaining 
    continuity in memory operations across multiple interactions within a single chat session.
    The registry caches the memory search results to avoid redundant memory accesses. 
    It also prevents the same memory entries from being written multiple times.
    """
    memory_access_registry: Annotated[list, operator.add]

    """
    Optional extra instructions to guide memory analysis.
    """
    extra_instructions: str

    """
    Identifier of the user associated with the memory operations.
    """
    user: str

    """
    Identifier of the current chat session, that can be stored as part of memory metadata, 
    to link memory entries to specific chat sessions.
    """
    current_chat_id: str

class MemoryAccessQueriesState(MemoryState):
    """
    State for generating memory access queries.
    """ 
    memory_access_queries: Annotated[list, operator.add]
    # TODO: Split this state into separate read and write query states
    #memory_read_queries: Annotated[list, operator.add]
    #memory_write_queries: Annotated[list, operator.add]