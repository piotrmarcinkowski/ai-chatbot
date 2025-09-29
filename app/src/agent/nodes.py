from functools import lru_cache
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from agent.tools import tools
from agent.state import AgentState, UserQueryAnalyzerState, KnowledgeSearchQueryGenerationState
from agent.schema import KnowledgeSearchQueryList
from agent.prompts import create_initial_system_message, query_analyzer_prompt, knowledge_search_query_generator_instructions
from utils.time import current_local_time, local_time_zone

@lru_cache(maxsize=4)
def _get_model(model_name: str, temperature: float = 0) -> ChatOpenAI:
    """
    Returns a language model instance based on the provided model name.
    Caches up to 4 different model instances.
    """
    if model_name == "openai":
        model = ChatOpenAI(temperature=temperature, model_name="gpt-4o")
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
    last_message = state['messages'][-1]
    if not hasattr(last_message, 'tool_calls'):
        return False
    return len(last_message.tool_calls) > 0

def node_analyze_user_query(state: AgentState, config: RunnableConfig) -> UserQueryAnalyzerState:
    """
    Analyzes the user's query to determine its complexity and whether it requires web search or long-term memory access.
    """
    system_prompt = query_analyzer_prompt
    messages = state["messages"]

    model_name = config.get('configurable', {}).get("model_name", "openai")

    llm = _get_model(model_name)
    structured_llm = llm.with_structured_output(UserQueryAnalyzerState)

    response = structured_llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return response

def node_generate_knowledge_search_query(state: AgentState, config: RunnableConfig) -> KnowledgeSearchQueryGenerationState:
    """
    Generates knowledge search queries based on the user's query analysis.
    """
    model_name = config.get('configurable', {}).get("model_name", "openai")
    llm = _get_model(model_name, temperature=1.0)

    structured_llm = llm.with_structured_output(KnowledgeSearchQueryList)

    formatted_prompt = knowledge_search_query_generator_instructions.format(
        current_time_and_date=current_local_time(),
        current_time_zone=local_time_zone(),
        user_query=state["user_query_interpretation"],
        num_of_queries_to_generate=1 if state["user_query_complexity"] < 5 else 2,
    )
    result = structured_llm.invoke(formatted_prompt)
    return {"knowledge_search_query": result.search_query}

def continue_to_knowledge_collection(state: AgentState) -> list[Send]:
    """
    This is used to spawn n number of knowledge collection nodes, depending on the user query analysis.
    """
    nodes_to_call = []
    if state["requires_web_search"]:
        nodes_to_call.append("web_search")
    if state["requires_long_term_memory_access"]:
        nodes_to_call.append("memory_search")
    return [
        Send(node, {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["knowledge_search_query"])
        for node in nodes_to_call
    ]

def node_web_search(state: AgentState) -> AgentState:
    """ Placeholder for web search node.
    """
    return state

def node_memory_search(state: AgentState) -> AgentState:
    """ Placeholder for memory search node.
    """
    return state

def node_knowledge_collected(state: AgentState) -> AgentState:
    """ Placeholder for knowledge collected node.
    """
    return state

# TODO: Remove this node and directly connect to the query router
def node_continue_to_query_router(state: AgentState) -> AgentState:
    """ Continues to the query router node.
    """
    return state

def select_route(state: AgentState) -> Literal["knowledge_collection", "END"]:
    """
    Routes the user's query to the appropriate processing path based on its complexity and requirements.
    """
    needs_knowledge = (
        state["requires_web_search"] or state["requires_long_term_memory_access"]
    )

    if needs_knowledge:
        return "knowledge_collection"
    else:
        return "END"