import json
import re
from unittest.mock import MagicMock, patch

import brevo
from django.test import TestCase, override_settings

from .models import PasswordResetCode, User


class SignupLoginLogoutTests(TestCase):
    def test_signup_creates_user_with_hashed_password(self):
        response = self.client.post(
            "/cadastro/",
            {"nome": "Maria Teste", "email": "maria@teste.com", "password": "senha123", "confirm": "senha123"},
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="maria@teste.com")
        self.assertEqual(user.nome, "Maria Teste")
        self.assertNotEqual(user.password, "senha123")
        self.assertTrue(user.check_password("senha123"))

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(email="dup@teste.com", password="senha123", nome="Já existe")
        response = self.client.post(
            "/cadastro/",
            {"nome": "Outro", "email": "dup@teste.com", "password": "senha123", "confirm": "senha123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está cadastrado.")

    def test_signup_rejects_short_password(self):
        response = self.client.post(
            "/cadastro/",
            {"nome": "Teste", "email": "curta@teste.com", "password": "123", "confirm": "123"},
        )
        self.assertContains(response, "A senha deve ter no mínimo 6 caracteres.")

    def test_login_wrong_password_message(self):
        User.objects.create_user(email="joao@teste.com", password="correta123", nome="Joao")
        response = self.client.post("/", {"email": "joao@teste.com", "password": "errada"})
        self.assertContains(response, "Senha incorreta. Verifique e tente novamente.")

    def test_login_unknown_email_message(self):
        response = self.client.post("/", {"email": "naoexiste@teste.com", "password": "qualquer"})
        self.assertContains(response, "Não encontramos uma conta com este e-mail.")

    def test_login_success_redirects_to_apresentacao(self):
        User.objects.create_user(email="ok@teste.com", password="senha123", nome="OK")
        response = self.client.post("/", {"email": "ok@teste.com", "password": "senha123"})
        self.assertRedirects(response, "/apresentacao/")

    def test_protected_page_redirects_when_anonymous(self):
        response = self.client.get("/apresentacao/")
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_to_login_and_ends_session(self):
        User.objects.create_user(email="out@teste.com", password="senha123", nome="Out")
        self.client.post("/", {"email": "out@teste.com", "password": "senha123"})
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/")
        response = self.client.get("/apresentacao/")
        self.assertEqual(response.status_code, 302)


@override_settings(BREVO_API_KEY="fake-key-for-tests", BREVO_SENDER_EMAIL="no-reply@teste.com")
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="recuperar@teste.com", password="senhaAntiga1", nome="Recuperar")

    def _post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_request_code_for_unknown_email_never_reveals_and_never_leaks_code(self):
        response = self._post_json("/recuperar-senha/solicitar-codigo/", {"email": "fantasma@teste.com"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertNotIn("code", json.dumps(body))
        self.assertIn("Se o e-mail estiver cadastrado", body["message"])
        # Nenhum código deve ter sido criado no banco para um e-mail inexistente.
        self.assertFalse(PasswordResetCode.objects.filter(email="fantasma@teste.com").exists())

    def test_full_reset_flow_never_exposes_code_and_stores_only_hash(self):
        with patch("accounts.emailing.brevo.Brevo") as mock_brevo_cls:
            instance = mock_brevo_cls.return_value
            instance.transactional_emails.send_transac_email.return_value = MagicMock(message_id="ok")

            response = self._post_json("/recuperar-senha/solicitar-codigo/", {"email": "recuperar@teste.com"})
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertNotIn("code", json.dumps(body))

            # O código real só existe no corpo do e-mail "enviado" (mock) — nunca na resposta HTTP.
            html_sent = instance.transactional_emails.send_transac_email.call_args.kwargs["html_content"]
            real_code = re.search(r">(\d{6})<", html_sent).group(1)

            # Confirma remetente/destinatário reais usados na chamada ao SDK oficial.
            call_kwargs = instance.transactional_emails.send_transac_email.call_args.kwargs
            self.assertEqual(call_kwargs["to"], [{"email": "recuperar@teste.com"}])
            self.assertEqual(call_kwargs["sender"]["email"], "no-reply@teste.com")

        # O banco armazena somente o hash — nunca o código em texto puro.
        record = PasswordResetCode.objects.get(email="recuperar@teste.com", used=False)
        self.assertNotIn(real_code, record.code_hash)
        self.assertEqual(len(record.code_hash), 64)  # SHA-256 hex digest

        # Etapa 2: validar o código.
        response = self._post_json(
            "/recuperar-senha/verificar-codigo/", {"email": "recuperar@teste.com", "code": real_code}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])

        # Etapa 3: redefinir a senha.
        response = self._post_json(
            "/recuperar-senha/redefinir/",
            {"email": "recuperar@teste.com", "code": real_code, "password": "senhaNova99"},
        )
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("senhaNova99"))
        self.assertFalse(self.user.check_password("senhaAntiga1"))

        # Código reutilizado deve falhar.
        response = self._post_json(
            "/recuperar-senha/verificar-codigo/", {"email": "recuperar@teste.com", "code": real_code}
        )
        self.assertEqual(response.status_code, 400)

    def test_brevo_failure_never_reports_false_success_and_self_invalidates_code(self):
        with patch("accounts.emailing.brevo.Brevo") as mock_brevo_cls:
            instance = mock_brevo_cls.return_value
            instance.transactional_emails.send_transac_email.side_effect = brevo.UnauthorizedError(
                body={"message": "invalid api key"}
            )
            response = self._post_json("/recuperar-senha/solicitar-codigo/", {"email": "recuperar@teste.com"})

        self.assertNotEqual(response.status_code, 200)
        body = response.json()
        self.assertNotIn("code", json.dumps(body))

        record = PasswordResetCode.objects.filter(email="recuperar@teste.com").order_by("-created_at").first()
        self.assertIsNotNone(record)
        self.assertTrue(record.used)  # autoinvalidado, nunca foi entregue

    @override_settings(BREVO_API_KEY="", BREVO_SENDER_EMAIL="")
    def test_request_code_without_brevo_configured_returns_real_error(self):
        response = self._post_json("/recuperar-senha/solicitar-codigo/", {"email": "recuperar@teste.com"})
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn("code", json.dumps(response.json()))

    def test_invalid_email_format_rejected(self):
        response = self._post_json("/recuperar-senha/solicitar-codigo/", {"email": "nao-e-email"})
        self.assertEqual(response.status_code, 400)
