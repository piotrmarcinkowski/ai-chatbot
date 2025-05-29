from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config
from pymongo import MongoClient
import time
from langchain_core.messages import BaseMessage

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
    
    def get_archived_chat_session_list(self, limit=None):
        """
        Retrieves a list of archived chat sessions.
        :param limit: Optional limit on the number of sessions to return. Most recent sessions are returned first.
        :return: A list of archived chat sessions.
        """
        print("ChatHistory.get_archived_chat_session_list: Retrieving archived chat sessions")
        
        connection_string = config.get("mongodb_connection_string")
        database_name = config.get("mongodb_chat_history_db_name")
        collection_name = config.get("mongodb_chat_history_collection_name")

        print(f"ChatHistory.get_archived_chat_session_list: Retrieving archived sessions from MongoDB at {connection_string}, database: {database_name}, collection: {collection_name}")
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
        print(f"ChatHistory.get_archived_chat_session_list: Database retrieval took {elapsed_time:.4f} seconds")
        print(f"ChatHistory.get_archived_chat_session_list: Found {len(chat_sessions)} archived sessions")

        if limit is not None:
            chat_sessions = chat_sessions[:limit]
        print(f"ChatHistory.get_archived_chat_session_list: Returning {len(chat_sessions)} archived sessions")
        return chat_sessions
   
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

class CustomMongoDBChatMessageHistory(MongoDBChatMessageHistory):
    """
    MongoDBChatMessageHistory with customized message handling function what allows 
    intercepting messages that are being passed to storage. 
    Just before the message is stored, it can be modified or logged.
    """
    def __init__(self, session_id, *args, **kwargs):
        print(f"CustomMongoDBChatMessageHistory: Initializing with session_id: {session_id}")
        super().__init__(session_id=session_id, *args, **kwargs)

    def add_message(self, message: BaseMessage) -> None:
        """Append metadata to the message and store it in the database."""
        message.additional_kwargs = {
            "timestamp": int(time.time() * 1000),  # Store timestamp in milliseconds
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # ISO 8601 UTC format
        }
        super().add_message(message)

def _provide_history_instance(session_id):
    """
    Returns a MongoDBChatMessageHistory instance for the given session ID.
    """
    history_instance = chat_history.history_cache.get(session_id)
    if history_instance is None:
        print(f"_provide_history_instance: Creating MongoDBChatMessageHistory instance for session_id: {session_id}")
        history_instance = CustomMongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=config.get("mongodb_connection_string"),
            database_name=config.get("mongodb_chat_history_db_name"),
            collection_name=config.get("mongodb_chat_history_collection_name"),
        )
        chat_history.history_cache[session_id] = history_instance
    print(f"_provide_history_instance: Returning history instance for session_id: {session_id}")
    return history_instance
