from typing import List
from pydantic import BaseModel, Field


class WebResearchQuery(BaseModel):
    """
    A single web research query with rationale.
    """
    query: str
    rationale: str

class WebResearchInput(BaseModel):
    """
    Model representing a list of search queries for web research.
    """
    user_query: str = Field(
        description="The original query from the user that needs to be answered."
    )
    web_research_queries: List[WebResearchQuery] = Field(
        description="A list of web research queries to be sent to a web search engine."
    )

class Reflection(BaseModel):
    """
    Model reflection on the provided summaries about a research topic.
    """
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: List[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )


