from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Represents the state of the chatbot.
    Specifies what type of information will flow 
    between different nodes and edges in a graph.
    """

    messages: Annotated[list[BaseMessage], add_messages]
