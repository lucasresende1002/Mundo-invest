import re
from flask import Blueprint, request, jsonify

from app.db import repositories as repo
from app.services import cliente_service as svc

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_payload(data: dict) -> list[str]:
    errors = []
    for field in ("cliente_nome", "cliente_email", "tipo_solicitacao", "valor_patrimonio"):
        if field not in data:
            errors.append(f"Campo obrigatório ausente: '{field}'.")
    if errors:
        return errors

    if not str(data["cliente_nome"]).strip():
        errors.append("'cliente_nome' não pode ser vazio.")
    if not str(data["tipo_solicitacao"]).strip():
        errors.append("'tipo_solicitacao' não pode ser vazio.")
    if not EMAIL_RE.match(str(data["cliente_email"])):
        errors.append("'cliente_email' não é um e-mail válido.")
    try:
        patrimonio = float(data["valor_patrimonio"])
        if patrimonio < 0:
            errors.append("'valor_patrimonio' não pode ser negativo.")
    except (TypeError, ValueError):
        errors.append("'valor_patrimonio' deve ser um número.")
    return errors


@clientes_bp.post("")
def criar_cliente():
    data = request.get_json(silent=True) or {}

    errors = _validate_payload(data)
    if errors:
        return jsonify({"errors": errors}), 422

    email = str(data["cliente_email"]).strip().lower()
    if repo.get_cliente_by_email(email):
        return jsonify({"error": f"Já existe um cliente com o e-mail '{email}'."}), 409

    cliente = svc.criar_cliente(
        nome=str(data["cliente_nome"]).strip(),
        email=email,
        tipo_solicitacao=str(data["tipo_solicitacao"]).strip(),
        valor_patrimonio=float(data["valor_patrimonio"]),
    )
    return jsonify(cliente), 201