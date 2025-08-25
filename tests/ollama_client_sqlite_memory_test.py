import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pytest
from unittest.mock import patch, MagicMock
from friday.llm_integration.ollama_client import OllamaClient
from friday.memory.sqlite_conversation_memory import SqliteConversationMemory
from friday.prompts import GENERAL_SYSTEM_PROMPT

@pytest.fixture
def client():
    return OllamaClient(memory=SqliteConversationMemory(system_prompt=GENERAL_SYSTEM_PROMPT))

def mock_post_generate(*args, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {"role": "assistant", "content": "Python is a programming language."}
    }
    return mock_resp

def mock_post_read_file(*args, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {"role": "assistant", "content": "This file defines a Python class."}
    }
    return mock_resp


@patch("requests.post", side_effect=mock_post_generate)
def test_generate_action(mock_post, client):
    response = client.generate_action("What is Python?")
    assert "Python is a programming language." in response
    mock_post.assert_called_once()


def test_build_context_prompt(client):
    # Add some messages to memory
    client.memory.add_to_history("user", "Hello")
    client.memory.add_to_history("assistant", "Hi there!")
    prompt = client._build_context_prompt("What is Python?")
    assert "Previous conversation context:" in prompt
    assert "USER: Hello" in prompt
    assert "ASSISTANT: Hi there!" in prompt



@patch("requests.post", side_effect=mock_post_generate)
def test_handle_input_generate_action(mock_post, client, monkeypatch):
    # Patch parse_json_from_model to return a valid action
    monkeypatch.setattr(
        "friday.llm_integration.ollama_client.parse_json_from_model",
        lambda x: {"action": "generate_action", "question": "What is Python?"}
    )
    response = client.handle_input("What is Python?")
    assert "Python is a programming language." in response


@patch("requests.post", side_effect=mock_post_generate)
def test_generate_natural_response(mock_post, client):
    client.memory.add_to_history("user", "What is Python?")
    response = client.generate_natural_response("What is Python?")
    assert "Python is a programming language." in response
    mock_post.assert_called()


def test_get_conversation_summary(client):
    client.memory.add_to_history("user", "Hello")
    summary = client.get_conversation_summary()
    assert isinstance(summary, dict)
    assert "total_messages" in summary

def test_clear_context(client):
    client.memory.add_to_history("user", "Hello")
    client.clear_context()
    msgs = client.memory.get_messages()
    # Should only have the system prompt after clear
    assert len(msgs) == 1
    assert msgs[0]["role"] == "system"

def test_get_context_messages(client):
    client.memory.add_to_history("user", "Hello")
    msgs = client.get_context_messages()
    assert any(m["role"] == "user" for m in msgs)

@patch("requests.post", side_effect=mock_post_read_file)
def test_read_file(mock_post, tmp_path, client):
    # Create a temporary file
    file_path = tmp_path / "test.txt"
    file_path.write_text("class Test: pass")

    response = client.read_file("Explain this file", str(file_path))
    assert "Python class" in response
    mock_post.assert_called_once()
