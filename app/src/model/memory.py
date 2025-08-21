from langchain_community.storage.mongodb import MongoDBStore
from langchain_core.stores import BaseStore
from config.model_config import model_config

class Memory:
    """
    A class that manages long-term memory for the chatbot.
    """
    def __init__(self):
        print("Memory: Initializing long-term memory")
        connection_string = model_config.get("mongodb_connection_string")
        database_name = model_config.get("mongodb_longterm_memory_db_name")
        collection_name = model_config.get("mongodb_longterm_memory_collection_name")
        print(f"Memory: Using MongoDB connection string: {connection_string}, database: {database_name}, collection: {collection_name}")

        self._store = MongoDBStore(
            connection_string,
            db_name=database_name,
            collection_name=collection_name)
        
        print("Memory: Long-term Memory initialized")
        
    def get_store(self) -> BaseStore:
        """
        Returns the MongoDB store instance.
        """
        return self._store
    
def init_memory() -> Memory:
    return Memory()
