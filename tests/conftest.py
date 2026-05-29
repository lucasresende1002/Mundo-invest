import os
import sys

os.environ["DB_PATH"] = ":memory:"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import reset_memory_db, init_db  # noqa: E402
from app.main import app as flask_app  # noqa: E402

flask_app.config["TESTING"] = True

# ── Payloads reutilizáveis ───────────────────────────────────────────────────

CLIENTE_ALTO_PATRIMONIO = {
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250_000,
}

CLIENTE_BAIXO_PATRIMONIO = {
    "cliente_nome": "Maria Souza",
    "cliente_email": "maria.souza@example.com",
    "tipo_solicitacao": "Abertura de conta",
    "valor_patrimonio": 100_000,
}

CLIENTE_LIMITE_EXATO = {
    "cliente_nome": "Carlos Lima",
    "cliente_email": "carlos.lima@example.com",
    "tipo_solicitacao": "Portabilidade",
    "valor_patrimonio": 200_000,
}


def fresh_db():
    """Reseta e recria o schema; chamar no setUp de cada TestCase."""
    reset_memory_db()
    init_db()