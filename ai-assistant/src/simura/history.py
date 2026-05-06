"""SQLite-backed conversation history for SIMURA Assistant.

Each row is one message. Conversations are grouped by ``conversation_id``.
The schema is intentionally tiny so older builds can read newer DBs.
"""
from __future__ import annotations

import os
import sqlite3
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT    NOT NULL,
    created_at      REAL    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('system','user','assistant','tool')),
    content         TEXT    NOT NULL,
    model           TEXT
);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, created_at);
"""


@dataclass
class Message:
    role: str
    content: str
    model: str | None = None
    created_at: float = 0.0


class History:
    def __init__(self, path: str) -> None:
        Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(os.path.expanduser(path))
        with closing(self._db.cursor()) as cur:
            cur.executescript(SCHEMA)
        self._db.commit()

    @staticmethod
    def new_conversation_id() -> str:
        return uuid.uuid4().hex[:16]

    def append(self, conversation_id: str, msg: Message) -> None:
        with closing(self._db.cursor()) as cur:
            cur.execute(
                "INSERT INTO messages (conversation_id, created_at, role, content, model) "
                "VALUES (?, ?, ?, ?, ?)",
                (conversation_id, msg.created_at or time.time(),
                 msg.role, msg.content, msg.model),
            )
        self._db.commit()

    def list_conversations(self, limit: int = 50) -> list[tuple[str, float, str]]:
        """Return (conversation_id, last_ts, first_user_message_preview)."""
        rows = self._db.execute(
            """
            SELECT conversation_id,
                   MAX(created_at) AS last_ts,
                   COALESCE(
                     (SELECT content FROM messages m2
                       WHERE m2.conversation_id = m1.conversation_id
                         AND m2.role = 'user'
                       ORDER BY created_at LIMIT 1),
                     ''
                   ) AS preview
              FROM messages m1
             GROUP BY conversation_id
             ORDER BY last_ts DESC
             LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [(cid, ts, preview[:80]) for cid, ts, preview in rows]

    def load(self, conversation_id: str) -> list[Message]:
        rows = self._db.execute(
            "SELECT role, content, model, created_at FROM messages "
            "WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,),
        ).fetchall()
        return [Message(role=r, content=c, model=m, created_at=t) for (r, c, m, t) in rows]

    def close(self) -> None:
        self._db.close()
