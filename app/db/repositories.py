from typing import Optional
from app.db.database import get_connection


def create_cliente(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO clientes (nome, email, tipo_solicitacao, valor_patrimonio)
            VALUES (?, ?, ?, ?)
            """,
            (nome, email, tipo_solicitacao, valor_patrimonio),
        )
        conn.commit()
        return get_cliente_by_id(cursor.lastrowid)


def get_cliente_by_id(cliente_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        return dict(row) if row else None


def get_cliente_by_email(email: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clientes WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def update_cliente_status_prioridade(
    email: str,
    status: str,
    prioridade: str,
) -> Optional[dict]:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE clientes
            SET status = ?,
                prioridade = ?,
                atualizado_em = datetime('now')
            WHERE email = ?
            """,
            (status, prioridade, email),
        )
        conn.commit()
        return get_cliente_by_email(email)


def evento_ja_processado(event_id: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM eventos_processados WHERE event_id = ?", (event_id,)
        ).fetchone()
        return row is not None


def registrar_evento(event_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO eventos_processados (event_id) VALUES (?)", (event_id,)
        )
        conn.commit()