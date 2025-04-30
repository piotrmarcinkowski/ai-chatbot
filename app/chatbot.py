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
        # load_qa_chain is designed for question-answering tasks over a list of documents.
        # It integrates with Language Models and various chain types to provide precise answers.
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

        # TODO: Replace load_qa_chain with self-crafted prompt for better control over the output.
        # Formatted output would be better: eg. to have a field "answer_found: true/false"
        # Internally load_qa_chain user the following system prompt:
        # "Use the following pieces of context to answer the user's question.
        # If you don't know the answer, just say that you don't know, don't try to make up an answer."

    def search_local_knowledge(self, user_input):
        """
        Search in local vector store for related documents and provide most relevant ones to LLM to get precise response.
        LLM will reply that it doesn't know (eg. if no documents are found and answer cannot be determined).
        """
        match = self.knowledge.vectors.similarity_search(user_input)
        response = self.chain.run(input_documents=match, question=user_input)
        return response

class Knowledge:
    def __init__(self):
        self.embeddings = init_embeddings()
        self.vectors = load_knowledge_vectors(self.embeddings)





