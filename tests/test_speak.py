import io
import os
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Skip tests if Flask is not installed in the environment
try:
    import flask  # noqa: F401
except Exception:
    pytest.skip('Flask not installed; skipping endpoint tests', allow_module_level=True)

from importlib import import_module

# import the app module explicitly to avoid package-level imports
app = import_module('voice_assistant.app').app


def test_speak_endpoint():
    client = app.test_client()
    resp = client.post('/speak', json={'text': 'hello world'})
    assert resp.status_code == 200
    assert 'audio' in resp.content_type
