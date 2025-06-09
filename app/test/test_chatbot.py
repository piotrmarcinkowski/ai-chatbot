import pytest
from unittest.mock import patch, MagicMock
from langchain_core.language_models.fake import FakeListLLM
from langchain_community.embeddings import FakeEmbeddings
import model.chatbot

# Mock the functions imported to model.chatbot module instead of the original module
# with the definitions of these functions
# Refer to "Where to patch" section in the documentation: app/docs/code_testing.md
@patch("model.chatbot.init_llm")
@patch("model.chatbot.init_embeddings")
@patch("model.chatbot.init_chat_history_saver")
@patch("model.chatbot.init_chat_archive")
@patch("model.chatbot.init_chat_vector_store")
def test_chatbot_instance_creation(mock_init_chat_vector_store, mock_init_chat_archive, mock_init_chat_history_saver, 
                                   mock_init_embeddings, mock_init_llm):
    chatbot = model.chatbot.Chatbot()
    
    assert chatbot.chat_session_id is None

    # Have the dependencies been initialized?
    mock_init_llm.assert_called_once()
    mock_init_embeddings.assert_called_once()
    mock_init_chat_history_saver.assert_called_once()
    mock_init_chat_archive.assert_called_once()
    mock_init_chat_vector_store.assert_called_once()

    # Has the chat history been set up correctly?
    mock_init_chat_history_saver.return_value.manage_chat_history.assert_called_once()

    # Has the chat vector store been linked to the chat history saver to react on new messages?
    mock_init_chat_history_saver.return_value.add_new_message_callback.assert_called_once_with(
        mock_init_chat_vector_store.return_value.add_message
    )


@patch("model.chatbot.init_llm")
@patch("model.chatbot.init_embeddings")
@patch("model.chatbot.init_chat_history_saver")
@patch("model.chatbot.init_chat_archive")
@patch("model.chatbot.init_chat_vector_store")
def test_chatbot_new_chat(mock_init_chat_vector_store, mock_init_chat_archive, mock_init_chat_history_saver, 
                          mock_init_embeddings, mock_init_llm):
    chatbot = model.chatbot.Chatbot()
    
    assert chatbot.chat_session_id is None

    # Start a new chat session
    chatbot.start_new_chat()
    assert chatbot.chat_session_id is not None

@patch("model.chatbot.init_llm")
@patch("model.chatbot.init_embeddings")
@patch("model.chatbot.init_chat_history_saver")
@patch("model.chatbot.init_chat_archive")
@patch("model.chatbot.init_chat_vector_store")
def test_chatbot_messages_processing(mock_init_chat_vector_store, mock_init_chat_archive, mock_init_chat_history_saver, 
                                     mock_init_embeddings, mock_init_llm):
    
    mock_pipeline = MagicMock(name="mock pipeline")
    mock_init_chat_history_saver.return_value.manage_chat_history.return_value = mock_pipeline 

    chatbot = model.chatbot.Chatbot()
    chatbot.start_new_chat()
    user_input = "Hello, how are you?"
    chatbot.process_user_input(user_input)
    messages = chatbot.get_current_chat_messages()

    # Check if pipeline was invoked with the user input
    mock_pipeline.invoke.assert_called_once_with(
        {"user_input": user_input}, config={"configurable": {"session_id": chatbot.chat_session_id}}
    )
    
    mock_init_chat_archive.return_value.get_chat_messages.assert_called_once_with(chatbot.chat_session_id)
