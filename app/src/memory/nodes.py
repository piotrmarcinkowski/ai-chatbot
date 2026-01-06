import uuid
import json
from datetime import datetime
from functools import lru_cache
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from memory.state import MemoryState, MemoryAccessQueriesState
from memory.prompts import generate_memory_queries_prompt, analyze_memory_results_prompt
from memory.schema import MemoryAccessQueriesResult

@lru_cache(maxsize=4)
def _get_model(model_name: str, temperature: float = 0.0) -> BaseChatModel:
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

    return model

def node_generate_memory_access_queries(state: MemoryState, config: RunnableConfig) -> MemoryAccessQueriesState:
    """LangGraph node that generates memory queries based on the given user input.

    Uses LLM model to create both, read and write queries, to interact with long-term memory.
    """
        
    datetime_now = datetime.now().isoformat()
    messages = state["messages"]
    system_prompt = generate_memory_queries_prompt.format(
        current_date_and_time=datetime_now,
    )
    messages = [system_prompt] + messages
    model_name = config.get('configurable', {}).get("model_name", "openai")
    llm = _get_model(model_name, temperature=0.5)
    structured_llm = llm.with_structured_output(MemoryAccessQueriesResult)

    result = structured_llm.invoke(messages)
    result_queries = [query.dict() for query in result.memory_access_queries]
    return {
        "memory_access_queries": result_queries
    }

def determine_namespace(query: dict, config: RunnableConfig) -> tuple:
    """
    Determines the namespace for the memory access based on the query details.
    The namespace that will be picked is heavily dependent on the user. 
    The function first checks if the user is specified in the query,
    otherwise it falls back to the config. If neither is provided, it uses 'default_user'.
    """
    user = query.get("user") or config.get('configurable', {}).get("user")
    if not user:
        print("Warning: No user specified in neither query nor config, using 'default_user'")
        user = "default_user"

    default_memory_type="facts"
    memory_type = query.get("memory_type", default_memory_type)
    # convert user and memory_type to lowercase strings to avoid issues with case sensitivity
    user = str(user).lower()
    memory_type = str(memory_type).lower()
    namespace = (user, memory_type)
    return namespace

def read_memory(query: dict, store: BaseStore, config: RunnableConfig) -> dict:
    """
    Reads from memory based on the given query.
    """
    assert query.get("access_type") == "read", "Query type must be 'read' for reading memory."

    read_query = query.get("query")
    namespace = determine_namespace(query, config)

    memories = store.search(
        namespace,
        query=read_query,
        limit=100,
    )
    memories_dicts = [ item.dict() for item in memories ]
    return {
        "namespace": namespace,
        "memories": memories_dicts
    }

def write_memory(query: dict, store: BaseStore, config: RunnableConfig) -> dict:
    """
    Writes to memory based on the given query.
    """
    assert query.get("access_type") == "write", "Query type must be 'write' for writing memory."

    memory_id = str(uuid.uuid4())
    memory = query.get("query")
    namespace = determine_namespace(query, config)
    # TODO: Extend memory with metadata such as timestamp, context, conversation reference, etc.
    store.put(namespace, memory_id, memory)
    return {
        "namespace": namespace,
        "stored_memory_id": memory_id,
    }

def node_access_memory(state: MemoryAccessQueriesState, config: RunnableConfig, *, store: BaseStore) -> MemoryState:
    """
    Node to access memory based on the generated memory queries (read and write).
    """
    memory_access_queries = state.get("memory_access_queries", [])
    results = []
    for query in memory_access_queries:
        if query.get("access_type") == "read":
            read_result = read_memory(query, store, config)
            results.append(
                {
                    "query": query,
                    "read_result": read_result,
                }
            )
        if query.get("access_type") == "write":
            write_result = write_memory(query, store, config)
            results.append(
                {
                    "query": query,
                    "write_result": write_result,
                }
            )   

    return {
        "memory_access_registry": results,
    }

def node_analyze_results(state: MemoryState, config: RunnableConfig) -> MemoryState:
    """
    Analyzes the results from memory access and prepares the response.
    """
    
    datetime_now = datetime.now().isoformat()
    messages = state["messages"]

    system_prompt = analyze_memory_results_prompt.format(
        current_date_and_time=datetime_now,
        memory_access_registry="\n\n---\n\n".join(json.dumps(item) for item in state.get("memory_access_registry", [])),
    )

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    model_name = config.get('configurable', {}).get("model_name", "openai")
    model = _get_model(model_name)
    result = model.invoke(messages)
    return {"messages": [AIMessage(content=result.content)]}
