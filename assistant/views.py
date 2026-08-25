import json
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Conversation, Message
from .services import AssistantError, ask_ai


def _json_body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


@login_required
def ia_view(request):
    return render(request, "assistant/ia.html")


@login_required
@require_http_methods(["GET", "POST"])
def conversations_collection(request):
    if request.method == "GET":
        conversations = Conversation.objects.filter(user=request.user).order_by("-updated_at")
        data = [
            {
                "id": str(c.id),
                "title": c.title,
                "createdAt": c.created_at.isoformat(),
                "updatedAt": c.updated_at.isoformat(),
            }
            for c in conversations
        ]
        return JsonResponse({"conversations": data})

    # POST — cria uma nova conversa vazia
    conversation = Conversation.objects.create(user=request.user, title="Nova conversa")
    return JsonResponse(
        {
            "id": str(conversation.id),
            "title": conversation.title,
            "createdAt": conversation.created_at.isoformat(),
            "updatedAt": conversation.updated_at.isoformat(),
        },
        status=201,
    )


@login_required
@require_http_methods(["DELETE"])
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    return JsonResponse({"ok": True})


@login_required
@require_http_methods(["GET"])
def conversation_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = conversation.messages.order_by("created_at")
    data = [
        {"id": str(m.id), "role": m.role, "content": m.content, "createdAt": m.created_at.isoformat()}
        for m in messages
    ]
    return JsonResponse({"messages": data})


@login_required
@require_http_methods(["POST"])
def ask_assistant(request):
    data = _json_body(request)
    conversation_id = data.get("conversationId")
    question = (data.get("question") or "").strip()

    try:
        uuid.UUID(str(conversation_id))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Conversa não encontrada."}, status=404)

    if not question or len(question) > 4000:
        return JsonResponse({"error": "Pergunta inválida."}, status=400)

    conversation = Conversation.objects.filter(id=conversation_id, user=request.user).first()
    if conversation is None:
        return JsonResponse({"error": "Conversa não encontrada."}, status=404)

    history_qs = conversation.messages.order_by("created_at")[: settings.AI_CONVERSATION_HISTORY_LIMIT]
    history = [{"role": m.role, "content": m.content} for m in history_qs]
    is_first_question = len(history) == 0

    Message.objects.create(conversation=conversation, role=Message.Role.USER, content=question)

    try:
        answer = ask_ai(history, question)
    except AssistantError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    Message.objects.create(conversation=conversation, role=Message.Role.ASSISTANT, content=answer)

    if is_first_question:
        max_len = settings.AI_CONVERSATION_TITLE_MAX_LENGTH
        conversation.title = question[:max_len] + ("…" if len(question) > max_len else "")
    conversation.save(update_fields=["title", "updated_at"])

    return JsonResponse({"answer": answer, "title": conversation.title})
