import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Gerenciador de usuários com e-mail como identificador de login.

    Equivalente ao par auth.users + public.profiles do projeto original
    (Supabase): aqui os dois viram um único modelo de usuário do Django.
    """

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("nome", extra_fields.get("nome") or "Administrador")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Usuário da aplicação. Login por e-mail + senha (hash via Django)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("e-mail", unique=True)
    nome = models.CharField("nome", max_length=255, blank=True, default="")
    is_active = models.BooleanField("ativo", default=True)
    is_staff = models.BooleanField("equipe (acesso ao admin)", default=False)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return self.nome or self.email

    def get_short_name(self) -> str:
        return self.nome or self.email


class PasswordResetCode(models.Model):
    """Código de recuperação de senha de 6 dígitos, com hash e expiração.

    Réplica exata da tabela public.password_reset_codes do projeto original:
    o código nunca é armazenado em texto puro, apenas seu hash SHA-256.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "código de recuperação de senha"
        verbose_name_plural = "códigos de recuperação de senha"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["email", "created_at"])]

    def __str__(self) -> str:
        return f"{self.email} ({'usado' if self.used else 'ativo'})"
