from llm import init_llm
from llm import init_embeddings
from chat_history import ChatHistory
from chat_history import history_prompt
import uuid

class Chatbot:
    def __init__(self):
        print("===Creating AIChatbot instance===")
        self.chat_session_id = None

        print("===Initializing LLM model===")
        self.llm = init_llm()

        print("===Initializing embeddings===")
        self.embeddings = init_embeddings()

        print("===Creating pipeline===")
        self.pipeline = history_prompt | self.llm

        print("Initializing memory subsystem")
        self.memory = ChatHistory()
        self.pipeline = self.memory.manage_chat_history(self.pipeline)

        print("===Chatbot initialized===")

    def start_new_chat(self):
        """
        Starts a new chat session by generating a new session ID and clearing current chat history.
        """
        self.chat_session_id = str(uuid.uuid4())
        print("Starting new chat session with ID:", self.chat_session_id)

    def process_user_input(self, user_input):
        """
        Generates a response to the user input.
        """
        config = {"configurable": {"session_id": self.chat_session_id}}
        return self.pipeline.invoke({"user_input": user_input}, config=config)
    
    def get_chat_history(self):
        """
        Retrieves the chat history for the current session.
        """
        return self.memory.get_chat_history(self.chat_session_id)

