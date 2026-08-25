"""
Envio do código de recuperação de senha via Brevo, usando o SDK oficial
`brevo-python` (pacote instalado como `brevo-python`, importado como `brevo`).

Este módulo é a ÚNICA via de entrega do código de recuperação de senha.
Diferente de uma versão anterior deste projeto, o código NUNCA é
devolvido para o frontend nem exibido na tela — ele só existe:

1. no processamento interno deste módulo/da view que o chama;
2. em forma de hash (nunca em texto puro) no banco de dados
   (accounts.models.PasswordResetCode);
3. no corpo do e-mail realmente enviado pela Brevo.

Se o envio falhar por qualquer motivo (chave inválida, remetente não
verificado, limite de envio, erro de rede, erro interno da Brevo etc.),
uma exceção `EmailDeliveryError` é levantada — a camada de views
(accounts/views.py) trata essa exceção retornando um erro genérico ao
usuário, sem jamais reportar sucesso falso.
"""

import logging

import brevo
import httpx
from brevo.core.api_error import ApiError
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Levantada quando o envio real do e-mail falha.

    A mensagem desta exceção é sempre segura para logar (nunca contém a
    API key nem qualquer segredo) — mas mesmo assim as views não repassam
    o texto da exceção diretamente ao usuário; elas mostram uma mensagem
    genérica própria.
    """


def is_configured() -> bool:
    """Indica se há credenciais suficientes da Brevo no `.env`."""
    return bool(settings.BREVO_API_KEY and settings.BREVO_SENDER_EMAIL)


def _build_client() -> "brevo.Brevo":
    return brevo.Brevo(api_key=settings.BREVO_API_KEY)


def _render_email_html(code: str, ttl_minutes: int) -> str:
    return (
        "<div style=\"font-family:sans-serif;max-width:480px;margin:0 auto\">"
        "<p>Você (ou alguém em seu nome) solicitou a recuperação de senha da "
        "sua conta no sistema <strong>Desenvolvimento Back-end</strong> (UNIPÊ).</p>"
        "<p>Use o código abaixo para continuar a recuperação:</p>"
        f"<p style=\"font-size:32px;font-weight:700;letter-spacing:6px;"
        f"background:#f1f3f8;padding:16px 20px;border-radius:12px;"
        f"text-align:center\">{code}</p>"
        f"<p>Esse código é válido por {ttl_minutes} minutos e só pode ser "
        "usado uma vez.</p>"
        "<p style=\"color:#666;font-size:13px\">Se você não solicitou essa "
        "recuperação, apenas ignore este e-mail — sua senha permanece "
        "inalterada.</p>"
        "</div>"
    )


def send_password_reset_code(email: str, code: str, ttl_minutes: int) -> None:
    """Envia o código de recuperação por e-mail via Brevo.

    Não retorna nada em caso de sucesso. Em caso de falha, levanta
    `EmailDeliveryError` — nunca falha silenciosamente e nunca retorna
    "sucesso" sem que a Brevo tenha de fato aceitado o envio.
    """
    if not is_configured():
        # Configuração ausente é um problema de operação/infraestrutura,
        # não algo que o usuário final deva ver em detalhes.
        logger.error(
            "Brevo não configurado: BREVO_API_KEY e/ou BREVO_SENDER_EMAIL "
            "ausentes no .env. O código de recuperação NÃO foi enviado."
        )
        raise EmailDeliveryError("Serviço de e-mail não configurado.")

    client = _build_client()

    try:
        client.transactional_emails.send_transac_email(
            sender={
                "name": settings.BREVO_SENDER_NAME,
                "email": settings.BREVO_SENDER_EMAIL,
            },
            to=[{"email": email}],
            subject="Código de recuperação de senha — Desenvolvimento Back-end",
            html_content=_render_email_html(code, ttl_minutes),
        )

    # --- Erros de resposta HTTP da Brevo (todos herdam de ApiError) ---
    except brevo.UnauthorizedError:
        logger.error("Brevo: 401 Unauthorized — BREVO_API_KEY inválida ou revogada.")
        raise EmailDeliveryError("Falha de autenticação com o provedor de e-mail.") from None

    except brevo.ForbiddenError:
        logger.error(
            "Brevo: 403 Forbidden — verifique se o remetente '%s' está validado na conta Brevo.",
            settings.BREVO_SENDER_EMAIL,
        )
        raise EmailDeliveryError("Remetente não autorizado no provedor de e-mail.") from None

    except brevo.TooManyRequestsError:
        logger.warning("Brevo: 429 Too Many Requests — limite de envio atingido.")
        raise EmailDeliveryError("Limite de envio atingido no provedor de e-mail.") from None

    except brevo.BadRequestError as exc:
        logger.error("Brevo: 400 Bad Request ao enviar e-mail (destinatário=%s): %s", email, exc)
        raise EmailDeliveryError("Requisição de e-mail inválida.") from None

    except brevo.InternalServerError:
        logger.error("Brevo: 500 Internal Server Error.")
        raise EmailDeliveryError("Erro interno do provedor de e-mail.") from None

    except ApiError as exc:
        # Qualquer outro status HTTP não coberto explicitamente acima
        # (ex.: 402 Payment Required — créditos de e-mail esgotados).
        logger.error("Brevo: erro da API (status %s): %s", exc.status_code, exc.body)
        raise EmailDeliveryError("Erro no provedor de e-mail.") from None

    # --- Erros de transporte (rede/DNS/timeout) — o SDK usa httpx internamente ---
    except httpx.HTTPError as exc:
        logger.error("Brevo: falha de conexão/timeout ao contatar a API: %s", exc)
        raise EmailDeliveryError("Falha de conexão com o provedor de e-mail.") from None

    # --- Rede de segurança final: nunca deixar uma falha real virar "sucesso" ---
    except Exception as exc:  # noqa: BLE001 — intencional: nunca engolir silenciosamente
        logger.error("Brevo: falha inesperada ao enviar e-mail: %s", exc)
        raise EmailDeliveryError("Falha inesperada ao enviar e-mail.") from None

    logger.info("Brevo: e-mail de recuperação de senha enviado com sucesso para %s.", email)
