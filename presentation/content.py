"""
Conteúdo acadêmico extraído integralmente do documento
"BACKEND_-_DP.pdf" (UNIPÊ — Design Profissional, 2026.2).

Nada aqui é inventado: os textos reproduzem exatamente o conteúdo já
presente no projeto original (src/content/presentation.ts). Qualquer
alteração neste arquivo deve ser feita apenas para corrigir uma
divergência em relação ao documento fonte, nunca para "melhorar" o texto.
"""

INSTITUTIONAL = {
    "instituicao": "Centro Universitário de João Pessoa (UNIPÊ)",
    "curso": "Ciência da Computação",
    "componente": "Design Profissional",
    "periodo": "2026.2",
    "docente": "Francisco Ribeiro Dos Santos Junior",
    "discentes": [
        "Rai Soares da Silva",
        "Luiz Eduardo Medeiros Lima",
        "Débora Mouzinho da Silva",
        "Ronald Amaral Melo",
    ],
    "tema": "Desenvolvimento Back-end",
}

CONCEITO_AREA = {
    "titulo": "Conceito da área",
    "paragrafos": [
        "O back-end é a parte do sistema responsável por fazer tudo o que o usuário vê "
        "funcionar. Ele apresenta lógicas complexas e realiza o armazenamento de dados, "
        "além de se comunicar com as outras partes do sistema.",
    ],
    "exemplo": (
        "Exemplo: quando o usuário realiza login, o back-end é responsável por verificar "
        "o usuário e a senha, confirmar se as credenciais estão corretas e, então, "
        "permitir o acesso ao sistema."
    ),
}

CONCEITOS_ESTUDADOS = [
    {
        "numero": "2.1",
        "titulo": "Servidor",
        "texto": "Responsável por processar as informações e executar as funções do sistema.",
    },
    {
        "numero": "2.2",
        "titulo": "Banco de Dados",
        "texto": "É onde as informações do sistema são armazenadas e organizadas.",
    },
    {
        "numero": "2.3",
        "titulo": "Lógica de Negócio",
        "texto": "Define as regras e os processos que determinam como o sistema deve funcionar.",
    },
    {
        "numero": "2.4",
        "titulo": "API",
        "texto": (
            "Permite a comunicação entre o back-end e outras partes do sistema, "
            "incluindo o front-end."
        ),
    },
    {
        "numero": "2.5",
        "titulo": "Autenticação e autorização",
        "texto": (
            "É o conjunto de métodos que verifica quem é o usuário e o que ele tem "
            "permissão para fazer dentro do sistema."
        ),
    },
]

COMPETENCIAS = {
    "conhecimentos_essenciais": (
        "Para iniciar na área de desenvolvimento back-end, é fundamental dominar lógica "
        "de programação e pelo menos uma linguagem, como Python, JavaScript/TypeScript, "
        "Java, C# ou PHP."
    ),
    "linguagens": ["Python", "JavaScript/TypeScript", "Java", "C#", "PHP"],
    "ferramentas": [
        "PostgreSQL",
        "MySQL",
        "Docker",
        "AWS",
        "Cursor",
        "VS Code",
        "Git/GitHub",
        "Azure",
        "Windows, Linux ou Mac",
    ],
    "soft_skills": [
        {"titulo": "Resolução de problemas", "texto": "Investigar erros e encontrar soluções."},
        {"titulo": "Comunicação", "texto": "Explicar decisões técnicas com clareza."},
        {"titulo": "Trabalho em equipe", "texto": "Colaborar com diferentes profissionais."},
        {
            "titulo": "Autonomia e proatividade",
            "texto": "Buscar soluções e saber quando pedir ajuda.",
        },
        {
            "titulo": "Aprendizado contínuo",
            "texto": "Acompanhar novas tecnologias e práticas.",
        },
        {
            "titulo": "Atenção aos detalhes",
            "texto": "Evitar erros que possam comprometer sistemas.",
        },
        {
            "titulo": "Organização e adaptabilidade",
            "texto": "Gerenciar tarefas e adaptar-se a diferentes projetos.",
        },
    ],
}

PORTA_ENTRADA = {
    "paragrafo": (
        "Devido à grande concorrência presente nessa área, um iniciante que possua "
        "habilidades e conhecimentos técnicos poderá ingressar como estagiário na maior "
        "parte das vagas ofertadas. Com o decorrer do tempo, consequentemente, virá o "
        "ganho de experiência, característica essa que irá corroborar com o aumento de "
        "posições do indivíduo na área. Posições essas que são: Júnior, Pleno e Sênior."
    ),
    "fluxo": [
        {
            "nivel": "Estagiário",
            "texto": (
                "Ingresso na maior parte das vagas ofertadas para quem possui "
                "habilidades e conhecimentos técnicos."
            ),
        },
        {"nivel": "Júnior", "texto": "Primeira posição efetiva, com o ganho de experiência."},
        {"nivel": "Pleno", "texto": "Evolução decorrente da experiência adquirida na área."},
        {"nivel": "Sênior", "texto": "Posição mais avançada citada no trabalho."},
    ],
}

BRASIL = {
    "linkedin": {
        "titulo": "5.1. Análise feita a partir do Linkedin",
        "intro": (
            "Hodiernamente, ao acessarmos o Linkedin, a maior rede social profissional "
            "do mundo, e buscarmos vagas back-end no Brasil, veremos que há diversas "
            "vagas para a área em nosso país:"
        ),
        "meio": (
            "Contudo, dependendo do estado que você residir, poderá haver uma baixa "
            "significativa na quantidade de vagas ofertadas. Ao procurarmos vagas em "
            "nossa estado (Paraíba), iremos nos deparar com a seguinte quantidade de "
            "vagas oferecidas:"
        ),
        "fim": (
            "Tais resultados refletem como em determinadas regiões de nossa federação, "
            "poderá haver mudanças na quantidade de oportunidades, inferindo no número "
            "de ingressos na área."
        ),
        "legenda_brasil": (
            "Busca por vagas de back-end no Brasil no Linkedin, com destaque para a vaga "
            "de Desenvolvedor Back-end Júnior na Housi."
        ),
        "legenda_paraiba": "Busca por vagas de back-end na Paraíba no Linkedin.",
    },
    "brasscom": {
        "titulo": "5.2. Análise realizada com o jornal Brasscom",
        "paragrafos": [
            "A Brasscom (Associação das Empresas de Tecnologia da Informação e "
            "Comunicação (TIC) e de Tecnologias Digitais do Brasil) publicou, em agosto "
            "de 2026, o Relatório de Regionalização dos Empregos CLT de TIC, que "
            "apresenta um panorama do mercado de Tecnologia da Informação e Comunicação "
            "no Brasil, abordando a evolução do setor e das principais ocupações da área.",
            "O estudo destaca a relevância das ocupações relacionadas ao desenvolvimento "
            "de sistemas e à programação. Como apresentado na imagem acima, entre as "
            "principais ocupações estão Analista de Desenvolvimento de Sistemas, com "
            "252.903 empregos CLT, e Programador de Sistemas da Informação, com 101.593 "
            "empregos CLT. Esses profissionais desempenham atividades diretamente "
            "relacionadas ao desenvolvimento de software, podendo atuar em funções que "
            "envolvem o back-end.",
            "Embora o relatório não apresente uma categoria específica para "
            "desenvolvedores back-end, os dados demonstram a importância do "
            "desenvolvimento de sistemas no mercado brasileiro de TI. Esse cenário "
            "reforça a relevância da área de back-end, responsável por aspectos "
            "fundamentais das aplicações, como regras de negócio, processamento de "
            "informações, gerenciamento de dados e comunicação entre diferentes partes "
            "de um sistema.",
        ],
        "legenda_mapa": (
            "Mapa Geral Nacional — participação dos empregos CLT de TIC e Top 5 "
            "ocupações de TIC (Brasscom, 2026)."
        ),
        "participacao": [
            {"ano": "2016", "valor": 1.4},
            {"ano": "2018", "valor": 1.4},
            {"ano": "2020", "valor": 1.5},
            {"ano": "2022", "valor": 1.7},
            {"ano": "2025", "valor": 1.6},
        ],
        "periodos": [
            {
                "intervalo": "2016 a 2020",
                "texto": (
                    "Entre 2016 e 2020, a participação do setor TIC avançou de forma "
                    "orgânica e linear, elevando em 0,1 p.p. O movimento partiu de uma "
                    "base pequena, com ganhos marginais e trajetória previsível."
                ),
            },
            {
                "intervalo": "2020 a 2022",
                "texto": (
                    "De 2020 a 2022, a pandemia acelerou a digitalização e redefiniu a "
                    "demanda, elevando a participação de TIC para 1,7% em 2022. O ganho "
                    "de 0,2 p.p. reflete o choque de adoção tecnológica e a readequação "
                    "das necessidades de empresas e consumidores."
                ),
            },
            {
                "intervalo": "2023 a 2025",
                "texto": (
                    "Entre 2023 e 2025, o setor entra em normalização e consolidação: "
                    "crescimento mais seletivo, com foco em produtividade, profissionais "
                    "seniores, qualificação da força de trabalho e integração da "
                    "tecnologia às cadeias setoriais da economia."
                ),
            },
        ],
        "transformacao": (
            "Este setor está passando por uma transformação estrutural nas relações de "
            "trabalho, com crescimento das contratações não celetistas: especialmente "
            "PJs e MEIs, que já superam os vínculos formais CLT no que tange ao "
            "crescimento do número total de profissionais. Entre 2023 e 2025, "
            "trabalhadores informais tiveram um crescimento de 3,3%, enquanto PJs e "
            "MEIs cresceram 8,9% no mesmo período, indicando maior diversificação das "
            "modalidades de emprego."
        ),
        "top_ocupacoes": [
            {
                "posicao": "1°",
                "ocupacao": "Analista de Desenvolvimento de Sistemas",
                "empregos": "252.903",
                "participacao": "26,8%",
                "salario": "R$ 8.337",
                "gerados": "6.039",
            },
            {
                "posicao": "2°",
                "ocupacao": "Analista de Suporte Computacional",
                "empregos": "114.663",
                "participacao": "12,2%",
                "salario": "R$ 3.990",
                "gerados": "2.707",
            },
            {
                "posicao": "3°",
                "ocupacao": "Programador de Sistemas da Informação",
                "empregos": "101.593",
                "participacao": "10,8%",
                "salario": "R$ 5.496",
                "gerados": "2.598",
            },
            {
                "posicao": "4°",
                "ocupacao": "Técnico de apoio ao usuário de informática",
                "empregos": "92.505",
                "participacao": "9,8%",
                "salario": "R$ 2.334",
                "gerados": "7.089",
            },
            {
                "posicao": "5°",
                "ocupacao": "Técnico Eletrônico",
                "empregos": "58.494",
                "participacao": "6,2%",
                "salario": "R$ 2.644",
                "gerados": "745",
            },
        ],
        "fonte": (
            "Fonte: Relatório de Perspectivas do Mercado de Trabalho do Macrossetor de "
            "TIC (Brasscom, 2026)."
        ),
    },
}

SURPREENDEU = {
    "texto": (
        "O desenvolvimento back-end é a base da tecnologia corporativa moderna. "
        "Independentemente do segmento da empresa, é no back-end que se processam as "
        "regras de negócio, a segurança dos dados e o desempenho do sistema, servindo "
        "como a base fundamental para o crescimento computacional e operacional do "
        "negócio."
    ),
    "destaques": [
        {
            "titulo": "Base da tecnologia corporativa moderna",
            "texto": (
                "O desenvolvimento back-end é a base da tecnologia corporativa moderna, "
                "independentemente do segmento da empresa."
            ),
        },
        {
            "titulo": "Regras de negócio, segurança e desempenho",
            "texto": (
                "É no back-end que se processam as regras de negócio, a segurança dos "
                "dados e o desempenho do sistema."
            ),
        },
        {
            "titulo": "Base do crescimento do negócio",
            "texto": "Serve como a base fundamental para o crescimento computacional e operacional do negócio.",
        },
    ],
}


def _build_document_context() -> str:
    """Contexto textual do trabalho, usado como base de conhecimento da IA.

    Réplica exata da lógica de `documentContext` em content/presentation.ts.
    """
    discentes = ", ".join(INSTITUTIONAL["discentes"])
    conceitos = "\n".join(
        f"{c['numero']} {c['titulo']}: {c['texto']}" for c in CONCEITOS_ESTUDADOS
    )
    soft_skills = "\n".join(
        f"- {s['titulo']}: {s['texto']}" for s in COMPETENCIAS["soft_skills"]
    )
    participacao = "; ".join(
        f"{p['ano']}: {str(p['valor']).replace('.', ',')}%" for p in BRASIL["brasscom"]["participacao"]
    )
    periodos = "\n".join(
        f"{p['intervalo']}: {p['texto']}" for p in BRASIL["brasscom"]["periodos"]
    )
    top_ocupacoes = "; ".join(
        f"{o['posicao']} {o['ocupacao']} — {o['empregos']} empregos CLT, "
        f"{o['participacao']} do total, média salarial {o['salario']}, "
        f"{o['gerados']} empregos gerados em 2025"
        for o in BRASIL["brasscom"]["top_ocupacoes"]
    )

    return f"""TRABALHO ACADÊMICO — {INSTITUTIONAL['tema']}
Instituição: {INSTITUTIONAL['instituicao']}
Curso: {INSTITUTIONAL['curso']} | Componente curricular: {INSTITUTIONAL['componente']} | Período: {INSTITUTIONAL['periodo']}
Docente: {INSTITUTIONAL['docente']}
Discentes: {discentes}

1. CONCEITO DA ÁREA
{chr(10).join(CONCEITO_AREA['paragrafos'])}
{CONCEITO_AREA['exemplo']}

2. PRINCIPAIS CONCEITOS ESTUDADOS
{conceitos}

3. COMPETÊNCIAS PARA COMEÇAR
3.1 Conhecimentos essenciais: {COMPETENCIAS['conhecimentos_essenciais']}
3.2 Ferramentas: {', '.join(COMPETENCIAS['ferramentas'])}.
3.3 Competências comportamentais (Soft Skills):
{soft_skills}

4. PORTA DE ENTRADA
{PORTA_ENTRADA['paragrafo']}

5. A ÁREA NO BRASIL
{BRASIL['linkedin']['intro']}
{BRASIL['linkedin']['meio']}
{BRASIL['linkedin']['fim']}
{chr(10).join(BRASIL['brasscom']['paragrafos'])}
Participação dos empregos CLT de TIC sobre o total de empregos CLT no Brasil: {participacao}.
{periodos}
{BRASIL['brasscom']['transformacao']}
Top 5 ocupações de TIC: {top_ocupacoes}.
{BRASIL['brasscom']['fonte']}

6. O QUE SURPREENDEU A EQUIPE
{SURPREENDEU['texto']}""".strip()


DOCUMENT_CONTEXT = _build_document_context()
