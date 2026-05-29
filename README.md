# Mundo Invest – API de Gestão de Clientes e Pipefy

API interna em Python/Flask para gerenciamento de clientes e seus patrimônios investidos, com integração simulada ao Pipefy via GraphQL seguindo a especificação oficial da plataforma.

---

# Sumário

1. Tecnologias
2. Funcionalidades Implementadas
3. Estrutura do Projeto
4. Execução Local
5. Executando os Testes
6. Exemplos de Requisição (curl)
7. Status HTTP Utilizados
8. Mapeamento GraphQL com o Pipefy
9. Visão de Produção na AWS

---

# Tecnologias

* Python 3.12
* Flask – framework web
* SQLite – persistência local
* pytest – testes automatizados
* Docker – empacotamento opcional
* Pydantic – validação de payloads
* GraphQL – integração simulada com Pipefy

---

# Funcionalidades Implementadas

* Cadastro de clientes
* Persistência em SQLite
* Validação de payload
* Simulação de integração Pipefy via GraphQL
* Processamento de webhook
* Regra de prioridade baseada em patrimônio
* Idempotência por `event_id`
* Testes automatizados
* Arquitetura em camadas
* Separação entre API, Services e Repositories

---

# Estrutura do Projeto

```txt
mundo-invest/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── clientes.py
│   │   └── webhooks.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── repositories.py
│   │
│   ├── services/
│   │   ├── cliente_service.py
│   │   └── pipefy_client.py
│   │
│   └── schemas/
│       └── schemas.py
│
├── tests/
│   ├── conftest.py
│   ├── test_cliente.py
│   ├── test_webhook.py
│   └── test_pipefy_client.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── mundo_invest.db
└── README.md
```

---

# Execução Local

## Pré-requisitos

* Python 3.12+
* pip

---

## 1. Clone o repositório

```bash
git clone <repo-url>
cd mundo-invest
```

---

## 2. Crie o ambiente virtual

### Windows

```bash
python -m venv .venv
```

---

## 3. Ative o ambiente virtual

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### CMD

```bash
.venv\Scripts\activate
```

---

## 4. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 5. Execute a aplicação

```bash
python -m app.main
```

A API ficará disponível em:

```txt
http://localhost:8000
```

---

# Executando os Testes

Execute:

```bash
pytest -v
```

Saída esperada:

```txt
===================== test session starts =====================

tests/test_cliente.py .....
tests/test_webhook.py .....
tests/test_pipefy_client.py .....

===================== 21 passed =====================
```

---

# Cobertura dos Testes

| Cenário                     | Arquivo                 |
| --------------------------- | ----------------------- |
| Criação de cliente          | `test_cliente.py`       |
| Validação de payload        | `test_cliente.py`       |
| Regra de prioridade alta    | `test_webhook.py`       |
| Regra de prioridade normal  | `test_webhook.py`       |
| Idempotência por `event_id` | `test_webhook.py`       |
| Estrutura GraphQL Pipefy    | `test_pipefy_client.py` |

---

# Exemplos de Requisição (curl)

## Fluxo 1 – Criar Cliente

### PowerShell

```powershell
curl -Method POST http://127.0.0.1:8000/clientes `
-Headers @{"Content-Type"="application/json"} `
-Body '{"cliente_nome":"Joao Silva","cliente_email":"joao@email.com","tipo_solicitacao":"Atualizacao cadastral","valor_patrimonio":250000}'
```

---

## Resposta esperada

```json
{
  "message": "Cliente criado com sucesso.",
  "cliente": {
    "id": 1,
    "nome": "Joao Silva",
    "email": "joao@email.com",
    "tipo_solicitacao": "Atualizacao cadastral",
    "valor_patrimonio": 250000.0,
    "status": "Aguardando Análise",
    "prioridade": null
  }
}
```

---

# Fluxo 2 – Webhook Pipefy

```powershell
curl -Method POST http://127.0.0.1:8000/webhooks/pipefy/card-updated `
-Headers @{"Content-Type"="application/json"} `
-Body '{"event_id":"evt_1","card_id":"card_1","cliente_email":"joao@email.com","timestamp":"2026-05-18T12:00:00Z"}'
```

---

# Resposta esperada

```json
{
  "message": "Evento processado com sucesso.",
  "event_id": "evt_1",
  "cliente": {
    "status": "Processado",
    "prioridade": "prioridade_alta"
  }
}
```

---

# Teste de Idempotência

Reenvio do mesmo `event_id`:

```json
{
  "message": "Evento já processado anteriormente (idempotência).",
  "event_id": "evt_1",
  "cliente": null
}
```

---

# Status HTTP Utilizados

| Status | Descrição                           |
| ------ | ----------------------------------- |
| 200    | Processamento realizado com sucesso |
| 201    | Cliente criado com sucesso          |
| 404    | Cliente não encontrado              |
| 422    | Payload inválido                    |

---

# Mapeamento GraphQL com o Pipefy

As mutations seguem a estrutura oficial da documentação pública do Pipefy.

---

# Mutation – createCard

```graphql
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
    }
  }
}
```

---

# Variáveis enviadas

```json
{
  "input": {
    "pipe_id": "302000001",
    "title": "Joao Silva",
    "fields_attributes": [
      {
        "field_id": "email_cliente",
        "field_value": "joao@email.com"
      },
      {
        "field_id": "valor_patrimonio",
        "field_value": "250000"
      }
    ]
  }
}
```

---

# Mutation – updateCardField

```graphql
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    card {
      id
    }
  }
}
```

---

# Atualização de prioridade

```json
{
  "input": {
    "card_id": "card_1",
    "field_id": "prioridade_cliente",
    "new_value": "prioridade_alta"
  }
}
```

---

# Atualização de status

```json
{
  "input": {
    "card_id": "card_1",
    "field_id": "status_cliente",
    "new_value": "Processado"
  }
}
```

---

# Visão de Produção na AWS

## Arquitetura Proposta

```txt
Cliente / Pipefy
      │
      ▼
 API Gateway
      │
      ▼
 AWS Lambda
      │
      ├── RDS PostgreSQL
      ├── DynamoDB
      ├── SQS
      └── Pipefy GraphQL API
```

---

# Serviços AWS Utilizados

## API Gateway

Responsável por expor os endpoints HTTP da aplicação.

---

## AWS Lambda

Cada endpoint pode ser executado como uma função serverless independente.

---

## RDS PostgreSQL

Persistência principal da aplicação em ambiente produtivo.

---

## DynamoDB

Utilizado para controle de idempotência via `event_id`.

---

## SQS

Processamento assíncrono de webhooks em alta escala.

---

## Secrets Manager

Armazenamento seguro de tokens e credenciais.

---

## CloudWatch + X-Ray

Monitoramento, logs estruturados e rastreamento distribuído.

---

# Escalabilidade

A arquitetura proposta suporta:

* processamento concorrente
* alta disponibilidade
* desacoplamento de webhooks
* proteção contra eventos duplicados
* escalabilidade horizontal automática

A utilização do DynamoDB para idempotência evita race conditions em cenários de alta concorrência, garantindo processamento único por `event_id`.

---

# Considerações Finais

O projeto foi desenvolvido seguindo boas práticas de arquitetura backend:

* separação em camadas
* validação de entrada
* regras de negócio desacopladas
* persistência isolada
* testes automatizados
* integração externa simulada
* idempotência de webhooks

A aplicação está preparada para evolução futura para ambientes cloud-native e integrações reais com o Pipefy.
