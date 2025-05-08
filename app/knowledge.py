from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

class Knowledge:
    def __init__(self, llm, embeddings):
        """Initialize the Knowledge class and load knowledge vectors."""
        self.llm = llm
        self.embeddings = embeddings
        self.vectors = self.load_knowledge_vectors(embeddings)
        # load_qa_chain is designed for question-answering tasks over a list of documents.
        # It integrates with Language Models and various chain types to provide precise answers.
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

    def find_context(self, user_input):
        """
        Finds the most relevant context for the given user input by searching the knowledge base.
        """
        match = self.vectors.similarity_search(user_input)
        response = self.chain.run(input_documents=match, question=user_input)
        return response

    def load_knowledge_vectors(self, embeddings):
        return self._load_test_knowledge_vectors(embeddings)

    def _load_test_knowledge_vectors(self, embeddings):
        print("Loading test knowledge with embeddings:" + embeddings.model)
        sentences = self._load_test_knowledge_sentences()
        print("Creating FAISS vector store")
        # TODO: Replace FAISS with chromadb
        # TODO: Add storing to file - load from file if available, create a file if not there yet
        vectors = FAISS.from_texts(sentences, embeddings)
        return vectors

    def _load_test_knowledge_sentences(self):
        knowledge = """
        Nasza rodzina składa się z 6 osób. Mieszkają z nami jeszcze 2 psy, które uwielbiają biegać w przydomowym ogrodzie.
    Janusz jest tatą. Grażyna jest mamą. Sebastian jest synem. Karina jest córką. Psy wabią się Kapsel i Kufelek. Psy są mieszańcami.
    Kapsel jest czarny, a Kufelek jest brązowy. Kapsel ma 3 lata, a Kufelek ma 2 lata. Kapsel jest większy od Kufelka.    
        """

        # Split text into sentences
        splitter = RecursiveCharacterTextSplitter(
            separators=[".", "!", "?", "\n"],
            chunk_size=30,
            chunk_overlap=10,
        )
        sentences = splitter.split_text(knowledge)
        return sentences

    