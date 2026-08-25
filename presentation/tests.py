from django.test import TestCase

from accounts.models import User

PROTECTED_URLS = [
    "/apresentacao/",
    "/conceito/",
    "/conceitos/",
    "/competencias/",
    "/porta-de-entrada/",
    "/brasil/",
    "/surpreendeu/",
]


class ProtectedPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="conteudo@teste.com", password="senha123", nome="Leitor")

    def test_all_content_pages_redirect_when_anonymous(self):
        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)

    def test_all_content_pages_load_when_authenticated(self):
        self.client.post("/", {"email": "conteudo@teste.com", "password": "senha123"})
        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_academic_content_present_and_unaltered(self):
        self.client.post("/", {"email": "conteudo@teste.com", "password": "senha123"})

        response = self.client.get("/apresentacao/")
        self.assertContains(response, "Rai Soares da Silva")
        self.assertContains(response, "Francisco Ribeiro Dos Santos Junior")

        response = self.client.get("/brasil/")
        self.assertContains(response, "Brasscom")
        self.assertContains(response, "252.903")  # nº de empregos CLT da 1ª ocupação do relatório

        response = self.client.get("/conceitos/")
        self.assertContains(response, "Servidor")
        self.assertContains(response, "Autenticação e autorização")

    def test_sidebar_active_item_matches_current_page(self):
        self.client.post("/", {"email": "conteudo@teste.com", "password": "senha123"})
        response = self.client.get("/brasil/")
        self.assertContains(response, "A área no Brasil")

    def test_404_page_for_unknown_route(self):
        self.client.post("/", {"email": "conteudo@teste.com", "password": "senha123"})
        response = self.client.get("/rota-que-nao-existe/")
        self.assertEqual(response.status_code, 404)
