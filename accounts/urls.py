from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("cadastro/", views.signup_view, name="cadastro"),
    path("logout/", views.logout_view, name="logout"),
    path("recuperar-senha/", views.recover_password_view, name="recuperar_senha"),
    path(
        "recuperar-senha/solicitar-codigo/",
        views.request_reset_code,
        name="request_reset_code",
    ),
    path(
        "recuperar-senha/verificar-codigo/",
        views.verify_reset_code,
        name="verify_reset_code",
    ),
    path("recuperar-senha/redefinir/", views.reset_password, name="reset_password"),
]
