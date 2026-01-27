from typing import List
from langchain_core.messages import AnyMessage

def chat_to_str(messages: List[AnyMessage]) -> str:
    """
    Converts a list of chat messages to a single string.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        result_str = messages[-1].get("content", "")
    else:
        result_str = ""
        for message in messages:
            if (message.get("role") == "user" or message.get("type") == "human"):
                result_str += f"User: {message.get("content", "")}\n"
            elif (message.get("role") == "assistant" or message.get("type") == "ai"):
                result_str += f"Assistant: {message.get("content", "")}\n"
            else:
                raise ValueError(f"Unknown message type: {message}")
    return result_str
