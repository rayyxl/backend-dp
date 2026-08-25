import hashlib
import json
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import emailing
from .models import PasswordResetCode, User
from .validators import is_valid_email, normalize_email


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("presentation:apresentacao")

    error = None
    email_value = ""

    if request.method == "POST":
        email_value = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        email = normalize_email(email_value)

        if not email or not password:
            error = "Preencha o e-mail e a senha."
        elif not is_valid_email(email):
            error = "Informe um e-mail válido."
        else:
            user = authenticate(request, username=email, password=password)
            if user is None:
                exists = User.objects.filter(email=email).exists()
                error = (
                    "Senha incorreta. Verifique e tente novamente."
                    if exists
                    else "Não encontramos uma conta com este e-mail."
                )
            elif not user.is_active:
                error = "Esta conta está desativada."
            else:
                auth_login(request, user)
                return redirect("presentation:apresentacao")

    return render(request, "accounts/login.html", {"error": error, "email_value": email_value})


# ---------------------------------------------------------------------------
# Cadastro
# ---------------------------------------------------------------------------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("presentation:apresentacao")

    error = None
    form_values = {"nome": "", "email": ""}

    if request.method == "POST":
        nome = (request.POST.get("nome") or "").strip()
        email_raw = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm = request.POST.get("confirm") or ""
        form_values = {"nome": nome, "email": email_raw}
        email = normalize_email(email_raw)

        if not nome or not email or not password or not confirm:
            error = "Preencha todos os campos."
        elif not is_valid_email(email):
            error = "Informe um e-mail válido."
        elif len(password) < 6:
            error = "A senha deve ter no mínimo 6 caracteres."
        elif password != confirm:
            error = "As senhas não coincidem."
        elif User.objects.filter(email=email).exists():
            error = "Este e-mail já está cadastrado."
        else:
            User.objects.create_user(email=email, password=password, nome=nome)
            messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
            return redirect("accounts:login")

    return render(request, "accounts/cadastro.html", {"error": error, "form_values": form_values})


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@require_POST
def logout_view(request):
    auth_logout(request)
    return redirect("accounts:login")


# ---------------------------------------------------------------------------
# Recuperação de senha — página (wizard de 3 etapas, mesma UI do original)
# ---------------------------------------------------------------------------

def recover_password_view(request):
    return render(request, "accounts/recuperar_senha.html")


# ---------------------------------------------------------------------------
# Recuperação de senha — endpoints JSON (equivalentes aos server functions
# requestResetCode / verifyResetCode / resetPassword do projeto original)
# ---------------------------------------------------------------------------

def _hash_code(email: str, code: str) -> str:
    return hashlib.sha256(f"{email}:{code}".encode("utf-8")).hexdigest()


def _json_body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


def _load_valid_code(email: str, code: str) -> PasswordResetCode | None:
    record = (
        PasswordResetCode.objects.filter(email=email, code_hash=_hash_code(email, code), used=False)
        .order_by("-created_at")
        .first()
    )
    return record


@require_POST
def request_reset_code(request):
    """Etapa 1 — gera um código de recuperação e o envia exclusivamente
    por e-mail via Brevo.

    Regras de segurança aplicadas aqui:
    - O código NUNCA é incluído na resposta JSON, nem em nenhum outro
      lugar acessível ao frontend — ele só existe (a) em memória durante
      este request, (b) como hash SHA-256 no banco, e (c) no corpo do
      e-mail realmente enviado pela Brevo.
    - A resposta não revela se o e-mail está ou não cadastrado (evita
      enumeração de contas): tanto para um e-mail existente quanto para
      um inexistente, o formato-padrão de sucesso é o mesmo.
    - Se o envio pela Brevo falhar de verdade (credenciais inválidas,
      remetente não verificado, indisponibilidade, rede etc.), a resposta
      é um erro genuíno — nunca uma falsa mensagem de sucesso.
    """
    data = _json_body(request)
    email = normalize_email(data.get("email", ""))

    if not email or not is_valid_email(email):
        return JsonResponse({"error": "Informe um e-mail válido."}, status=400)

    generic_success = {
        "success": True,
        "message": "Se o e-mail estiver cadastrado, enviaremos um código de recuperação.",
    }

    user = User.objects.filter(email=email).first()
    if user is None:
        # Não revela que a conta não existe — mesma resposta do caminho feliz.
        return JsonResponse(generic_success)

    code = f"{secrets.randbelow(1_000_000):06d}"
    code_hash = _hash_code(email, code)
    ttl = settings.PASSWORD_RESET_CODE_TTL_MINUTES

    with transaction.atomic():
        PasswordResetCode.objects.filter(email=email, used=False).update(used=True)
        record = PasswordResetCode.objects.create(
            email=email,
            code_hash=code_hash,
            expires_at=timezone.now() + timedelta(minutes=ttl),
        )

    try:
        emailing.send_password_reset_code(email, code, ttl)
    except emailing.EmailDeliveryError:
        # Autoinvalida o código recém-criado: como o e-mail não foi
        # entregue, ninguém deveria conseguir usá-lo.
        record.used = True
        record.save(update_fields=["used"])
        return JsonResponse(
            {"error": "Não foi possível enviar o código agora. Tente novamente em instantes."},
            status=502,
        )

    return JsonResponse(generic_success)


@require_POST
def verify_reset_code(request):
    """Etapa 2 — valida o código informado pelo usuário."""
    data = _json_body(request)
    email = normalize_email(data.get("email", ""))
    code = (data.get("code") or "").strip()

    if not email or not is_valid_email(email) or len(code) != 6:
        return JsonResponse({"error": "Código de recuperação inválido."}, status=400)

    record = _load_valid_code(email, code)
    if not record:
        return JsonResponse({"error": "Código de recuperação inválido."}, status=400)
    if record.expires_at < timezone.now():
        return JsonResponse({"error": "Código de recuperação expirado. Solicite um novo."}, status=400)

    return JsonResponse({"valid": True})


@require_POST
def reset_password(request):
    """Etapa 3 — define a nova senha e invalida o código."""
    data = _json_body(request)
    email = normalize_email(data.get("email", ""))
    code = (data.get("code") or "").strip()
    password = data.get("password") or ""

    if not email or not is_valid_email(email) or len(code) != 6:
        return JsonResponse({"error": "Código de recuperação inválido."}, status=400)
    if len(password) < 6:
        return JsonResponse({"error": "A senha deve ter no mínimo 6 caracteres."}, status=400)

    record = _load_valid_code(email, code)
    if not record:
        return JsonResponse({"error": "Código de recuperação inválido."}, status=400)
    if record.expires_at < timezone.now():
        return JsonResponse({"error": "Código de recuperação expirado. Solicite um novo."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Não encontramos uma conta com este e-mail."}, status=400)

    user.set_password(password)
    user.save(update_fields=["password"])

    record.used = True
    record.save(update_fields=["used"])

    return JsonResponse({"ok": True})
