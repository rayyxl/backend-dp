"""
Configurações do projeto "Desenvolvimento Back-end — Apresentação UNIPÊ".

Réplica em Django do projeto original (TanStack Start + React + Supabase,
gerado com Lovable). Todas as credenciais/segredos são lidos do arquivo
.env — nunca ficam hardcoded aqui.
"""

import os

import dj_database_url

from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-apenas-para-desenvolvimento-local-troque-em-producao",
)

DEBUG = env_bool("DEBUG", True)

_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(",") if h.strip()]

_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(",") if o.strip()]


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "presentation",
    "assistant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "presentation.context_processors.sidebar_nav",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ---------------------------------------------------------------------------
# Banco de dados — SQLite nativo do Django (nenhuma configuração externa
# é necessária).
# ---------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
    )
}


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

# O modelo de usuário customizado usa email como USERNAME_FIELD, então o
# ModelBackend padrão do Django já autentica por e-mail sem necessidade de
# um backend próprio.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "presentation:apresentacao"
LOGOUT_REDIRECT_URL = "accounts:login"


# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Segurança adicional em produção (DEBUG=False)
#
# O PythonAnywhere já serve as Web Apps via HTTPS nos subdomínios
# *.pythonanywhere.com, então é seguro exigir cookies apenas-HTTPS quando
# DEBUG estiver desligado. SECURE_SSL_REDIRECT é deixado como False por
# padrão (configurável via .env) para evitar loop de redirecionamento
# atrás do proxy reverso deles caso SECURE_PROXY_SSL_HEADER não esteja
# configurado no ambiente específico.
# ---------------------------------------------------------------------------

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)


# ---------------------------------------------------------------------------
# Integrações externas (chaves lidas do .env — nunca hardcoded)
# ---------------------------------------------------------------------------

# IA — Google Gemini (SDK oficial google-genai). Necessária apenas para o
# chat de IA (assistant/services.py) realmente gerar respostas; sem ela, o
# restante do site funciona normalmente e o chat retorna uma mensagem de
# erro amigável.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

# Brevo (envio de e-mails transacionais — necessária apenas para o fluxo de
# recuperação de senha realmente entregar o código por e-mail; o restante
# do site funciona normalmente sem essas variáveis configuradas)
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "no-reply@example.com")
BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Desenvolvimento Back-end — UNIPÊ")

# Regras de negócio replicadas do projeto original
PASSWORD_RESET_CODE_TTL_MINUTES = 15
AI_CONVERSATION_HISTORY_LIMIT = 30
AI_CONVERSATION_TITLE_MAX_LENGTH = 48
