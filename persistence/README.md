# Persistence

This folder contains components that are responsible for storing all knowledge that is accessible by ai-chatbot

# Chats history

Storing and updating history of all chats from user-model interactions.

**Requirements:**
- Store history of chats - messages with metadata (session-id, date, from, tags eg. #note, #idea, #fact #important)
- Fast search (indexing)
- Backup

**Here are the key advantages of using MongoDB for this usecase:**
- AI & LangChain Integration – Works well as a knowledge base for retrieval-augmented generation (RAG) and embedding storage.
- Flexible Document Storage – Stores chat history and facts in JSON-like BSON, allowing easy schema evolution.
- Replication & Backups – Built-in replication ensures high availability, with support for incremental backups.

# Chat history as embeddings

Based on a database containing chat history and a selected embedding implementation, such as OpenAI embeddings, a vector database can be generated and used by agents for semantic search.

TODO: Add ChromaDB vector database that can be populated with data from MongoDB database holding chats history

**Here are the key advantages of using ChromaDB for this usecase:**
- Optimized for Vector Search – Designed specifically for fast similarity search, making it ideal for semantic retrieval in AI applications.
- Simple & Scalable – Easy to set up and scale, with in-memory and persistent storage options for different performance needs.
- Seamless Integration – Natively supports LangChain, making it a great choice for AI-driven fact retrieval.
- Flexible Storage – Can use local disk, cloud storage, or databases like PostgreSQL for persistence.

# Backup

##Encrypt Backups
TODO: Use mongodump with encryption or encrypt the backup file manually:
eg.
```
mongodump --archive=backup.gz --gzip
# encrypt
openssl enc -aes-256-cbc -salt -in backup.gz -out backup.enc -pass pass:MySecurePassword
# decrypt
openssl enc -aes-256-cbc -d -in backup.enc -out backup.gz -pass pass:MySecurePassword
```