from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph
from model.llm import init_llm
from model.llm import init_embeddings
from model.tools import init_tools
from model.chat_history import ChatArchive, init_chat_archive, init_chat_vector_store
from model.graph import init_state_graph
from model.utils import get_current_time, get_current_timestamp
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
        self.graph : StateGraph = init_state_graph(llm=self.llm, tools=tools, checkpointer=checkpointer)
        
        # TODO: [research]Rework vector store implementation to be compatible with builder.compile to pass it as store parameter
        # self.chat_vector_store = init_chat_vector_store(self.embeddings)
                
        # Link the chat history saver to the chat vector store so that
        # every new messages added to the chat gets immediately added
        # to the vector store
        # TODO: Rework this: add agent graph with the node that saves messages to the vector store
        #self.chat_history_saver.add_new_message_callback(self.chat_vector_store.add_message)

        print("Chatbot: Initilization complete")

    def new_chat(self):
        """
        Starts a new chat session by generating a new session ID and clearing current chat history.
        """
        self.chat_session_id = str(uuid.uuid4())
        print("Chatbot.start_new_chat: Starting new chat session with ID:", self.chat_session_id)

    def load_chat(self, session_id):
        """
        Loads an existing chat session by its session ID.
        """
        print(f"Chatbot.load_chat: Loading chat session with ID: {session_id}")
        self.chat_session_id = session_id

    def create_user_message(self, content: str) -> HumanMessage:
        """
        Creates a new human message for the current chat session.
        """
        metadata = {"timestamp": get_current_timestamp(), "time": get_current_time()}
        message = HumanMessage(content=content, additional_kwargs=metadata)
        print(f"Chatbot.create_user_message: Created user message for session {self.chat_session_id}: {message}")
        return message

    def process_user_message(self, user_input: HumanMessage) -> list[BaseMessage]:
        """
        Returns the AI response to a human message. The response is a list of AIMessage and ToolMessage instances.
        """
        print(f"Chatbot.process_user_input: Processing user input for session {self.chat_session_id}: {user_input}")
        config={"configurable": {"thread_id": self.chat_session_id}}
        response = self.graph.invoke({"messages": [user_input]}, config)

        # Get the last AI messages from the response (tool calls are also included)
        last_ai_messages = []
        for message in reversed(response['messages']):
            if message.type == "ai" or message.type == "tool":
                print(f"< AI: {message.content}")
                #print(f"< AI response details: {message}")
                last_ai_messages.insert(0, message)
            else:
                break

        return last_ai_messages
    
    def process_user_message_stream(self, user_input: HumanMessage):
        """
        Processes user input and returns a generator that yields AI responses.
        This is useful for streaming responses in the UI.
        """
        print(f"Chatbot.process_user_message_stream: Processing user input for session {self.chat_session_id}: {user_input}")
        config = {"configurable": {"thread_id": self.chat_session_id}}
        stream = self.graph.stream({"messages": [user_input]}, config, stream_mode= "values")
        return stream

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
        #TODO: Restore vector store refresh logic after migration to LangGraph
        #self.chat_vector_store.refresh(self.chat_archive)
        print("Chatbot.refresh_vector_store: Refresh complete")
    
    def search_memory_for_context(self, query, top_k=5) -> list[BaseMessage]:
        """
        Searches the chat vector store for relevant context to the input query.
        Returns the top_k most relevant messages.
        """
        print(f"Chatbot.search_memory_for_context: Searching memory for query: '{query}'")
        return []
        #TODO: Restore vector store search logic after migration to LangGraph
        #return self.chat_vector_store.search_messages(query, limit=top_k)
    
    