import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pytest
from unittest.mock import patch, MagicMock
from src.friday.llm_integration.ollama_client import OllamaClient

@pytest.fixture
def client():
    return OllamaClient()

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

@patch("requests.post", side_effect=mock_post_read_file)
def test_read_file(mock_post, tmp_path, client):
    # Create a temporary file
    file_path = tmp_path / "test.txt"
    file_path.write_text("class Test: pass")

    response = client.read_file("Explain this file", str(file_path))
    assert "Python class" in response
    mock_post.assert_called_once()
