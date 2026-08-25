from django.urls import path

from . import views

app_name = "presentation"

urlpatterns = [
    path("apresentacao/", views.apresentacao, name="apresentacao"),
    path("conceito/", views.conceito, name="conceito"),
    path("conceitos/", views.conceitos, name="conceitos"),
    path("competencias/", views.competencias, name="competencias"),
    path("porta-de-entrada/", views.porta_de_entrada, name="porta_de_entrada"),
    path("brasil/", views.brasil, name="brasil"),
    path("surpreendeu/", views.surpreendeu, name="surpreendeu"),
]
