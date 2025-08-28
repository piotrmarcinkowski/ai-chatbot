from functools import lru_cache
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from agent.tools import tools
from agent.state import AgentState
from agent.prompts import create_initial_system_message

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    """
    Returns a language model instance based on the provided model name.
    Caches up to 4 different model instances.
    """
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        #model =  ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
        raise NotImplementedError("Do not use Anthropic models for now")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model

# Define the function that calls the model
def call_model(state, config):
    """
    Calls the language model with the current state and configuration.
    """
    messages = state["messages"]
    system_prompt = create_initial_system_message()
    messages = [system_prompt] + messages
    model_name = config.get('configurable', {}).get("model_name", "openai")
    model = _get_model(model_name)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define the function to execute tools
tool_node = ToolNode(tools)

def tool_call_exists(state: AgentState):
    """
    Checks if there are still tools to be called.
    This node is used to create a loop in the graph that continues until no more tool calls are needed.
    """
    result = state['messages'][-1]
    return len(result.tool_calls) > 0
