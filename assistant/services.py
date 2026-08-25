"""
Comunicação com o Google Gemini através do SDK oficial `google-genai`.

Substitui a integração anterior com a OpenAI. Usa exclusivamente o cliente
oficial do Google:

    from google import genai
    client = genai.Client(api_key=...)
    client.models.generate_content(...)

Nenhuma chamada manual via `requests.post()` ou REST é feita para a API do
Gemini — toda a comunicação passa pelo SDK oficial. A chave nunca é
exposta ao navegador: toda chamada acontece aqui, no backend.

O histórico e o SYSTEM_PROMPT (com o conteúdo acadêmico do trabalho) são
preservados exatamente como antes; só a camada de transporte/IA mudou, de
OpenAI para Gemini. Diferente da API da OpenAI, o Gemini não usa uma
mensagem de papel "system" dentro da lista de conteúdos — o prompt de
sistema é passado separadamente via `system_instruction`, e o papel do
assistente é "model" (não "assistant") na lista de turnos da conversa.
"""

import logging

import httpx
from django.conf import settings
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from .prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Timeout de requisição para a API do Gemini, em milissegundos (formato
# exigido por HttpOptions.timeout do SDK).
_REQUEST_TIMEOUT_MS = 45_000

# O papel do usuário é o mesmo em ambas as APIs ("user"), mas o papel do
# assistente na Gemini API é "model" (na OpenAI era "assistant"). Nossos
# models Django continuam salvando "assistant" — a tradução acontece só
# aqui, na fronteira com o SDK.
_ROLE_MAP = {"user": "user", "assistant": "model"}


class AssistantError(Exception):
    """Erro amigável, já com a mensagem pronta para exibir ao usuário.

    Nunca deve carregar a API key, stack trace ou qualquer detalhe interno
    — apenas uma frase curta e segura para mostrar na interface.
    """


def _build_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        # Nunca revela ao usuário que é um problema de configuração interna.
        raise AssistantError("Não foi possível enviar sua pergunta.")

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS),
    )


def _build_contents(history: list[dict], question: str) -> list[types.Content]:
    contents = [
        types.Content(role=_ROLE_MAP[m["role"]], parts=[types.Part(text=m["content"])])
        for m in history
    ]
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    return contents


def ask_ai(history: list[dict], question: str) -> str:
    """Envia a pergunta + histórico ao Gemini e retorna o texto da resposta.

    `history` é uma lista de dicts {"role": "user"|"assistant", "content": str},
    já limitada a AI_CONVERSATION_HISTORY_LIMIT mensagens, na ordem
    cronológica (mensagens mais antigas primeiro) — o mesmo contrato que a
    view em `assistant/views.py` já monta a partir do banco.
    """
    client = _build_client()
    contents = _build_contents(history, question)
    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config,
        )

    # --- Erros de resposta HTTP do Gemini (ClientError=4xx, ServerError=5xx,
    # ambos herdam de genai_errors.APIError, que expõe `.code` com o status
    # HTTP real) ---
    except genai_errors.ClientError as exc:
        code = exc.code
        if code in (401, 403):
            logger.error("Gemini: erro de autenticação/permissão (status %s): %s", code, exc.message)
            raise AssistantError("O serviço de IA está temporariamente indisponível para este projeto.") from None
        if code == 429:
            logger.warning("Gemini: limite de requisições atingido (status 429).")
            raise AssistantError("Muitas perguntas em sequência. Aguarde alguns segundos.") from None
        if code == 404:
            logger.error("Gemini: modelo '%s' não encontrado (status 404).", settings.GEMINI_MODEL)
            raise AssistantError("Não foi possível enviar sua pergunta.") from None
        logger.error("Gemini: requisição inválida (status %s): %s", code, exc.message)
        raise AssistantError("Não foi possível enviar sua pergunta.") from None

    except genai_errors.ServerError as exc:
        logger.error("Gemini: erro no servidor da API (status %s): %s", exc.code, exc.message)
        raise AssistantError("O serviço de IA está temporariamente indisponível. Tente novamente em instantes.") from None

    except genai_errors.APIError as exc:
        # Rede de segurança para qualquer outro erro de API não coberto acima.
        logger.error("Gemini: erro da API (status %s): %s", exc.code, exc.message)
        raise AssistantError("Não foi possível enviar sua pergunta.") from None

    # --- Erros de transporte (rede/DNS/timeout) — o SDK usa httpx internamente ---
    except httpx.HTTPError as exc:
        logger.error("Gemini: falha de conexão/timeout ao contatar a API: %s", exc)
        raise AssistantError("Não foi possível enviar sua pergunta.") from None

    except Exception as exc:  # noqa: BLE001 — rede de segurança final, nunca crasha a request
        logger.error("Gemini: erro inesperado do SDK: %s", exc)
        raise AssistantError("Não foi possível enviar sua pergunta.") from None

    try:
        answer = (response.text or "").strip()
    except Exception as exc:  # resposta em formato inesperado (ex.: bloqueada por segurança)
        logger.warning("Gemini: não foi possível extrair texto da resposta: %s", exc)
        answer = ""

    if not answer:
        logger.warning("Gemini: resposta vazia recebida para o modelo '%s'.", settings.GEMINI_MODEL)

    return answer or "Não consegui gerar uma resposta agora. Tente reformular sua pergunta."
