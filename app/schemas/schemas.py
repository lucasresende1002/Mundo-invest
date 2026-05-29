from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


# ── Clientes ──────────────────────────────────────────────────────────────────

class ClienteCreateRequest(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: float

    @field_validator("cliente_nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("cliente_nome não pode ser vazio.")
        return v.strip()

    @field_validator("tipo_solicitacao")
    @classmethod
    def tipo_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("tipo_solicitacao não pode ser vazio.")
        return v.strip()

    @field_validator("valor_patrimonio")
    @classmethod
    def patrimonio_positivo(cls, v: float) -> float:
        if v < 0:
            raise ValueError("valor_patrimonio não pode ser negativo.")
        return v


class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str
    prioridade: Optional[str]
    pipefy_card_id: Optional[str]
    criado_em: str
    atualizado_em: Optional[str]


# ── Webhooks ───────────────────────────────────────────────────────────────────

class CardUpdatedWebhookRequest(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: str

    @field_validator("event_id", "card_id")
    @classmethod
    def nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Campo não pode ser vazio.")
        return v.strip()


class WebhookResponse(BaseModel):
    message: str
    event_id: str
    cliente: Optional[ClienteResponse] = None