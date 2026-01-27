from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ProcessQueryResult(BaseModel):
    """
    Result of query processing containing analysis and decisions.
    """
    summary: str = Field(
        description="A concise summary of the query processing, user query interpretation, and decisions made.",
    )
    answer: str = Field(
        description="The answer to the user's query.",
    )
    requires_web_search: bool = Field(
        description="Whether the query requires a web search to answer, eg. if user asks for current events (publicly known)",
    )
    requires_long_term_memory_access: bool = Field(
        description="Whether the query requires access to long-term memory to answer, eg user refers to past conversations or personal data. This should ONLY be set to true if the user name is already known. If memory access is needed but user name is unknown, ask for the user name first instead.",
    )
    instructions_for_web_search: Optional[str] = Field(
        default=None,
        description="If requires_web_search is true, provide specific instructions or search queries for the web search agent. Otherwise leave empty.",
    )
    instructions_for_long_term_memory_access: Optional[str] = Field(
        default=None,
        description="If requires_long_term_memory_access is true, provide specific instructions for what to look for in long-term memory. Otherwise leave empty.",
    )
    user: str = Field(
        description="The user name determined during the query processing.",
    )
