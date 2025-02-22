import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
import os
import sys


# Validate OPENAI_API_KEY
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY environment variable is not defined.")
    sys.exit(1)

my_api_key = os.getenv("OPENAI_API_KEY")

st.header("My AI Chatbot")

with st.sidebar:
    st.title("Upload text file")
    file = st.file_uploader("Choose a file and chat with the AI", type=["txt"])

if file is not None:
    text = file.read().decode("utf-8")
    st.write(text)

    # Split text into sentences
    splitter = RecursiveCharacterTextSplitter(
        separators=[".", "!", "?", "\n"],
        chunk_size=1000
    )
    sentences = splitter.split_text(text)

    # Create embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=my_api_key)

    # Create vector store
    vectors = FAISS.from_texts(sentences, embeddings)

    # Get user input
    user_input = st.text_input("Start conversation with AI chatbot: ")

    if user_input:
        match = vectors.similarity_search(user_input)

        llm = ChatOpenAI(
            openai_api_key=my_api_key,
            temperature=0.5,
            max_tokens=1000,
            model_name="gpt-3.5-turbo"
        )

        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents = match, question=user_input)

        st.write(response)
