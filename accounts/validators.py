import re

# Mesma expressão regular usada no frontend original (index.tsx / cadastro.tsx
# / recuperar-senha.tsx): validação simples e permissiva de e-mail.
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value or ""))


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()
