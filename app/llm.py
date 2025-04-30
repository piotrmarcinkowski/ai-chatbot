import os
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings

_my_api_key = os.getenv("OPENAI_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not defined.")

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "ai-chatbot"

def init_llm():
    return ChatOpenAI(
        openai_api_key=_my_api_key,
        temperature=0.5,
        max_tokens=1000,
        model_name="gpt-3.5-turbo"
)
    
def init_embeddings():
    return OpenAIEmbeddings(openai_api_key=_my_api_key)
