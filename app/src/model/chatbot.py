from langchain_core.messages import HumanMessage, BaseMessage
from model.llm import init_llm
from model.llm import init_embeddings
from model.tools import init_tools
from model.chat_history import ChatArchive, init_chat_archive, init_chat_vector_store
from model.prompts import system_prompt
from model.graph import init_state_graph
import uuid

class Chatbot:
    """
    A chatbot class that's main task is to processes user input.
    It initializes the LLM model, embeddings, and the main pipeline.
    """
    def __init__(self):
        print("Chatbot: Creating Chatbot instance")
        self.chat_session_id = None

        print("Chatbot: Initializing tools")
        tools = init_tools(self)

        print("Chatbot: Initializing LLM model")
        self.llm = init_llm().bind_tools(tools)

        print("Chatbot: Initializing embeddings")
        self.embeddings = init_embeddings()

        print("Chatbot: Initializing chat archive")
        self.chat_archive : ChatArchive = init_chat_archive()
        checkpointer = self.chat_archive.get_checkpointer()

        print("Chatbot: Creating agent graph")
        self.graph = init_state_graph(self.llm, tools)
        
        # TODO: [research]Rework vector store implementation to be compatible with builder.compile to pass it as store parameter
        self.chat_vector_store = init_chat_vector_store(self.embeddings)
                
        # Link the chat history saver to the chat vector store so that
        # every new messages added to the chat gets immediately added
        # to the vector store
        # TODO: Rework this: add agent graph with the node that saves messages to the vector store
        #self.chat_history_saver.add_new_message_callback(self.chat_vector_store.add_message)

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
        config = {"configurable": {
            "thread_id": self.chat_session_id,
            "assistant_name": "Jarvis",
            }}
        print("Chatbot.process_user_input: Processing user input for session:", self.chat_session_id)
        messages = [HumanMessage(content=user_input)]
        result = self.graph.invoke({"messages": messages})
        return result
 
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
    
    