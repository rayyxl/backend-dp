from django.urls import reverse

# Mesma lista NAV do componente _authenticated/route.tsx do projeto original,
# com os mesmos rótulos e ícones (Lucide) na mesma ordem.
NAV = [
    ("presentation:apresentacao", "Apresentação", "layout-dashboard"),
    ("presentation:conceito", "Conceito da área", "book-open"),
    ("presentation:conceitos", "Principais conceitos estudados", "boxes"),
    ("presentation:competencias", "Competências para começar", "target"),
    ("presentation:porta_de_entrada", "Porta de entrada", "door-open"),
    ("presentation:brasil", "A área no Brasil", "bar-chart-3"),
    ("presentation:surpreendeu", "O que surpreendeu a equipe", "star"),
    ("assistant:ia", "IA Generativa", "sparkles"),
]


def sidebar_nav(request):
    """Disponibiliza `nav_items` (com o estado 'active' já calculado) e
    `current_nav_label` para o header mobile, em todos os templates —
    equivalente ao array NAV + pathname.startsWith(item.to) do original.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    path = request.path
    items = []
    current_label = "Apresentação"
    for url_name, label, icon in NAV:
        url = reverse(url_name)
        active = path.startswith(url)
        if active:
            current_label = label
        items.append({"url": url, "label": label, "icon": icon, "active": active})

    return {"nav_items": items, "current_nav_label": current_label}
