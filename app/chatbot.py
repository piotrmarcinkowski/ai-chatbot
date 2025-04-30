from langchain.chains.question_answering import load_qa_chain

from knowledge import load_knowledge_vectors
from llm import init_llm
from llm import init_embeddings

class Chatbot:
    def __init__(self):
        print("Creating AIChatbot instance")
        self.chat_history = {}
        self.knowledge = Knowledge()
        self.llm = init_llm()
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

    def get_response(self, user_input):
        match = self.knowledge.vectors.similarity_search(user_input)
        response = self.chain.run(input_documents=match, question=user_input)
        return response

class Knowledge:
    def __init__(self):
        self.embeddings = init_embeddings()
        self.vectors = load_knowledge_vectors(self.embeddings)





