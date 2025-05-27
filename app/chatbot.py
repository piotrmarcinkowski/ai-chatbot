from llm import init_llm
from llm import init_embeddings
from chat_history import history_prompt, chat_history
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

        print("Chatbot: Initializing memory subsystem")
        self.chat_history = chat_history
        self.pipeline = self.chat_history.manage_chat_history(self.pipeline)

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
        return self.chat_history.get_chat_history(self.chat_session_id)

