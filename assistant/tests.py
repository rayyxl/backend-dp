import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from google.genai import errors as genai_errors

from accounts.models import User
from .models import Conversation, Message


def _fake_response(text: str):
    response = MagicMock()
    response.text = text
    return response


def _client_error(code: int, message: str) -> genai_errors.ClientError:
    return genai_errors.ClientError(code=code, response_json={"error": {"message": message}})


@override_settings(GEMINI_API_KEY="fake-key-for-tests", GEMINI_MODEL="gemini-3.6-flash")
class AssistantChatTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email="a@teste.com", password="senha123", nome="Usuário A")
        self.user_b = User.objects.create_user(email="b@teste.com", password="senha123", nome="Usuário B")

    def _login(self, client, email):
        client.post("/", {"email": email, "password": "senha123"})

    def _post_json(self, client, url, payload):
        return client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_anonymous_cannot_reach_chat_endpoints(self):
        response = self.client.get("/ia/api/conversas/")
        self.assertEqual(response.status_code, 302)

    def test_create_and_list_conversation(self):
        self._login(self.client, "a@teste.com")
        response = self.client.post("/ia/api/conversas/")
        self.assertEqual(response.status_code, 201)
        conv_id = response.json()["id"]

        response = self.client.get("/ia/api/conversas/")
        ids = [c["id"] for c in response.json()["conversations"]]
        self.assertIn(conv_id, ids)

    def test_ask_uses_official_sdk_and_persists_messages(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.return_value = _fake_response(
                "Uma API é uma interface que permite a comunicação entre sistemas."
            )
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "O que é uma API?"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("interface", response.json()["answer"])

            call_kwargs = instance.models.generate_content.call_args.kwargs
            # O contexto acadêmico vai em system_instruction (não em uma
            # mensagem de papel "system", que não existe na Gemini API).
            self.assertIn("UNIPÊ", call_kwargs["config"].system_instruction)
            self.assertEqual(call_kwargs["model"], "gemini-3.6-flash")

        messages = Message.objects.filter(conversation_id=conv_id).order_by("created_at")
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")

    def test_history_sent_on_second_question_with_correct_roles(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.return_value = _fake_response("Primeira resposta.")
            self._post_json(self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "Pergunta 1"})

            instance.models.generate_content.return_value = _fake_response("Segunda resposta.")
            self._post_json(self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "Pergunta 2"})

            call_kwargs = instance.models.generate_content.call_args.kwargs
            contents = call_kwargs["contents"]
            # (pergunta 1 + resposta 1) + pergunta 2 nova = 3 turnos
            # (o system_instruction não entra em "contents" na Gemini API).
            self.assertEqual(len(contents), 3)
            self.assertEqual(contents[0].role, "user")
            self.assertEqual(contents[1].role, "model")  # papel do assistente na Gemini API
            self.assertEqual(contents[2].role, "user")

    def test_rate_limit_error_returns_friendly_message(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.side_effect = _client_error(429, "Resource exhausted")
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "teste"}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Muitas perguntas", response.json()["error"])

    def test_authentication_error_returns_friendly_message_without_key(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.side_effect = _client_error(401, "Invalid API key")
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "teste"}
            )
            self.assertEqual(response.status_code, 400)
            body = response.json()
            self.assertNotIn("fake-key-for-tests", json.dumps(body))
            self.assertIn("indisponível", body["error"])

    def test_server_error_returns_friendly_message(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.side_effect = genai_errors.ServerError(
                code=500, response_json={"error": {"message": "internal error"}}
            )
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "teste"}
            )
            self.assertEqual(response.status_code, 400)

    def test_empty_response_falls_back_to_friendly_message(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        with patch("assistant.services.genai.Client") as mock_client_cls:
            instance = mock_client_cls.return_value
            instance.models.generate_content.return_value = _fake_response(None)
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "teste"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("Não consegui gerar", response.json()["answer"])

    def test_user_cannot_read_another_users_conversation(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        other_client = self.client_class()
        self._login(other_client, "b@teste.com")

        response = other_client.get(f"/ia/api/conversas/{conv_id}/mensagens/")
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_users_conversation(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        other_client = self.client_class()
        self._login(other_client, "b@teste.com")

        response = other_client.delete(f"/ia/api/conversas/{conv_id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Conversation.objects.filter(id=conv_id).exists())

    def test_user_cannot_ask_in_another_users_conversation(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]

        other_client = self.client_class()
        self._login(other_client, "b@teste.com")

        response = self._post_json(
            other_client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "invasão"}
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_own_conversation(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]
        response = self.client.delete(f"/ia/api/conversas/{conv_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Conversation.objects.filter(id=conv_id).exists())

    def test_ask_without_api_key_returns_friendly_error(self):
        self._login(self.client, "a@teste.com")
        conv_id = self.client.post("/ia/api/conversas/").json()["id"]
        with override_settings(GEMINI_API_KEY=""):
            response = self._post_json(
                self.client, "/ia/api/perguntar/", {"conversationId": conv_id, "question": "teste"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("fake-key-for-tests", response.json()["error"])
