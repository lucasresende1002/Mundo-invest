"""
Testes – Estrutura das Mutations GraphQL do Pipefy
"""
import json
import unittest

from app.services.pipefy_client import (
    CREATE_CARD_MUTATION,
    UPDATE_CARD_FIELD_MUTATION,
    build_create_card_variables,
    build_update_card_field_variables,
)


class TestCreateCardMutation(unittest.TestCase):

    def test_mutation_contem_operacao_correta(self):
        self.assertIn("mutation CreateCard", CREATE_CARD_MUTATION)
        self.assertIn("createCard(input: $input)", CREATE_CARD_MUTATION)

    def test_mutation_retorna_campos_esperados(self):
        self.assertIn("card {", CREATE_CARD_MUTATION)
        self.assertIn("id", CREATE_CARD_MUTATION)
        self.assertIn("current_phase", CREATE_CARD_MUTATION)
        self.assertIn("fields", CREATE_CARD_MUTATION)

    def test_variables_tem_pipe_id(self):
        v = build_create_card_variables("João", "joao@example.com", "Abertura", 300_000)
        self.assertIn("pipe_id", v["input"])
        self.assertIsNotNone(v["input"]["pipe_id"])

    def test_variables_tem_titulo(self):
        v = build_create_card_variables("João", "joao@example.com", "Abertura", 300_000)
        self.assertIn("title", v["input"])
        self.assertIn("João", v["input"]["title"])

    def test_variables_tem_fields_attributes(self):
        v = build_create_card_variables("João", "joao@example.com", "Abertura", 300_000)
        fields = v["input"]["fields_attributes"]
        self.assertIsInstance(fields, list)
        self.assertGreaterEqual(len(fields), 2)
        ids = {f["field_id"] for f in fields}
        self.assertIn("email_cliente", ids)
        self.assertIn("valor_patrimonio", ids)

    def test_variables_email_correto(self):
        v = build_create_card_variables("João", "joao@example.com", "Abertura", 300_000)
        field = next(f for f in v["input"]["fields_attributes"] if f["field_id"] == "email_cliente")
        self.assertEqual(field["field_value"], "joao@example.com")

    def test_variables_patrimonio_como_string(self):
        """Pipefy exige field_value como string."""
        v = build_create_card_variables("João", "joao@example.com", "Abertura", 300_000)
        field = next(f for f in v["input"]["fields_attributes"] if f["field_id"] == "valor_patrimonio")
        self.assertIsInstance(field["field_value"], str)


class TestUpdateCardFieldMutation(unittest.TestCase):

    def test_mutation_contem_operacao_correta(self):
        self.assertIn("mutation UpdateCardField", UPDATE_CARD_FIELD_MUTATION)
        self.assertIn("updateCardField(input: $input)", UPDATE_CARD_FIELD_MUTATION)

    def test_mutation_retorna_card_e_mutation_id(self):
        self.assertIn("card {", UPDATE_CARD_FIELD_MUTATION)
        self.assertIn("clientMutationId", UPDATE_CARD_FIELD_MUTATION)

    def test_variables_tem_campos_obrigatorios(self):
        v = build_update_card_field_variables("card_123", "status_cliente", "Processado")
        self.assertIn("card_id", v["input"])
        self.assertIn("field_id", v["input"])
        self.assertIn("new_value", v["input"])

    def test_variables_valores_corretos(self):
        v = build_update_card_field_variables("card_456", "prioridade_cliente", "prioridade_alta")
        self.assertEqual(v["input"]["card_id"], "card_456")
        self.assertEqual(v["input"]["field_id"], "prioridade_cliente")
        self.assertEqual(v["input"]["new_value"], "prioridade_alta")

    def test_payload_serializavel_em_json(self):
        v = build_update_card_field_variables("card_789", "status_cliente", "Processado")
        payload = {"query": UPDATE_CARD_FIELD_MUTATION, "variables": v}
        serialized = json.dumps(payload)
        self.assertIn("updateCardField", serialized)
        self.assertIn("card_789", serialized)


if __name__ == "__main__":
    unittest.main()