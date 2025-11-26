from functools import lru_cache
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from agent.tools import tools
from agent.state import (
    AgentState, 
    UserQueryAnalyzerState, 
    CollectedKnowledgeState
)
from agent.prompts import (
    create_initial_system_message,
    query_analyzer_prompt,
    answer_provider_prompt,
)
from deep_research.graph import graph as deep_research_graph
from memory.graph import graph as memory_graph

@lru_cache(maxsize=4)
def _get_model(model_name: str, temperature: float = 0) -> BaseChatModel:
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
    system_prompt = query_analyzer_prompt.format(
        collected_information="\n\n---\n\n".join(state.get("knowledge_search_results", [])),
    )
    messages = state["messages"]

    model_name = config.get('configurable', {}).get("model_name", "openai")

    llm = _get_model(model_name)
    structured_llm = llm.with_structured_output(UserQueryAnalyzerState)

    response = structured_llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return response

def node_collect_knowledge(state: AgentState):
    """
    Initiates the knowledge collection process
    """
    return {}

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
        Send(node, {"messages": state["messages"], "id": int(idx)})
        for idx, node in enumerate(nodes_to_call)
    ]

def node_web_search(state: AgentState) -> CollectedKnowledgeState:
    """ Call deep_research_graph to perform a web search.
    """
    response = deep_research_graph.invoke(
        {
            "messages": state["messages"],
        }
    )
    ai_message = response["messages"][-1]
    return {
        "knowledge_search_results": [ai_message.content]
    }

def node_memory_search(state: AgentState):
    """ Placeholder for memory search node.
    """
    response = memory_graph.invoke(
        {
            "messages": state["messages"],
        }
    )
    ai_message = response["messages"][-1]
    return {
        "knowledge_search_results": [ai_message.content]
    }

def node_knowledge_collected(state: AgentState):
    """ Placeholder for knowledge collected node.
    """
    return {}

def node_route_query(state: AgentState):
    """ Continues to the query router node.
    """
    return {}

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
        return "final_answer"

def node_finalize_answer(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Generates a final answer to the user's query based on the collected knowledge and conversation history.
    """
    # TODO: Is complexity of the query is high add "Let me summarize and confirm the key points before answering."
    # TODO: If complexity is very high, propose to split it into smaller sub-questions.
    # TODO: if answer is already provided in state, use it directly. 
    system_prompt = answer_provider_prompt.format(
        user_query_interpretation=state["user_query_interpretation"],
        collected_information="\n\n---\n\n".join(state.get("knowledge_search_results", [])),
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    model_name = config.get('configurable', {}).get("model_name", "openai")
    model = _get_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}