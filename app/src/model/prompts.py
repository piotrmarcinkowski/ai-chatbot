from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState

#TODO: Move history_prompt here


def system_prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:  
    assitant_name = config["configurable"].get("assistant_name")
    system_message = f"""
    You are a helpful assistant called {assitant_name}. Respond using the same language as in the user query. If you are unsure, respond in English.
    """
    return [{"role": "system", "content": system_message}] + state["messages"]