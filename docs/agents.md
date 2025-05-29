# Agent concept

By themselves, language models can't take actions - they just output text. Agents are systems that take a high-level task and use an LLM as a reasoning engine to decide what actions to take and execute those actions.

https://python.langchain.com/docs/concepts/agents/

# LangChain vs LangGraph

During the framework selection phase for this project, a decision was made to implement the agents using the approach employed by LangGraph. At that time, the LangChain approach utilizing AgentExecutor was already considered legacy.

https://python.langchain.com/docs/concepts/agents/
LangGraph is an extension of LangChain specifically aimed at creating highly controllable and customizable agents. LangGraph is recommended to use for building agents.

## Legacy agent concept: AgentExecutor
LangChain previously introduced the AgentExecutor as a runtime for agents. While it served as an excellent starting point, its limitations became apparent when dealing with more sophisticated and customized agents. As a result, we're gradually phasing out AgentExecutor in favor of more flexible solutions in LangGraph.
https://python.langchain.com/docs/how_to/agent_executor/

## LangGraph's react agent executor
LangGraph's react agent executor manages a state that is defined by a list of messages. It will continue to process the list until there are no tool calls in the agent's output. To kick it off, we input a list of messages. The output will contain the entire state of the graph-- in this case, the conversation history.
https://python.langchain.com/docs/how_to/migrate_agent/ 