from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config

# TODO: Make this a structured prompt with bool result indicating if LLM knew the answer
history_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Use the following pieces of history to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer."),
        MessagesPlaceholder(variable_name="history"),
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
        print("ChatHistory.__init__")
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
            history_messages_key="history",
        )
   
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
