from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

def load_knowledge_vectors(embeddings):
    return _load_test_knowledge_vectors(embeddings)

def _load_test_knowledge_vectors(embeddings):
    print("Loading test knowledge with embeddings:" + embeddings.model)
    sentences = load_test_knowledge_sentences()
    print("Creating FAISS vector store")
    vectors = FAISS.from_texts(sentences, embeddings)
    return vectors

def load_test_knowledge_sentences():
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

