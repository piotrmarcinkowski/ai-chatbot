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
        self.chat_history = {}

    def manage_chat_history(self, pipeline):
        """
        Enables chat history management for the given pipeline. Returns a new pipeline
        that wraps the original pipeline.
        """
        return RunnableWithMessageHistory(
            pipeline,
            lambda session_id: MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=config.get("mongodb_connection_string"),
                database_name=config.get("mongodb_chat_history_db_name"),
                collection_name=config.get("mongodb_chat_history_collection_name"),
            ),
            input_messages_key="user_input",
            history_messages_key="history",
        )
   
