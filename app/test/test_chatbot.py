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
def test_chatbot_instance_creation(mock_init_llm, mock_init_embeddings, mock_init_chat_history_saver,
                                   mock_init_chat_archive, mock_init_chat_vector_store):
    chatbot = model.chatbot.Chatbot()
    
    assert chatbot.chat_session_id is None
    mock_init_llm.assert_called_once()
    mock_init_embeddings.assert_called_once()
    mock_init_chat_history_saver.assert_called_once()
    mock_init_chat_archive.assert_called_once()
    mock_init_chat_vector_store.assert_called_once()