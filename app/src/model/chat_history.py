from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config.model_config import model_config
from pymongo import MongoClient
import time
from langchain_core.messages import BaseMessage
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.checkpoint.mongodb import MongoDBSaver

# TODO: Make this a structured prompt with bool result indicating if LLM knew the answer
history_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Use the following pieces of chat history to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}"),
    ]
)

class ChatArchive:
    """
    Manages the chat archive, allowing retrieval of archived chat sessions.
    """
    def __init__(self):
        """
        Initializes the chat archive.
        """
        print("ChatArchive: Initializing chat archive")
        connection_string = model_config.get("mongodb_connection_string")
        database_name = model_config.get("mongodb_chat_history_db_name")
        collection_name = model_config.get("mongodb_chat_history_collection_name")
        print(f"ChatArchive: Using MongoDB connection string: {connection_string}, database: {database_name}, collection: {collection_name}")

        client = MongoClient(connection_string)
        self._checkpointer = MongoDBSaver(
            client = client,
            db_name = database_name,
            checkpoint_collection_name = collection_name,
            writes_collection_name = collection_name + "_writes",
        )

    def get_session_id_set(self):
        """
        Retrieves a set with archived chat sessions IDs.
        :return: A set of IDs of the archived chat sessions.
        """
        print("ChatArchive.get_session_id_set: Retrieving archived chat sessions")
        
        connection_string = model_config.get("mongodb_connection_string")
        database_name = model_config.get("mongodb_chat_history_db_name")
        collection_name = model_config.get("mongodb_chat_history_collection_name")

        print(f"ChatArchive.get_session_id_set: Retrieving archived sessions from MongoDB at {connection_string}, database: {database_name}, collection: {collection_name}")
        start_time = time.time()
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]

        # Retrieve all unique thread_id values
        pipeline = [
            {
                "$group": {
                    "_id": "$thread_id",
                }
            },
        ]
        session_id_list = list(collection.aggregate(pipeline))
        session_id_set = {session["_id"] for session in session_id_list}
        
        elapsed_time = time.time() - start_time
        print(f"ChatArchive.get_session_id_set: Found {len(session_id_set)} archived sessions in {elapsed_time:.4f} seconds")
        return session_id_set
    
    def get_session_list(self):
        """
        Retrieves a list of archived chat sessions with their metadata.
        Sessions are sorted by timestamp in descending order.
        :return: A list of dictionaries containing session metadata, including session ID, first message, and timestamp.
        """
        start_time = time.time()
        
        session_id_set = self.get_session_id_set()
        sessions = [
            {
                "session_id": session_id,
                "messages": self.get_chat_messages(session_id),
            }
            for session_id in session_id_set
        ]

        def get_first_human_message(session):
            if not session["messages"]:
                return None
            for message in session["messages"]:
                if message.type == "human":
                    return message
            return None
        
        sessions_with_first_message = [
            {
                "session_id": session["session_id"],
                "first_message": get_first_human_message(session),
            }
            for session in sessions
        ]
        
        sessions_with_metadata = [
            {
                "session_id": session["session_id"],
                "first_message": session["first_message"].content if session["first_message"] else "",
                "timestamp": session["first_message"].additional_kwargs.get("timestamp", 0) if session["first_message"] else 0,
                "time": session["first_message"].additional_kwargs.get("time", "<Unknown time>") if session["first_message"] else "<Unknown time>",
            }
            for session in sessions_with_first_message
        ]

        sessions_with_metadata.sort(key=lambda x: x['timestamp'], reverse=True)

        elapsed_time = time.time() - start_time
        print(f"ChatArchive.get_sessions: Sessions retrieval took {elapsed_time:.4f} seconds")
        return sessions_with_metadata
   
    def get_chat_messages(self, session_id):
        """
        Retrieves the chat history for the given session ID.
        If no history is found, returns an empty list.
        :param session_id: The session ID for which to retrieve chat history.
        :return: A list of chat messages for the given session ID.
        """
        print(f"ChatArchive.get_chat_messages: Retrieving chat history for session_id: {session_id}")
        config={"configurable": {"thread_id": session_id}}
        last_checkpoint = self._checkpointer.get(
            config=config,
        )
        print(f"ChatArchive.get_chat_messages: Last checkpoint for session_id {session_id}: {last_checkpoint}")
        if last_checkpoint is None:
            print(f"ChatArchive.get_chat_messages: No checkpoint found for session_id: {session_id}")
            return []
        if not 'channel_values' in last_checkpoint:
            print(f"ChatArchive.get_chat_messages: No channel_values found in last checkpoint for session_id {session_id}")
            return []
        channel_values = last_checkpoint['channel_values']
        if not 'messages' in channel_values:
            print(f"ChatArchive.get_chat_messages: No messages found in channel_values for session_id {session_id}")
            return []
        
        messages_list = channel_values['messages']
        print(f"ChatArchive.get_chat_messages: Found {len(messages_list)} messages for session_id {session_id}")
        return messages_list

    def get_checkpointer(self) -> BaseCheckpointSaver:
        """
        Returns a checkpointer for the chat archive.
        This can be used to save and restore the state of the chat archive.
        """
        return self._checkpointer
    
def init_chat_archive() -> ChatArchive:
    return ChatArchive()

class ChatVectorStore:
    def __init__(self, embeddings:Embeddings=None, persist_directory:str=None):
        print(f"ChatVectorStore: embeddings: {embeddings}")
        print(f"ChatVectorStore: persist_directory: {persist_directory}")
        print("ChatVectorStore: Creating Chroma vector store")
        self._persist_directory = persist_directory
        self.vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,)

    def add_message(self, message: BaseMessage) -> None:
        """
        Adds the message to the vector store.
        This method is called when a new message is added to the chat history.
        """
        print(f"ChatVectorStore.add_message: Adding message to vector store: {message}")
        self.add_messages([message])

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """
        Adds a list of messages to the vector store.
        :param messages: A list of BaseMessage objects to be added to the vector store.
        """
        print(f"ChatVectorStore.add_messages: Adding {len(messages)} messages to vector store")
        texts = [msg.content for msg in messages]
        metadatas = [msg.additional_kwargs for msg in messages]
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)

    def search_messages(self, query: str, limit: int = 20) -> list[BaseMessage]:
        """
        Searches for messages in the vector store that are similar to the query.
        :param query: The query string to search for.
        :param limit: The maximum number of results to return.
        :return: A list of messages that match the query.
        """
        print(f"ChatVectorStore.search_messages: Searching for '{query}'")
        results = self.vector_store.similarity_search(query, k=limit)
        return results
    
    @property
    def persist_directory(self):
        """Get the directory where the vector store is persisted."""
        return self._persist_directory
    
    def refresh(self, chat_archive: ChatArchive):
        """
        Refreshes the vector store by re-indexing all messages from the chat archive.
        :param chat_archive: The chat archive to retrieve messages from.
        :param embeddings: The embeddings to use for the vector store.
        """
        print("ChatVectorStore.refresh: Re-indexing all messages in the vector store")
        start_time = time.time()
        chat_sessions = chat_archive.get_session_list()
        print(f"Chats to re-index: {len(chat_sessions)}")

        print("ChatVectorStore.refresh: Removing the vector store collection")
        self.vector_store.reset_collection()
        
        messages_count = 0
        
        for session in chat_sessions:
            session_id = session["session_id"]
            messages = chat_archive.get_chat_messages(session_id=session_id)
            if not messages:
                print(f"ChatVectorStore.refresh: No messages found for session {session_id}, skipping")
                continue
            messages_count += len(messages)
            self.add_messages(messages)
            print(f"ChatVectorStore.refresh: Added {len(messages)} messages from session {session_id}")

        elapsed_time = time.time() - start_time
        print(f"ChatVectorStore.refresh: Re-indexed {messages_count} messages in {elapsed_time:.4f} seconds")
        return messages_count

def init_chat_vector_store(embeddings: Embeddings) -> ChatVectorStore:
    """
    Initializes the chat vector store with the given embeddings.
    :param embeddings: The embeddings to use for the vector store.
    :return: An instance of ChatVectorStore.
    """
    print("init_chat_vector_store: Creating ChatVectorStore instance")
    
    persist_directory = model_config.get("chat_vector_store_dir")
    print("init_chat_vector_store: persist_directory:", persist_directory)

    return ChatVectorStore(embeddings=embeddings, persist_directory=persist_directory)
