from model.llm import init_llm
from model.llm import init_embeddings
from langchain_core.messages import BaseMessage
from model.chat_history import ChatHistorySaver, ChatArchive, init_chat_history_saver, init_chat_archive, init_chat_vector_store, history_prompt
import uuid

class Chatbot:
    """
    A chatbot class that's main task is to processes user input.
    It initializes the LLM model, embeddings, and the main pipeline.
    """
    def __init__(self):
        print("Chatbot: Creating Chatbot instance")
        self.chat_session_id = None

        print("Chatbot: Initializing LLM model")
        self.llm = init_llm()

        print("Chatbot: Initializing embeddings")
        self.embeddings = init_embeddings()

        print("Chatbot: Creating pipeline")
        self.pipeline = history_prompt | self.llm

        print("Chatbot: Initializing chat history")
        self.chat_history_saver : ChatHistorySaver = init_chat_history_saver()
        self.pipeline = self.chat_history_saver.manage_chat_history(self.pipeline)

        self.chat_archive : ChatArchive = init_chat_archive()

        self.chat_vector_store = init_chat_vector_store(self.embeddings)
        # Link the chat history saver to the chat vector store so that
        # every new messages added to the chat gets immediately added
        # to the vector store
        self.chat_history_saver.add_new_message_callback(self.chat_vector_store.add_message)

        print("Chatbot: Initilization complete")

    def start_new_chat(self):
        """
        Starts a new chat session by generating a new session ID and clearing current chat history.
        """
        self.chat_session_id = str(uuid.uuid4())
        print("Chatbot.start_new_chat: Starting new chat session with ID:", self.chat_session_id)

    def process_user_input(self, user_input):
        """
        Generates a response to the user input.
        """
        config = {"configurable": {"session_id": self.chat_session_id}}
        print("Chatbot.process_user_input: Processing user input for session:", self.chat_session_id)
        return self.pipeline.invoke({"user_input": user_input}, config=config)
    
    def get_current_chat_messages(self):
        """
        Retrieves the messages for the current chat session.
        """
        print("Chatbot.get_current_chat_messages: Chat messages requested for session:", self.chat_session_id)
        return self.chat_archive.get_chat_messages(self.chat_session_id)
    
    def refresh_vector_store(self):
        """
        Refreshes the chat vector store by re-indexing all messages.
        """
        print("Chatbot.refresh_vector_store: Refreshing")
        self.chat_vector_store.refresh(self.chat_archive)
        print("Chatbot.refresh_vector_store: Refresh complete")
    
    def search_memory_for_context(self, query, top_k=5) -> list[BaseMessage]:
        """
        Searches the chat vector store for relevant context to the input query.
        Returns the top_k most relevant messages.
        """
        print(f"Chatbot.search_memory_for_context: Searching memory for query: '{query}'")
        return self.chat_vector_store.search_messages(query, limit=top_k)

