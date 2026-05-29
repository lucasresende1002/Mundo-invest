import re
from flask import Blueprint, request, jsonify

from app.services import cliente_service as svc

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_webhook_payload(data: dict) -> list[str]:
    errors = []
    for field in ("event_id", "card_id", "cliente_email", "timestamp"):
        if field not in data:
            errors.append(f"Campo obrigatório ausente: '{field}'.")
    if errors:
        return errors

    for field in ("event_id", "card_id"):
        if not str(data[field]).strip():
            errors.append(f"'{field}' não pode ser vazio.")
    if not EMAIL_RE.match(str(data["cliente_email"])):
        errors.append("'cliente_email' não é um e-mail válido.")
    return errors


@webhooks_bp.post("/pipefy/card-updated")
def card_updated():
    data = request.get_json(silent=True) or {}

    errors = _validate_webhook_payload(data)
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        cliente = svc.processar_webhook_card_updated(
            event_id=str(data["event_id"]).strip(),
            card_id=str(data["card_id"]).strip(),
            cliente_email=str(data["cliente_email"]).strip().lower(),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    if cliente is None:
        return jsonify({
            "message": "Evento já processado anteriormente (idempotência).",
            "event_id": data["event_id"],
            "cliente": None,
        }), 200

    return jsonify({
        "message": "Evento processado com sucesso.",
        "event_id": data["event_id"],
        "cliente": cliente,
    }), 200