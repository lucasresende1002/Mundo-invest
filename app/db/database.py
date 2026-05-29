import sqlite3
import os
from typing import Optional

DB_PATH = os.environ.get("DB_PATH", "mundo_invest.db")

# Shared connection for in-memory mode (tests)
_memory_conn: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    global _memory_conn
    if DB_PATH == ":memory:":
        if _memory_conn is None:
            _memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            _memory_conn.row_factory = sqlite3.Row
        return _memory_conn
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def reset_memory_db() -> None:
    """Recria o banco em memória – usado entre testes para isolar estado."""
    global _memory_conn
    if DB_PATH == ":memory:" and _memory_conn is not None:
        _memory_conn.close()
        _memory_conn = None


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT    NOT NULL,
                email       TEXT    NOT NULL UNIQUE,
                tipo_solicitacao TEXT NOT NULL,
                valor_patrimonio REAL NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'Aguardando Análise',
                prioridade  TEXT,
                pipefy_card_id TEXT,
                criado_em   TEXT    NOT NULL DEFAULT (datetime('now')),
                atualizado_em TEXT
            );

            CREATE TABLE IF NOT EXISTS eventos_processados (
                event_id    TEXT    PRIMARY KEY,
                processado_em TEXT  NOT NULL DEFAULT (datetime('now'))
            );
            """
        )