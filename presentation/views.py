from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import content


@login_required
def apresentacao(request):
    return render(request, "presentation/apresentacao.html", {"institutional": content.INSTITUTIONAL})


@login_required
def conceito(request):
    pilares = [
        {"title": "Lógicas complexas", "icon": "workflow", "text": "Apresenta lógicas complexas."},
        {
            "title": "Armazenamento de dados",
            "icon": "database",
            "text": "Realiza o armazenamento de dados.",
        },
        {
            "title": "Comunicação",
            "icon": "server",
            "text": "Comunica-se com as outras partes do sistema.",
        },
        {
            "title": "Verificação de credenciais",
            "icon": "key-round",
            "text": "Verifica usuário e senha e libera o acesso ao sistema.",
        },
    ]
    return render(
        request,
        "presentation/conceito.html",
        {
            "conceito_area": content.CONCEITO_AREA,
            "pilares": pilares,
            "eyebrow": "Tópico 1",
            "title": content.CONCEITO_AREA["titulo"],
        },
    )


@login_required
def conceitos(request):
    return render(
        request,
        "presentation/conceitos.html",
        {
            "conceitos_estudados": content.CONCEITOS_ESTUDADOS,
            "eyebrow": "Tópico 2",
            "title": "Principais conceitos estudados",
            "intro": "Os conceitos abaixo são apresentados no trabalho como a base do desenvolvimento back-end.",
        },
    )


@login_required
def competencias(request):
    return render(
        request,
        "presentation/competencias.html",
        {
            "competencias": content.COMPETENCIAS,
            "eyebrow": "Tópico 3",
            "title": "Competências necessárias para começar",
            "intro": content.COMPETENCIAS["conhecimentos_essenciais"],
        },
    )


@login_required
def porta_de_entrada(request):
    return render(
        request,
        "presentation/porta_de_entrada.html",
        {
            "porta_entrada": content.PORTA_ENTRADA,
            "eyebrow": "Tópico 4",
            "title": "Porta de entrada na área",
            "intro": content.PORTA_ENTRADA["paragrafo"],
        },
    )


@login_required
def brasil(request):
    participacao = content.BRASIL["brasscom"]["participacao"]
    max_valor = max(item["valor"] for item in participacao)
    participacao_barras = [
        {
            "ano": item["ano"],
            "valor_fmt": str(item["valor"]).replace(".", ","),
            "largura_pct": round((item["valor"] / max_valor) * 100, 2),
        }
        for item in participacao
    ]
    return render(
        request,
        "presentation/brasil.html",
        {
            "brasil": content.BRASIL,
            "participacao_barras": participacao_barras,
            "eyebrow": "Tópico 5",
            "title": "A área no Brasil",
            "intro": (
                "O trabalho analisa o mercado brasileiro a partir de duas fontes: as vagas "
                "anunciadas no Linkedin e o relatório da Brasscom."
            ),
        },
    )


@login_required
def surpreendeu(request):
    return render(
        request,
        "presentation/surpreendeu.html",
        {
            "surpreendeu": content.SURPREENDEU,
            "eyebrow": "Tópico 6",
            "title": "O que mais surpreendeu a equipe",
        },
    )
