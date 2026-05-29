import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

PIPEFY_API_URL = os.environ.get("PIPEFY_API_URL", "https://api.pipefy.com/graphql")
PIPEFY_API_TOKEN = os.environ.get("PIPEFY_API_TOKEN", "")

# ID do Pipe configurado no Pipefy (substituir em produção)
PIPE_ID = os.environ.get("PIPEFY_PIPE_ID", "302000001")

# IDs dos campos customizados do card no Pipefy (substituir em produção)
FIELD_ID_EMAIL = "email_cliente"
FIELD_ID_PATRIMONIO = "valor_patrimonio"
FIELD_ID_STATUS = "status_cliente"
FIELD_ID_PRIORIDADE = "prioridade_cliente"


CREATE_CARD_MUTATION = """
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
      current_phase {
        id
        name
      }
      fields {
        name
        value
      }
    }
  }
}
"""


def build_create_card_variables(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> dict:
    """
    Monta as variáveis para a mutation createCard conforme a spec do Pipefy.
    O campo `fields_attributes` recebe uma lista de objetos {field_id, field_value}.
    """
    return {
        "input": {
            "pipe_id": PIPE_ID,
            "title": f"{nome} – {tipo_solicitacao}",
            "fields_attributes": [
                {"field_id": FIELD_ID_EMAIL, "field_value": email},
                {
                    "field_id": FIELD_ID_PATRIMONIO,
                    "field_value": str(valor_patrimonio),
                },
            ],
        }
    }



UPDATE_CARD_FIELD_MUTATION = """
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    card {
      id
      title
      fields {
        name
        value
      }
    }
    clientMutationId
  }
}
"""


def build_update_card_field_variables(
    card_id: str,
    field_id: str,
    new_value: str,
) -> dict:
  
    return {
        "input": {
            "card_id": card_id,
            "field_id": field_id,
            "new_value": new_value,
        }
    }



def _log_graphql_payload(operation: str, mutation: str, variables: dict) -> None:
    payload = {"query": mutation.strip(), "variables": variables}
    logger.info(
        "[PIPEFY SIMULADO] %s\nPayload que seria enviado para %s:\n%s",
        operation,
        PIPEFY_API_URL,
        json.dumps(payload, ensure_ascii=False, indent=2),
    )


def simulate_create_card(
    nome: str,
    email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> Optional[str]:
    """
    Simula o envio da mutation createCard ao Pipefy.
    Retorna um card_id fictício para persistência local.

    Em produção, remova esta função e utilize send_create_card().
    """
    variables = build_create_card_variables(nome, email, tipo_solicitacao, valor_patrimonio)
    _log_graphql_payload("createCard", CREATE_CARD_MUTATION, variables)

    # Simula resposta do Pipefy
    fake_card_id = f"simulated_card_{abs(hash(email)) % 10_000_000}"
    logger.info("[PIPEFY SIMULADO] Card criado com id: %s", fake_card_id)
    return fake_card_id


def simulate_update_card_status_and_priority(
    card_id: str,
    novo_status: str,
    prioridade: str,
) -> None:
    """
    Simula o envio de duas mutations updateCardField ao Pipefy:
      1. Atualiza o campo de status.
      2. Atualiza o campo de prioridade.

    Em produção, remova esta função e utilize send_update_card_field().
    """
    # Atualiza status
    vars_status = build_update_card_field_variables(
        card_id, FIELD_ID_STATUS, novo_status
    )
    _log_graphql_payload(
        "updateCardField (status)", UPDATE_CARD_FIELD_MUTATION, vars_status
    )

    # Atualiza prioridade
    vars_prioridade = build_update_card_field_variables(
        card_id, FIELD_ID_PRIORIDADE, prioridade
    )
    _log_graphql_payload(
        "updateCardField (prioridade)", UPDATE_CARD_FIELD_MUTATION, vars_prioridade
    )

    logger.info(
        "[PIPEFY SIMULADO] Card %s atualizado: status=%s | prioridade=%s",
        card_id,
        novo_status,
        prioridade,
    )




async def send_graphql(mutation: str, variables: dict) -> Any:  # pragma: no cover
    """
    Stub de produção: envia a mutation GraphQL real para o Pipefy.
    Requer httpx instalado e PIPEFY_API_TOKEN configurado.
    """
    import httpx  # noqa: PLC0415

    headers = {
        "Authorization": f"Bearer {PIPEFY_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": mutation.strip(), "variables": variables}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(PIPEFY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()