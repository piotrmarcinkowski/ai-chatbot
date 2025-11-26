from typing import List, Literal
from pydantic import BaseModel, Field


class MemoryAccessQuery(BaseModel):
    """
    A single memory access query.
    """
    query: str = Field(
        description="The memory access query to be used for retrieving or storing information.",
        examples=["User's favorite color", "Vacation 2025 details", "Procedure for resetting door password", "Meeting notes from last week"],
    )
    memory_type: Literal["facts", "events", "preferences"] = Field(
        description="The type of memory to access.",
    )
    #TODO: add memory context, conversation reference, circumstances when this memory was created
    access_type: Literal["read", "write"] = Field(
        description="The type of access operation to perform.",
    )
    user: str = Field(
        default="default_user",
        description="The user associated with the memory access, if determined from context.",
    )
    #TODO: store rationale with the memory access query for explainability
    rationale: str = Field(
        description="Rationale for the memory access operation.",
    )

class MemoryAccessQueriesResult(BaseModel):
    """
    Result containing a list of memory access queries.
    """
    memory_access_queries: List[MemoryAccessQuery] = Field(
        description="List of generated memory access queries.",
    )