"""Lightweight smoke tests that don't require Qt or Ollama to be running."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from simura.config import Config, load_config, save_config
from simura.history import History, Message
from simura.ollama import OllamaClient, OllamaError
from simura.tools import (
    fs_read,
    fs_search,
    parse_shell,
    shell_run,
)

# --------------------------- config -----------------------------------------

def test_config_roundtrip(tmp_path):
    """Saving and reloading a Config returns the same values."""
    cfg = Config(model="llama3.2:3b", ollama_host="http://example:11434")
    cfg_path = tmp_path / "config.yaml"
    save_config(cfg, override=cfg_path)
    loaded = load_config(override=cfg_path)
    assert loaded.model == "llama3.2:3b"
    assert loaded.ollama_host == "http://example:11434"


def test_config_defaults_created(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg = load_config(override=cfg_path)
    assert cfg_path.exists()
    assert cfg.model  # non-empty default


# --------------------------- history ----------------------------------------

def test_history_roundtrip(tmp_path):
    db = tmp_path / "h.sqlite3"
    h = History(str(db))
    cid = History.new_conversation_id()
    h.append(cid, Message(role="user", content="hello", created_at=100))
    h.append(cid, Message(role="assistant", content="world", model="llama3.2:3b",
                          created_at=101))
    msgs = h.load(cid)
    assert [m.role for m in msgs] == ["user", "assistant"]
    assert msgs[1].content == "world"
    convs = h.list_conversations()
    assert len(convs) == 1
    assert convs[0][0] == cid
    h.close()


# --------------------------- tools ------------------------------------------

def test_parse_shell_rejects_pipelines():
    with pytest.raises(ValueError):
        parse_shell("ls | grep foo")
    with pytest.raises(ValueError):
        parse_shell("echo hi > /tmp/x")


def test_parse_shell_splits_args():
    assert parse_shell("ls -la /etc") == ["ls", "-la", "/etc"]
    assert parse_shell('echo "hello world"') == ["echo", "hello world"]


def test_shell_run_uname():
    """uname is in the allow-list and should always succeed on Linux/macOS."""
    r = shell_run(["uname", "-s"])
    assert r.ok
    assert r.output.strip() in {"Linux", "Darwin"}
    assert r.meta["is_safe_read"] is True


def test_shell_run_missing_binary():
    r = shell_run(["definitely-not-a-real-binary-xyz"])
    assert not r.ok
    assert "not found" in r.error


def test_fs_search_finds_self(tmp_path):
    """fs_search should find a file we just created."""
    (tmp_path / "needle.txt").write_text("x")
    (tmp_path / "haystack.dat").write_text("y")
    r = fs_search(str(tmp_path), "needle")
    assert r.ok
    assert "needle.txt" in r.output
    assert "haystack.dat" not in r.output


def test_fs_read_roundtrip(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello\n")
    r = fs_read(str(p))
    assert r.ok
    assert r.output == "hello\n"


def test_fs_read_rejects_directory(tmp_path):
    r = fs_read(str(tmp_path))
    assert not r.ok


# --------------------------- ollama client ----------------------------------

def test_ollama_unreachable_is_false():
    """A bogus host should report not-reachable without raising."""
    client = OllamaClient("http://127.0.0.1:1")  # nothing listens here
    assert client.is_reachable() is False


def test_ollama_chat_stream_parses_json_lines():
    """Mock requests so we can exercise the streaming parser."""
    fake_lines = [
        json.dumps({"message": {"content": "Hello"}, "done": False}),
        json.dumps({"message": {"content": ", world"}, "done": False}),
        json.dumps({"done": True}),
    ]

    class FakeResponse:
        ok = True

        def raise_for_status(self):
            pass

        def iter_lines(self, decode_unicode=True):
            yield from fake_lines

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

    client = OllamaClient("http://localhost:11434")
    with patch("simura.ollama.requests.post", return_value=FakeResponse()):
        chunks = list(client.chat_stream("test", [{"role": "user", "content": "hi"}]))
    assert "".join(chunks) == "Hello, world"


def test_ollama_chat_stream_propagates_errors():
    fake_lines = [json.dumps({"error": "model not found"})]

    class FakeResponse:
        ok = True
        def raise_for_status(self): pass
        def iter_lines(self, decode_unicode=True):
            yield from fake_lines
        def __enter__(self): return self
        def __exit__(self, *_a): return False

    client = OllamaClient("http://localhost:11434")
    with patch("simura.ollama.requests.post", return_value=FakeResponse()):
        with pytest.raises(OllamaError):
            list(client.chat_stream("test", [{"role": "user", "content": "hi"}]))
