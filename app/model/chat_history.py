from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config
from pymongo import MongoClient
import time
from langchain_core.messages import BaseMessage
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings  # Add this import
from langchain_core.chat_history import BaseChatMessageHistory  # Add this import

# TODO: Make this a structured prompt with bool result indicating if LLM knew the answer
history_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Use the following pieces of chat history to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}"),
    ]
)

_new_message_callbacks = []
_history_cache : dict[str, BaseChatMessageHistory] = {}



def _call_new_message_callbacks(message):
    """
    Calls all registered new message callbacks with the given message.
    :param message: The message to be passed to the callbacks.
    """
    print("_call_new_message_callbacks: Calling new message callbacks for message:", message)
    for callback in _new_message_callbacks:
        print(f"_call_new_message_callbacks: Calling callback {callback} with message {message}")
        callback(message)

class CustomMongoDBChatMessageHistory(MongoDBChatMessageHistory):
    """
    MongoDBChatMessageHistory with customized message handling function what allows 
    intercepting messages that are being passed to storage. 
    Just before the message is stored, it can be modified or logged.
    """
    def __init__(self, new_message_callback, session_id, *args, **kwargs):
        print(f"CustomMongoDBChatMessageHistory: Initializing with session_id: {session_id}")
        super().__init__(session_id=session_id, *args, **kwargs)
        self.new_message_callback = new_message_callback

    def add_message(self, message: BaseMessage) -> None:
        """Append metadata to the message and store it in the database."""
        message.additional_kwargs = {
            "timestamp": int(time.time() * 1000),  # Store timestamp in milliseconds
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # ISO 8601 UTC format
        }
        self.new_message_callback(message)  # notify about the new message
        super().add_message(message)

def _provide_history_instance(session_id):
    """
    Returns a MongoDBChatMessageHistory instance for the given session ID.
    """
    history_instance = _history_cache.get(session_id)
    if history_instance is None:
        print(f"_provide_history_instance: Creating MongoDBChatMessageHistory instance for session_id: {session_id}")
        history_instance = CustomMongoDBChatMessageHistory(
            new_message_callback=_call_new_message_callbacks,
            session_id=session_id,
            connection_string=config.get("mongodb_connection_string"),
            database_name=config.get("mongodb_chat_history_db_name"),
            collection_name=config.get("mongodb_chat_history_collection_name"),
        )
        _history_cache[session_id] = history_instance
    print(f"_provide_history_instance: Returning history instance for session_id: {session_id}")
    return history_instance

class ChatHistorySaver:
    """
    Saves chat history for the provided pipeline.
    """

    def __init__(self):
        """
        Initializes the memory subsystem with the given LLM.
        """
        self.new_message_callbacks = []

    def manage_chat_history(self, pipeline) -> RunnableWithMessageHistory:
        """
        Enables chat history management for the given pipeline. 
        :param pipeline: The original pipeline to be wrapped.
        :return: A new pipeline that wraps the original pipeline and manages chat history.
        """
        print("ChatHistory.manage_chat_history: creating RunnableWithMessageHistory")
        return RunnableWithMessageHistory(
            pipeline,
            _provide_history_instance,
            input_messages_key="user_input",
            history_messages_key="chat_history",
        )
    
    def add_new_message_callback(self, callback):
        """
        Adds a new message callback to be called when a new message is added.
        :param callback: A function that takes a BaseMessage as an argument.
        """
        print("ChatHistorySaver.add_new_message_callback: Adding new message callback: ", callback)
        _new_message_callbacks.append(callback)

def init_chat_history_saver() -> ChatHistorySaver:
    """
    Initializes the chat history subsystem.
    This function should be called once at the start of the application.
    """
    print("init_chat_history_saver: Creating ChatHistorySaver instance")
    return ChatHistorySaver()

class ChatArchive:
    """
    Manages the chat archive, allowing retrieval of archived chat sessions.
    """
    def get_archived_session_ids(self, limit=None):
        """
        Retrieves a list of archived chat sessions.
        :param limit: Optional limit on the number of sessions to return. Most recent sessions are returned first.
        :return: A list of IDs of the archived chat sessions.
        """
        print("ChatArchive.get_archived_session_ids: Retrieving archived chat sessions")
        
        connection_string = config.get("mongodb_connection_string")
        database_name = config.get("mongodb_chat_history_db_name")
        collection_name = config.get("mongodb_chat_history_collection_name")

        print(f"ChatArchive.get_archived_session_ids: Retrieving archived sessions from MongoDB at {connection_string}, database: {database_name}, collection: {collection_name}")
        start_time = time.time()
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]

        # Retrieve all unique SessionId values
        # Aggregate to get the first message for each unique SessionId
        pipeline = [
            {"$sort": {"_id": 1}},  # Ensure earliest message comes first
            {
            "$group": {
                "_id": "$SessionId",
                "first_message": {"$first": "$History"},
            }
            },
            {"$sort": {"_id": -1}},  # Most recent sessions first by SessionId (UUIDs are sortable)
        ]
        results = list(collection.aggregate(pipeline))
        session_infos = [
            {"session_id": doc["_id"], "first_message": doc["first_message"]}
            for doc in results
        ]
        chat_sessions = session_infos
        elapsed_time = time.time() - start_time
        print(f"ChatArchive.get_archived_session_ids: Database retrieval took {elapsed_time:.4f} seconds")
        print(f"ChatArchive.get_archived_session_ids: Found {len(chat_sessions)} archived sessions")

        if limit is not None:
            chat_sessions = chat_sessions[:limit]
        print(f"ChatArchive.get_archived_session_ids: Returning {len(chat_sessions)} archived sessions")
        return chat_sessions
   
    def get_chat_messages(self, session_id):
        """
        Retrieves the chat history for the given session ID.
        If no history is found, returns an empty list.
        :param session_id: The session ID for which to retrieve chat history.
        :return: A list of chat messages for the given session ID.
        """
        print(f"ChatArchive.get_chat_messages: Retrieving chat history for session_id: {session_id}")
        if session_id not in _history_cache:
            print(f"ChatArchive.get_chat_messages: No chat history found for session_id: {session_id}")
            return []
        return _history_cache[session_id].messages
    
def init_chat_archive() -> ChatArchive:
    return ChatArchive()

class ChatVectorStore:
    def __init__(self, embeddings=None):
        print("ChatVectorStore: Initializing with embeddings:", embeddings.model if embeddings else "None")
        self.embeddings = embeddings
        print("ChatVectorStore: Creating Chroma vector store")
        self.vector_store = Chroma(embedding_function=embeddings)

    def add_message(self, message: BaseMessage) -> None:
        """
        Adds the message to the vector store.
        This method is called when a new message is added to the chat history.
        """
        if self.embeddings is None:
            print("ChatVectorStore.add_message: No embeddings provided, skipping vector store update")
            return
        print(f"ChatVectorStore.add_message: Adding message to vector store: {message}")
        self.vector_store.add_texts([message.content])

    def search_messages(self, query: str, limit: int = 20) -> list[BaseMessage]:
        """
        Searches for messages in the vector store that are similar to the query.
        :param query: The query string to search for.
        :param limit: The maximum number of results to return.
        :return: A list of messages that match the query.
        """
        print(f"ChatVectorStore.search_messages: Searching for '{query}'")
        results = self.vector_store.similarity_search(query, k=limit)
        return results

def init_chat_vector_store(embeddings: Embeddings) -> ChatVectorStore:
    """
    Initializes the chat vector store with the given embeddings.
    :param embeddings: The embeddings to use for the vector store.
    :return: An instance of ChatVectorStore.
    """
    print("init_chat_vector_store: Creating ChatVectorStore instance with embeddings:", embeddings.model if embeddings else "None")
    return ChatVectorStore(embeddings=embeddings)