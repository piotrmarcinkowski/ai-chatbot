import pytest
from unittest.mock import patch, MagicMock
from langchain_core.language_models.fake import FakeListLLM
from langchain_community.embeddings import DeterministicFakeEmbedding
from langchain_core.messages.human import HumanMessage
import model.chat_history

def test_vector_store_search():
    """
    Test the initialization of the ChatVectorStore with FakeEmbeddings and verify with basic search.
    """
    embeddings = DeterministicFakeEmbedding(size=100)
    vector_store = model.chat_history.ChatVectorStore(embeddings=embeddings)

    messages = [
        HumanMessage(content="Hello, how are you?"),
        HumanMessage(content="What is the weather like today?"),
        HumanMessage(content="Tell me a joke."),
        HumanMessage(content="Joke: Why did the chicken cross the road? To get to the other side!"),
    ]
    for message in messages:
        vector_store.add_message(message)

    results = vector_store.search_messages("Were any jokes told?", limit=1)

    assert len(results) == 1
    assert results[0].page_content == messages[3].content


@patch("model.chat_history.model_config")
def test_vector_store_configuration(mock_model_config, tmpdir):
    """
    Test the initialization of the ChatVectorStore with a configured persist directory.
    """
    # Prepare temporary directory for testing
    expected_persist_directory = tmpdir.mkdir("test_persist_directory")
    mock_model_config.get.return_value = str(expected_persist_directory)

    embeddings = DeterministicFakeEmbedding(size=100)
    vector_store = model.chat_history.init_chat_vector_store(embeddings)

    mock_model_config.get.assert_called_once_with("chat_vector_store_dir")
    assert vector_store.persist_directory == str(expected_persist_directory)
    assert len(tmpdir.listdir()) == 1