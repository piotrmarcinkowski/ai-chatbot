from langchain_core.messages import SystemMessage
from config.model_config import assistant_config

def create_initial_system_message() -> SystemMessage:
    """
    Creates a system message for the chatbot. The message can be customized
    based on the configuration provided.
    """
    assistant_name = assistant_config.get("assistant_name", "Assistant")
    
    system_message = f"""
    You are a helpful assistant called {assistant_name}. Respond using the same language as in the last human message. If you are unsure, respond in English.
    If there is no direct date or time reference in the user query, you can use the current date and time to answer. Always retrieve the current date and time using provided tools.
    Try to answer the user query as accurately as possible, using the tools available to you.
    If you are unsure about the answer, ask the user for clarification.
    If you need to use a tool, plan the tool calls first and then execute them.
    Keep your responses concise and relevant to the user's query. Generally provide short and to-the-point answers unless user asked for detailed answer.
    """
    return SystemMessage(content=system_message)