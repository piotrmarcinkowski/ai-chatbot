import json
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.types import Send, Command
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langsmith import traceable
from agent.tools import all_tools
from agent.state import (
    AgentState,
    ProcessQueryState,
    CollectedKnowledgeState,
)
from agent.prompts import (
    query_processing_prompt,
    final_answer_provider_prompt,
)
from agent.schema import (
    ProcessQueryResult,
)
from deep_research.graph import graph as deep_research_graph
from memory.graph import workflow as memory_graph_workflow
from utils.time import (
    local_time_zone,
    current_local_time
)
from config.config_loader import assistant_config, ASSISTANT_DEFAULT_NAME

def _get_processing_model(config: RunnableConfig) -> BaseChatModel:
    """
    Returns a language model instance for query processing.
    """
    model = ChatOpenAI(temperature=0.0, model_name="gpt-4o")
    return model

def _get_final_answer_model(config: RunnableConfig) -> BaseChatModel:
    """
    Returns a language model instance for final answer preparation.
    """
    model = ChatOpenAI(temperature=0.5, model_name="gpt-4o")
    model = model.bind_tools(all_tools)
    return model


# Define the function to execute tools
tool_node = ToolNode(all_tools)

def tool_call_exists(state: ProcessQueryState):
    """
    Checks if there are still tools to be called.
    This node is used to create a loop in the graph that continues until no more tool calls are needed.
    """
    last_message = state['messages'][-1]
    if not hasattr(last_message, 'tool_calls'):
        return False
    return len(last_message.tool_calls) > 0

def node_user_query_input(state: AgentState) -> ProcessQueryState:
    """
    Initial node to accept user query input.
    """
    user_query_message = None
    if state.get("user_query"):
        user_query = state["user_query"]
        user_query_message = HumanMessage(content=user_query)

    return {
        "messages": [user_query_message] if user_query_message else [],
        "processing_iteration": 0
    }

@traceable(run_type="llm", name="Process User Query")
def node_process_query(state: ProcessQueryState, config: RunnableConfig) -> ProcessQueryState:
    """ 
    Processes the user query, determining user name, complexity, and required actions.
    """
    processing_iteration = state.get("processing_iteration", 0) + 1
    
    system_prompt = query_processing_prompt.format(
        assistant_name = assistant_config.get("assistant_name", ASSISTANT_DEFAULT_NAME),
        current_timezone=local_time_zone(),
        current_datetime=current_local_time(),
        user=state.get("user", ""),
        memory_access_registry="\n\n---\n\n".join(json.dumps(item) for item in state.get("memory_access_registry", [])),
        collected_information="\n\n---\n\n".join(state.get("knowledge_search_results", [])),
    )
    messages = state["messages"]
    
    llm = _get_processing_model(config)
    structured_llm = llm.with_structured_output(ProcessQueryResult)

    response = structured_llm.invoke([SystemMessage(content=system_prompt)] + messages)
    print("Processing result:", response)
    return {
        "processing_iteration": processing_iteration,
        "processing_summary": response.summary,
        "processing_answer": response.answer,
        "requires_web_search": response.requires_web_search,
        "requires_long_term_memory_access": response.requires_long_term_memory_access,
        "instructions_for_web_search": response.instructions_for_web_search,
        "instructions_for_long_term_memory_access": response.instructions_for_long_term_memory_access,
        "user": response.user,
    }

def select_next_route_after_processing(state: ProcessQueryState, config: RunnableConfig) -> Literal["collect_knowledge", "finalize_answer"]:
    """
    Determines the next route after query processing based on iteration count and requirements.
    """
    processing_iteration = state.get("processing_iteration", 0)
    max_processing_iterations = config.get('configurable', {}).get("max_processing_iterations", 3)
    
    # If max iterations reached, finalize answer
    if processing_iteration >= max_processing_iterations:
        print(f"Max processing iterations ({max_processing_iterations}) reached, finalizing answer.")
        return "finalize_answer"
    
    # Check if knowledge collection is needed
    if state.get("requires_long_term_memory_access") and not state.get("user"):
        print("Warning: No user specified for long-term memory access")
    
    if state.get("requires_web_search") or (state.get("requires_long_term_memory_access") and state.get("user")):
        return "collect_knowledge"
    else:
        return "finalize_answer"

def node_route_after_processing(state: ProcessQueryState, config: RunnableConfig) -> Command[Literal["collect_knowledge", "finalize_answer"]]:
    """
    Router node that decides the next step after query processing.
    """
    print(f"Processing state - Iteration: {state.get('processing_iteration', 0)}, "
        f"User: {state.get('user', '')}, "
        f"Web search required: {state.get('requires_web_search', False)}, "
        f"Instructions for web search: {state.get('instructions_for_web_search', '')}, "
        f"Memory access required: {state.get('requires_long_term_memory_access', False)}, "
        f"Instructions for memory access: {state.get('instructions_for_long_term_memory_access', '')}, "
        f"Processing summary: {state.get('processing_summary', '')}, "
        f"Processing answer: {state.get('processing_answer', '')}, "
    )
    next_route = select_next_route_after_processing(state, config)
    print(f"Routing after processing to: {next_route}")
    return Command(goto=next_route)

def node_collect_knowledge(state: ProcessQueryState):
    """
    Initiates the knowledge collection process
    """
    return {}

def continue_to_knowledge_collection(state: ProcessQueryState) -> list[Send]:
    """
    This is used to spawn n number of knowledge collection nodes, depending on the user query analysis.
    """
    nodes_to_call = []
    if state.get("requires_web_search"):
        nodes_to_call.append("web_search")
    if state.get("requires_long_term_memory_access"):
        if not state.get("user"):
            print("Warning: No user specified for long-term memory access, skipping memory search")
        else:
            nodes_to_call.append("memory_search")
    return [
        Send(node, {"messages": state["messages"], "id": int(idx)})
        for idx, node in enumerate(nodes_to_call)
    ]

def node_web_search(state: ProcessQueryState) -> CollectedKnowledgeState:
    """ Call deep_research_graph to perform a web search.
    """
    # Prepare the input for the deep research graph
    research_input = {
        "messages": state["messages"],
    }
    
    # Pass instructions for web search if available
    if state.get("instructions_for_web_search"):
        research_input["extra_instructions"] = state["instructions_for_web_search"]
    
    response = deep_research_graph.invoke(research_input)
    ai_message = response["messages"][-1]
    return {
        "knowledge_search_results": [ai_message.content]
    }

@traceable(name="Memory Access")
def node_memory_access(state: ProcessQueryState, config: RunnableConfig, store: BaseStore) -> CollectedKnowledgeState:
    """ Call memory_graph to perform long-term memory access.
    """
    user = state.get("user") or config.get('configurable', {}).get("user", "default_user")
    config = {'configurable': {'user': user}}

    # If run via 'langgraph dev' store needs to be passed from parent graph
    # otherwise sub-graph nodes will be getting None as store parameter in its nodes.
    # Hence we import workflow from the memory graph and compile the graph
    # here with the store from the parent graph.
    memory_graph = memory_graph_workflow.compile(store=store)
    
    # Prepare the input for the memory graph
    memory_input = {
        "messages": state["messages"],
        "memory_access_registry": state.get("memory_access_registry", []),
        "user": user,
    }
    
    # Pass instructions for memory access if available
    if state.get("instructions_for_long_term_memory_access"):
        memory_input["extra_instructions"] = state["instructions_for_long_term_memory_access"]
    
    response = memory_graph.invoke(memory_input, config=config)
    memory_results = []
    last_message = response["messages"][-1]
    if last_message.type == "ai":
        memory_results = [ last_message.content ]  # Assume content contains the memory search results
    return {
        "knowledge_search_results": memory_results,
        "memory_access_registry": response.get("memory_access_registry", []),
    }

def node_knowledge_collected(state: CollectedKnowledgeState) -> CollectedKnowledgeState:
    """ Collected knowledge aggregation node.
    """
    print("Knowledge collected:", state.get("knowledge_search_results", []))
    print("Memory access registry:", state.get("memory_access_registry", []))
    return {
        "knowledge_search_results": state.get("knowledge_search_results", []),
        "memory_access_registry": state.get("memory_access_registry", []),
    }

@traceable(name="Final answer")
def node_finalize_answer(state: ProcessQueryState, config: RunnableConfig) -> ProcessQueryState:
    """
    Generates a final answer to the user's query based on the collected knowledge and conversation history.
    """
    # TODO: Is complexity of the query is high add "Let me summarize and confirm the key points before answering."
    # TODO: If complexity is very high, propose to split it into smaller sub-questions.    
    system_prompt = final_answer_provider_prompt.format(
        assistant_name = assistant_config.get("assistant_name", ASSISTANT_DEFAULT_NAME),
        user=state.get("user", ""),
        processing_summary=state.get("processing_summary", ""),
        processing_answer=state.get("processing_answer", ""),
        memory_access_registry="\n\n---\n\n".join(json.dumps(item) for item in state.get("memory_access_registry", [])),
        collected_information="\n\n---\n\n".join(state.get("knowledge_search_results", [])),
        current_timezone=local_time_zone(),
        current_datetime=current_local_time(),
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    model = _get_final_answer_model(config)
    result = model.invoke(messages)
    return {"messages": [result]}