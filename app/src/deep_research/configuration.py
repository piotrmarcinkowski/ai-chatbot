import os
from typing import Any, Optional
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gpt-4o-mini",
        description="The name of the language model to use for the agent's query generation.",
    )

    reflection_model: str = Field(
        default="gpt-4o-mini",
        description="The name of the language model to use for the agent's reflection.",
    )

    answer_model: str = Field(
        default="gpt-4o",
        description="The name of the language model to use for the agent's answer.",
    )

    number_of_initial_queries: int = Field(
        default=1,
        description="The number of initial search queries to generate.",
    )

    number_of_results_per_query: int = Field(
        default=1,
        description="The number of search results to retrieve per query.",
    )

    max_research_loops: int = Field(
        default=2,
        description="The maximum number of research loops to perform.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
    
    # TODO: verify how from_runnable_config works with env variables