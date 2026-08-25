from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação e recuperação de senha (mesmas rotas de topo do projeto
    # original: "/", "/cadastro", "/recuperar-senha").
    path("", include("accounts.urls")),
    # Páginas de conteúdo protegidas (mesmas rotas de topo do original:
    # "/apresentacao", "/conceito", "/conceitos", "/competencias",
    # "/porta-de-entrada", "/brasil", "/surpreendeu").
    path("", include("presentation.urls")),
    # Assistente de IA ("/ia" e os endpoints JSON do chat).
    path("ia/", include("assistant.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
