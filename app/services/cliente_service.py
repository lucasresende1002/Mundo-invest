"""
Serviço de Clientes
===================
Orquestra a persistência local e a integração (simulada) com o Pipefy.
"""

import logging
from typing import Optional

from app.db import repositories as repo
from app.services import pipefy_client as pipefy

logger = logging.getLogger(__name__)

LIMITE_PRIORIDADE_ALTA = 200_000.0


def calcular_prioridade(valor_patrimonio: float) -> str:
    """Retorna 'prioridade_alta' ou 'prioridade_normal' conforme regra de negócio."""
    if valor_patrimonio >= LIMITE_PRIORIDADE_ALTA:
        return "prioridade_alta"
    return "prioridade_normal"


def criar_cliente(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> dict:
    """
    1. Persiste o cliente com status 'Aguardando Análise'.
    2. Simula criação do card no Pipefy via GraphQL.
    3. Salva o pipefy_card_id retornado.
    """
    # Salva no banco local
    cliente = repo.create_cliente(nome, email, tipo_solicitacao, valor_patrimonio)

    # Envia (simulado) para o Pipefy
    card_id = pipefy.simulate_create_card(nome, email, tipo_solicitacao, valor_patrimonio)

    # Persiste o card_id recebido do Pipefy
    if card_id:
        from app.db.database import get_connection

        with get_connection() as conn:
            conn.execute(
                "UPDATE clientes SET pipefy_card_id = ? WHERE id = ?",
                (card_id, cliente["id"]),
            )
            conn.commit()
        cliente["pipefy_card_id"] = card_id

    logger.info("Cliente criado: id=%s email=%s card_id=%s", cliente["id"], email, card_id)
    return cliente


def processar_webhook_card_updated(
    event_id: str,
    card_id: str,
    cliente_email: str,
) -> Optional[dict]:
    """
    1. Garante idempotência verificando event_id.
    2. Busca cliente e calcula prioridade.
    3. Simula atualização de campos no Pipefy.
    4. Persiste novo status e prioridade no banco local.
    """
    # Idempotência
    if repo.evento_ja_processado(event_id):
        logger.warning("Evento duplicado ignorado: %s", event_id)
        return None

    # Busca cliente
    cliente = repo.get_cliente_by_email(cliente_email)
    if not cliente:
        raise ValueError(f"Cliente não encontrado para o e-mail: {cliente_email}")

    # Calcula prioridade
    prioridade = calcular_prioridade(cliente["valor_patrimonio"])
    novo_status = "Processado"

    # Simula envio ao Pipefy
    pipefy_card_id = cliente.get("pipefy_card_id") or card_id
    pipefy.simulate_update_card_status_and_priority(pipefy_card_id, novo_status, prioridade)

    # Persiste no banco local
    cliente_atualizado = repo.update_cliente_status_prioridade(
        cliente_email, novo_status, prioridade
    )

    # Registra o evento para idempotência futura
    repo.registrar_evento(event_id)

    logger.info(
        "Webhook processado: event_id=%s email=%s prioridade=%s",
        event_id,
        cliente_email,
        prioridade,
    )
    return cliente_atualizado