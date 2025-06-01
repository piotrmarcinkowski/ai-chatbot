import os
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings


assert os.environ[
    "OPENAI_API_KEY"
], "Set the OPENAI_API_KEY environment variable with your OpenAI API key."

_my_api_key = os.getenv("OPENAI_API_KEY")

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
