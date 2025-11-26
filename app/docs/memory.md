# Chatbot memory

## Requirements

Referring to past conversations, bringing up broader context.

Sample user prompts that should be supported:
- Can we go back to yesterday's conversation about ...
- Do you remember that idea we talked about some time ago? ...
- Remind me what things we were supposed to check in order to...
- Search the chat about ...
- Have we talked about this before?

## Implementation decisions

- Messages should be stored in a vector database to enable fast context retrieval for user queries.
- Converting message text to vector representation requires embeddings. For that OpenAI embeddings will be used but it should be possible to change embeddings provider in the future.
- Since the embeddings can change in the future the messages should also be stored in plain text so the conversion to vector form can be repeated at any time.
- For certain requirements the stored messages should include the following metadata: 
timestamp/date, session_id,

## LangChain way of implementing memory

- [LangChain message histoty HowTo](https://python.langchain.com/v0.2/docs/how_to/message_history/)
- [LangChain Essentials - Conversational Memory for OpenAI - LangChain](https://github.com/aurelio-labs/langchain-course/blob/main/chapters/04-chat-memory.ipynb)
- [MongoDBChatMessageHistory](https://python.langchain.com/docs/integrations/memory/mongodb_chat_message_history/)


### MongoDB (LangChain MongoDBChatMessageHistory)
Initial implementation (tags:1.x) was done around [MongoDBChatMessageHistory](https://python.langchain.com/docs/integrations/memory/mongodb_chat_message_history/#usage) class to store chat message history in a Mongodb database.

Chat messages are stored as a separate documents in chat/chat_history collection in mongodb database.

Sample document looks like this:
```json
{
  "_id": {
    "$oid": "68362bb02f4a7dd6650e7b40"
  },
  "SessionId": "254751de-538a-463f-a8a9-b69bfac3e560",
  "History": "{\"type\": \"human\", \"data\": {\"content\": \"How do you do?\", \"additional_kwargs\": {}, \"response_metadata\": {}, \"type\": \"human\", \"name\": null, \"id\": null, \"example\": false}}"
}
```
Database can be browsed with vscode mongodb extension that is available within devcontainer.

![vscode mongodb extension](./img/vscode-mongodb-extension.png)

### Issues with using two storages for messages 
The way the Memory API is designed in LangChain is quite problematic. In order to meet the requirement of storing messages in two storages (MongoDB and a vector database), several rather inelegant workarounds were necessary, and the resulting code was poorly testable and hard to maintain.

```
LangChain was used in versions 1.x of ai-chatbot. In version 2.x it was replaced with LangGraph.
```


## LangGraph way of implementing memory
- [Comparison of LangChain and LangGraph way of implementing agents with memory](https://python.langchain.com/docs/how_to/migrate_agent/)
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

### LangGraph memory types

- [LangGraph memory concept](https://langchain-ai.github.io/langgraph/concepts/memory/)

`Short-term memory`, or thread-scoped memory, can be recalled at any time from within a single conversational thread with a user. LangGraph manages short-term memory as a part of agent's state. State is persisted to a database using a checkpointer so the thread can be resumed at any time. Short-term memory updates when the graph is invoked or a step is completed, and the State is read at the start of each step.

`Long-term memory` is shared across conversational threads. It can be recalled at any time and in any thread. Memories are scoped to any custom namespace, not just within a single thread ID. LangGraph provides stores (reference doc) to let you save and recall long-term memories.

![alt text](img/langgraph-memory-types.png)

In LangGraph:
- Short-term memory is also referred to as thread-level memory.
- Long-term memory is also called cross-thread memory.

A [thread](https://langchain-ai.github.io/langgraph/concepts/persistence/#threads) represents a sequence of related runs grouped by the same thread_id.

# Short-term memory

This section describes short-term memory implementations used in this project.

### Langraph persistence implementation how-to

https://langchain-ai.github.io/langgraph/how-tos/persistence/
https://langchain-ai.github.io/langgraph/agents/context/

### MongoDB (LangGraph Checkpointer) 
After migration to LangGraph (tags:2.x) the implementation of chat history was updated to use checkpointer [MongoDBSaver](https://python.langchain.com/docs/integrations/memory/mongodb_chat_message_history/#usage).

Chat messages, similarily to LangChain's MongoDBChatMessageHistory, are stored as a separate documents. Note that some fields are of BSON type, eg. binary representation of ChatMessage.

[BSON spec](https://bsonspec.org/spec.html), 

Sample document looks like this:
```json
{
  "_id": {
    "$oid": "6859bef720a416c9b33c8d78"
  },
  "checkpoint_id": "1f050743-8fe8-6f9a-bfff-b479841ef6d9",
  "checkpoint_ns": "",
  "thread_id": "c0eecbcc-ac73-49f3-9da5-f05baea2f2b4",
  "checkpoint": {
    "$binary": {
      "base64": "h6F2A6J0c9kgMjAyNS0wNi0yM1QyMDo1NDoxNS4xMTIwNTkrMDA6MDCiaWTZJDFmMDUwNzQzLThmZTgtNmY5YS1iZmZmLWI0Nzk4NDFlZjZkOa5jaGFubmVsX3ZhbHVlc4GpX19zdGFydF9fgahtZXNzYWdlc5GCpHJvbGWkdXNlcqdjb250ZW50skphayBtYXN6IG5hIGltacSZP7BjaGFubmVsX3ZlcnNpb25zgalfX3N0YXJ0X18BrXZlcnNpb25zX3NlZW6BqV9faW5wdXRfX4CtcGVuZGluZ19zZW5kc5A=",
      "subType": "00"
    }
  },
  "metadata": {
    "source": {
      "$binary": {
        "base64": "ImlucHV0Ig==",
        "subType": "00"
      }
    },
    "writes": {
      "__start__": {
        "messages": {
          "$binary": {
            "base64": "W3sicm9sZSI6ICJ1c2VyIiwgImNvbnRlbnQiOiAiSmFrIG1hc3ogbmEgaW1pxJk/In1d",
            "subType": "00"
          }
        }
      }
    },
    "step": {
      "$binary": {
        "base64": "LTE=",
        "subType": "00"
      }
    },
    "parents": {},
    "thread_id": {
      "$binary": {
        "base64": "ImMwZWVjYmNjLWFjNzMtNDlmMy05ZGE1LWYwNWJhZWEyZjJiNCI=",
        "subType": "00"
      }
    },
    "assistant_name": {
      "$binary": {
        "base64": "IkphcnZpcyI=",
        "subType": "00"
      }
    }
  },
  "parent_checkpoint_id": null,
  "type": "msgpack"
}
```
Database can be browsed with vscode mongodb extension that is available within devcontainer.

### Implementation decisions

In order to access stored chat messages some data has to be base64-decoded (ChatMessage instances are stored as binary objects). Binary storage mechanism used by MongoDBSaver can be found here:
https://github.com/langchain-ai/langchain-mongodb/blob/libs/langchain-mongodb/v0.6.2/libs/langgraph-checkpoint-mongodb/langgraph/checkpoint/mongodb/aio.py#L309

### Mongodb extension 'playgrounds'
[MongoDb Playgrounds](./../test/mongo_playground/)

# Long-term memory

This section describes long-term memory implementations used in this project.

## Links

- https://langchain-ai.github.io/langgraph/concepts/memory/#long-term-memory

## Memory types

Memory types used in AI agents are often categorized into three main types:
- Semantic memory - facts - learned things - involves the retention of specific facts and concepts 
- Episodic memory - eperiences - things that happened
- Procedural memory - rules - system prompts

More about memory types:
https://www.psychologytoday.com/us/basics/memory/types-of-memory


## Semantic memory

https://docs.langchain.com/oss/python/langgraph/memory#semantic-memory

### Managing semantic memories

- Profile - memories can be a single, continuously updated “profile” of well-scoped and specific information about a user, organization, or other entity (including the agent itself). A profile is generally just a JSON document with various key-value pairs you’ve selected to represent your domain.

- Collection - memories can be a collection of documents that are continuously updated and extended over time. Each individual memory can be more narrowly scoped and easier to generate, which means that you’re less likely to lose information over time. It’s easier for an LLM to generate new objects for new information than reconcile new information with an existing profile

### Memory update strategies
https://github.com/hinthornw/trustcall

### LangGraph way of implementing long-term memory
The Store currently supports both: 
- [Semantic search](https://reference.langchain.com/python/langgraph/store/#langgraph.store.base.SearchOp.query)
- [Filtering by content](https://reference.langchain.com/python/langgraph/store/#langgraph.store.base.SearchOp.filter)

## Episodic memory
https://docs.langchain.com/oss/python/langgraph/memory#episodic-memory

The episodic memory involves recalling past events or actions.

### MemoryStore
https://docs.langchain.com/oss/python/langgraph/persistence#memory-store


[Integrate MongoDB with LangGraph](https://www.mongodb.com/docs/atlas/ai-integrations/langgraph/)
[MongoDB Store: Enabling cross-thread long-term memory](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)
[LangGraph With MongoDB: Building Conversational Long-Term Memory for Intelligent AI Agents](https://dev.to/mongodb/langgraph-with-mongodb-building-conversational-long-term-memory-for-intelligent-ai-agents-2pcn)

# MongoDBStore
The MongoDBStore provides a way to store and retrieve long-term memories using MongoDB as the backend database. It stores memories in the following format:

```json
{
  "_id": {
    "$oid": "6927569344516936bce6de2c"
  },
  "key": "4a5f4555-12ec-497c-b999-7e1b36100e46",
  "namespace": [
    "Piotr",
    "facts"
  ],
  "created_at": {
    "$date": "2025-11-26T19:35:47.905Z"
  },
  "updated_at": {
    "$date": "2025-11-26T19:35:47.905Z"
  },
  "value": "The user's name is Piotr."
}
```