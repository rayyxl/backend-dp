from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path("", views.ia_view, name="ia"),
    path("api/conversas/", views.conversations_collection, name="conversations_collection"),
    path("api/conversas/<uuid:conversation_id>/", views.conversation_detail, name="conversation_detail"),
    path(
        "api/conversas/<uuid:conversation_id>/mensagens/",
        views.conversation_messages,
        name="conversation_messages",
    ),
    path("api/perguntar/", views.ask_assistant, name="ask_assistant"),
]
