from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config
from pymongo import MongoClient
import time

# TODO: Make this a structured prompt with bool result indicating if LLM knew the answer
history_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Use the following pieces of chat history to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}"),
    ]
)

class ChatHistory:
    """
    Manages chat history, archives all messages and provides a way to quickly access 
    stored knowledge.
    It main usage is to provide a context for the LLM to generate more relevant responses.
    """

    def __init__(self):
        """
        Initializes the memory subsystem with the given LLM.
        """
        self.history_cache = {}

    def manage_chat_history(self, pipeline):
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
    
    def get_chat_session_ids(self, limit=None):
        """
        Retrieves a list of chat session IDs stored in the history.
        :param limit: Optional limit on the number of session IDs to return. Most recent sessions are returned first.
        :return: A list of chat session IDs.
        """
        print("ChatHistory.get_chat_session_ids: Retrieving chat session IDs")
        
        connection_string = config.get("mongodb_connection_string")
        database_name = config.get("mongodb_chat_history_db_name")
        collection_name = config.get("mongodb_chat_history_collection_name")

        print(f"ChatHistory.get_chat_session_ids: Retrieving session IDs from MongoDB at {connection_string}, database: {database_name}, collection: {collection_name}")
        start_time = time.time()
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]

        # Retrieve all unique SessionId values
        session_ids = list(
            collection.distinct("SessionId")
        )
        elapsed_time = time.time() - start_time
        print(f"ChatHistory.get_chat_session_ids: Database retrieval took {elapsed_time:.4f} seconds")
        print(f"ChatHistory.get_chat_session_ids: Found {len(session_ids)} session IDs")

        if limit is not None:
            session_ids = session_ids[:limit]
        print(f"ChatHistory.get_chat_session_ids: Returning {len(session_ids)} session IDs")
        return session_ids
   
    def get_chat_history(self, session_id):
        """
        Retrieves the chat history for the given session ID.
        If no history is found, returns an empty list.
        :param session_id: The session ID for which to retrieve chat history.
        :return: A list of chat messages for the given session ID.
        """
        print(f"ChatHistory.get_chat_history: Retrieving chat history for session_id: {session_id}")
        if session_id not in self.history_cache:
            print(f"ChatHistory.get_chat_history: No chat history found for session_id: {session_id}")
            return []
        return self.history_cache[session_id].messages
   
chat_history = ChatHistory()

def _provide_history_instance(session_id):
    """
    Returns a MongoDBChatMessageHistory instance for the given session ID.
    """
    history_instance = chat_history.history_cache.get(session_id)
    if history_instance is None:
        print(f"_provide_history_instance: Creating MongoDBChatMessageHistory instance for session_id: {session_id}")
        history_instance = MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=config.get("mongodb_connection_string"),
            database_name=config.get("mongodb_chat_history_db_name"),
            collection_name=config.get("mongodb_chat_history_collection_name"),
        )
        chat_history.history_cache[session_id] = history_instance
    print(f"_provide_history_instance: Returning history instance for session_id: {session_id}")
    return history_instance
