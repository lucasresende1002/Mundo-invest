"""
Testes – Fluxo 2: Webhook de Atualização de Card
"""
import unittest
import json
import os

os.environ["DB_PATH"] = ":memory:"

from tests.conftest import (
    flask_app, fresh_db,
    CLIENTE_ALTO_PATRIMONIO,
    CLIENTE_BAIXO_PATRIMONIO,
    CLIENTE_LIMITE_EXATO,
)


class TestWebhookCardUpdated(unittest.TestCase):

    def setUp(self):
        flask_app.config["TESTING"] = True
        self.client = flask_app.test_client()
        fresh_db()

    def _criar_cliente(self, payload):
        resp = self.client.post("/clientes", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        return resp.get_json()

    def _webhook(self, event_id, card_id, email):
        return self.client.post(
            "/webhooks/pipefy/card-updated",
            data=json.dumps({
                "event_id": event_id,
                "card_id": card_id,
                "cliente_email": email,
                "timestamp": "2026-05-18T12:00:00Z",
            }),
            content_type="application/json",
        )

    # ── Regra de prioridade ────────────────────────────────────────────────

    def test_prioridade_alta_patrimonio_acima_limite(self):
        """250.000 → prioridade_alta."""
        self._criar_cliente(CLIENTE_ALTO_PATRIMONIO)
        resp = self._webhook("evt_001", "card_001", "joao.silva@example.com")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["cliente"]["prioridade"], "prioridade_alta")
        self.assertEqual(data["cliente"]["status"], "Processado")

    def test_prioridade_normal_patrimonio_abaixo_limite(self):
        """100.000 → prioridade_normal."""
        self._criar_cliente(CLIENTE_BAIXO_PATRIMONIO)
        resp = self._webhook("evt_002", "card_002", "maria.souza@example.com")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["cliente"]["prioridade"], "prioridade_normal")
        self.assertEqual(data["cliente"]["status"], "Processado")

    def test_prioridade_alta_patrimonio_igual_ao_limite(self):
        """200.000 exato → prioridade_alta (borda do >=)."""
        self._criar_cliente(CLIENTE_LIMITE_EXATO)
        resp = self._webhook("evt_003", "card_003", "carlos.lima@example.com")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["cliente"]["prioridade"], "prioridade_alta")

    def test_status_atualizado_para_processado(self):
        """Status deve mudar de 'Aguardando Análise' para 'Processado'."""
        self._criar_cliente(CLIENTE_ALTO_PATRIMONIO)
        from app.db.repositories import get_cliente_by_email
        self.assertEqual(get_cliente_by_email("joao.silva@example.com")["status"], "Aguardando Análise")
        self._webhook("evt_004", "card_004", "joao.silva@example.com")
        self.assertEqual(get_cliente_by_email("joao.silva@example.com")["status"], "Processado")

    # ── Idempotência ───────────────────────────────────────────────────────

    def test_bloqueia_evento_duplicado(self):
        """Mesmo event_id processado duas vezes deve ser ignorado na segunda."""
        self._criar_cliente(CLIENTE_ALTO_PATRIMONIO)
        r1 = self._webhook("evt_idem_001", "card_001", "joao.silva@example.com")
        r2 = self._webhook("evt_idem_001", "card_001", "joao.silva@example.com")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertIn("já processado", r2.get_json()["message"].lower())
        self.assertIsNone(r2.get_json()["cliente"])

    def test_banco_inalterado_em_evento_duplicado(self):
        """Banco local não deve ser alterado no reprocessamento de evento já registrado."""
        self._criar_cliente(CLIENTE_ALTO_PATRIMONIO)
        self._webhook("evt_idem_002", "card_001", "joao.silva@example.com")
        from app.db.repositories import get_cliente_by_email
        after_first = get_cliente_by_email("joao.silva@example.com")
        self._webhook("evt_idem_002", "card_001", "joao.silva@example.com")
        after_second = get_cliente_by_email("joao.silva@example.com")
        self.assertEqual(after_first["atualizado_em"], after_second["atualizado_em"])

    def test_diferentes_event_ids_sao_processados(self):
        """Dois event_ids distintos para o mesmo cliente devem ser ambos processados."""
        self._criar_cliente(CLIENTE_ALTO_PATRIMONIO)
        r1 = self._webhook("evt_a", "card_001", "joao.silva@example.com")
        r2 = self._webhook("evt_b", "card_001", "joao.silva@example.com")
        self.assertIsNotNone(r1.get_json()["cliente"])
        self.assertIsNotNone(r2.get_json()["cliente"])

    # ── Erros ──────────────────────────────────────────────────────────────

    def test_retorna_404_para_cliente_inexistente(self):
        resp = self._webhook("evt_999", "card_999", "nao_existe@example.com")
        self.assertEqual(resp.status_code, 404)

    def test_rejeita_payload_sem_event_id(self):
        resp = self.client.post(
            "/webhooks/pipefy/card-updated",
            data=json.dumps({
                "card_id": "card_001",
                "cliente_email": "joao@example.com",
                "timestamp": "2026-05-18T12:00:00Z",
            }),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)


if __name__ == "__main__":
    unittest.main()