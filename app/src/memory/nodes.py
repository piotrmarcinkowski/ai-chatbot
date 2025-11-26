import uuid
from datetime import datetime
from functools import lru_cache
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from memory.state import MemoryState, MemoryAccessQueriesState, MemoryReadResultsState
from memory.prompts import generate_memory_queries_prompt
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
    return {
        "memory_access_queries": result.memory_access_queries,
    }

def determine_namespace(query: dict) -> tuple:
    namespace = (query.user, query.memory_type)
    return namespace

def read_memory(query: dict, store: BaseStore) -> list:
    """
    Reads from memory based on the given query.
    """
    assert query.access_type == "read", "Query type must be 'read' for reading memory."

    read_query = query.query
    namespace = determine_namespace(query)

    memories = store.search(
        namespace=namespace,
        query=read_query,
        limit=10,
    )
    return memories

def write_memory(query: dict, store: BaseStore):
    """
    Writes to memory based on the given query.
    """
    assert query.access_type == "write", "Query type must be 'write' for writing memory."

    memory_id = str(uuid.uuid4())
    memory = query.query
    namespace = determine_namespace(query)
    # TODO: Extend memory with metadata such as timestamp, context, conversation reference, etc.
    store.put(namespace, memory_id, memory)
    

def node_access_memory(state: MemoryAccessQueriesState, store: BaseStore) -> MemoryReadResultsState:
    """
    Node to access memory based on the generated memory queries (read and write).
    """
    memory_access_queries = state.get("memory_access_queries", [])
    read_results = []
    for query in memory_access_queries:
        if query.access_type == "read":
            result = read_memory(query, store)
            read_results.append(result)
        if query.access_type == "write":
            write_memory(query, store)

    return {
        "memory_read_results": read_results,
    }