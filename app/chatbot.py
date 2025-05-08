from llm import init_llm
from llm import init_embeddings
from chat_history import ChatHistory
from chat_history import history_prompt

class Chatbot:
    def __init__(self):
        print("===Creating AIChatbot instance===")
        self.chat_history = {}

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

    def get_response(self, user_input):
        """
        Generates a response to the user input using the LLM and stored chat history.
        """
        config = {"configurable": {"session_id": "test_session_id"}}
        return self.pipeline.invoke({"user_input": user_input}, config=config)

