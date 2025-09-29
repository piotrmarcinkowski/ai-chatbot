from typing import List
from pydantic import BaseModel, Field


class KnowledgeSearchQueryList(BaseModel):
    """
    Model representing the state of knowledge collection.
    """
    search_query: List[str] = Field(
        description="A list of search queries to be used for knowledge collection."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries and keywords are relevant to the search query"
    )

