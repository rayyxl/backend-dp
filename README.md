# Desenvolvimento Back-end — Apresentação UNIPÊ (réplica em Django)

Réplica funcional e visual, em **Python + Django**, do projeto acadêmico
originalmente gerado com **Lovable** (React 19 + TanStack Start + Supabase),
disponível em `academy-ascii`. O objetivo desta versão é reproduzir o mais
fielmente possível a experiência do usuário do projeto original — layout,
cores, tipografia, fluxos de navegação e funcionalidades — usando uma stack
100% Django, sem depender de nenhum serviço externo obrigatório (roda
localmente com SQLite).

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Apps Django](#apps-django)
- [Models](#models)
- [Instalação](#instalação)
- [Configuração do `.env`](#configuração-do-env)
- [Executando o projeto](#executando-o-projeto)
- [Criando um superusuário](#criando-um-superusuário)
- [Autenticação](#autenticação)
- [Recuperação de senha](#recuperação-de-senha)
- [Integração com o Google Gemini (IA)](#integração-com-o-google-gemini-ia)
- [Integração com a Brevo (e-mail)](#integração-com-a-brevo-e-mail)
- [Páginas e rotas](#páginas-e-rotas)
- [Assets / imagens](#assets--imagens)
- [Configuração das APIs externas](#configuração-das-apis-externas)
- [Deploy no PythonAnywhere](#deploy-no-pythonanywhere)
- [Estrutura de diretórios](#estrutura-de-diretórios)
- [Diferenças conscientes em relação ao original](#diferenças-conscientes-em-relação-ao-original)

---

## Visão geral

O projeto apresenta um trabalho acadêmico de Ciência da Computação (UNIPÊ,
2026.2) sobre **Desenvolvimento Back-end**, com:

- tela de **login**, **cadastro** e **recuperação de senha** (em 3 etapas);
- **7 páginas de conteúdo protegidas** por autenticação (apresentação,
  conceito da área, principais conceitos, competências, porta de entrada,
  a área no Brasil, o que surpreendeu a equipe);
- um **assistente de IA** com histórico de conversas persistido no banco,
  que responde tanto sobre desenvolvimento back-end em geral quanto sobre o
  conteúdo do próprio trabalho.

## Arquitetura

- **Backend:** Django (views + `JsonResponse`, sem Django REST Framework —
  não era necessário para o volume de endpoints do projeto).
- **Frontend:** Django Templates + Tailwind CSS (via CDN, configurado para
  usar exatamente os mesmos tokens de cor/raio do projeto original) + CSS
  próprio (`static/css/styles.css`) + JavaScript puro (sem framework).
- **Banco de dados:** SQLite (padrão do Django, nenhuma configuração
  externa necessária).
- **IA:** SDK oficial do Google Gemini (`google-genai`), feita inteiramente
  no backend (`assistant/services.py`).
- **E-mail:** integração opcional com a Brevo para o envio do código de
  recuperação de senha (`accounts/emailing.py`).

## Apps Django

| App            | Responsabilidade                                                                 |
|-----------------|-----------------------------------------------------------------------------------|
| `accounts`      | Usuário customizado (login por e-mail), cadastro, login, logout, recuperação de senha (código de 6 dígitos), integração opcional com a Brevo. |
| `presentation`  | Conteúdo acadêmico fixo do trabalho e as 7 páginas protegidas; também fornece o contexto de navegação (sidebar) usado em todo o site logado. |
| `assistant`     | Conversas e mensagens do assistente de IA, chamada ao Google Gemini, endpoints JSON do chat. |

## Models

**`accounts.User`** (usuário customizado, `AUTH_USER_MODEL`)
Equivale à junção de `auth.users` + `public.profiles` do Supabase no
projeto original.
- `id` (UUID), `email` (único, usado para login), `nome`, `is_active`,
  `is_staff`, `created_at`, `password` (hash, nunca em texto puro).

**`accounts.PasswordResetCode`**
Réplica da tabela `password_reset_codes` original.
- `id`, `email`, `code_hash` (SHA-256 do código — o código em si nunca é
  persistido), `expires_at`, `used`, `created_at`.

**`assistant.Conversation`**
- `id` (UUID), `user` (FK), `title`, `created_at`, `updated_at`.

**`assistant.Message`**
- `id` (UUID), `conversation` (FK), `role` (`user`/`assistant`), `content`,
  `created_at`.

O conteúdo acadêmico (textos, dados da Brasscom, etc.) **não** é modelado em
banco de dados porque, no projeto original, também é conteúdo estático
embutido no frontend (`src/content/presentation.ts`) — aqui ele foi portado
integralmente para `presentation/content.py`, mantendo o mesmo texto.

## Instalação

```bash
# 1. Clone ou extraia o projeto e entre na pasta
cd academy-ascii-django

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Copie o arquivo de variáveis de ambiente
cp .env.example .env
# edite o .env e preencha SECRET_KEY, GEMINI_API_KEY, BREVO_* (opcional)

# 5. Rode as migrations
python manage.py makemigrations
python manage.py migrate

# 6. (Opcional) crie um superusuário para acessar /admin/
python manage.py createsuperuser

# 7. Suba o servidor
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/** — a tela de login será exibida.

## Configuração do `.env`

```env
SECRET_KEY=troque-esta-chave-por-uma-string-aleatoria-e-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash

BREVO_API_KEY=
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=Desenvolvimento Back-end — UNIPÊ
```

- `SECRET_KEY`: gere uma string aleatória (ex.: `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
- `GEMINI_API_KEY`: necessária apenas para o chat de IA funcionar de fato;
  sem ela, o restante do sistema funciona normalmente e o chat retorna uma
  mensagem de erro amigável.
- `BREVO_*`: opcionais — ver seção [Brevo](#integração-com-a-brevo-e-mail).

Nenhuma dessas chaves é lida em nenhum template, nem enviada ao navegador —
elas só existem no processo Django (`config/settings.py` → `os.environ`).

## Executando o projeto

```bash
python manage.py runserver
```

Comandos úteis durante o desenvolvimento:

```bash
python manage.py makemigrations   # gerar novas migrations após mudar um model
python manage.py migrate          # aplicar migrations
python manage.py collectstatic    # coletar estáticos (para deploy)
python manage.py createsuperuser  # criar acesso ao /admin/
```

## Criando um superusuário

```bash
python manage.py createsuperuser
```

Como o modelo de usuário usa e-mail como identificador, o comando pedirá
`email`, `nome` e senha. Acesse `/admin/` para gerenciar usuários,
conversas e códigos de recuperação de senha.

## Autenticação

- Login por **e-mail + senha** (`/`), com mensagens de erro específicas:
  - e-mail/senha em branco → "Preencha o e-mail e a senha.";
  - e-mail em formato inválido → "Informe um e-mail válido.";
  - e-mail não cadastrado → "Não encontramos uma conta com este e-mail.";
  - senha incorreta → "Senha incorreta. Verifique e tente novamente."
- Cadastro (`/cadastro/`) com validação de nome, e-mail, senha (mínimo 6
  caracteres) e confirmação de senha.
- Logout via formulário `POST` (`/logout/`), disponível no rodapé da
  sidebar.
- Todas as 7 páginas de conteúdo e o chat de IA exigem login
  (`@login_required`); sem sessão válida, o usuário é redirecionado à tela
  de login.
- Senhas **nunca** são armazenadas em texto puro — usam o hasher padrão do
  Django (PBKDF2).

## Recuperação de senha

Fluxo em 3 etapas (`/recuperar-senha/`):

```
1. Informar e-mail        → POST /recuperar-senha/solicitar-codigo/
2. Informar código        → POST /recuperar-senha/verificar-codigo/
3. Definir nova senha      → POST /recuperar-senha/redefinir/
```

Regras de segurança aplicadas:

- O código de 6 dígitos é gerado aleatoriamente no backend
  (`secrets.randbelow`), válido por **15 minutos**, e apenas seu **hash
  SHA-256** é gravado no banco (`PasswordResetCode.code_hash`) — nunca o
  código em texto puro, nunca em log.
- **O código NUNCA é devolvido ao frontend.** Ele só existe (a) em memória
  durante o processamento do request, (b) como hash no banco, e (c) no
  corpo do e-mail realmente enviado pela **Brevo** (SDK oficial
  `brevo-python`, ver `accounts/emailing.py`) — essa é a única via de
  entrega.
- A resposta de "solicitar código" não revela se a conta existe ou não
  (evita enumeração de contas): tanto para um e-mail cadastrado quanto para
  um inexistente, a resposta padrão é
  `{"success": true, "message": "Se o e-mail estiver cadastrado, enviaremos um código de recuperação."}`.
- Se o envio pela Brevo falhar de verdade (credenciais inválidas, remetente
  não verificado, indisponibilidade, rede etc.), a aplicação **nunca**
  reporta um falso sucesso — a resposta é um erro genuíno (HTTP 502) e o
  código recém-gerado é imediatamente invalidado (`used=True`), já que
  nunca chegou a ser entregue.
- Após o uso (ou ao solicitar um novo código), o código anterior é marcado
  como `used=True` e não pode mais ser reaproveitado.

## Integração com o Google Gemini (IA)

- Usa o **SDK oficial do Google Gemini** (`pip install google-genai`,
  `from google import genai`, `genai.Client(api_key=...)`) em
  `assistant/services.py` — nenhuma chamada manual via `requests` é feita
  para a API do Gemini.
- Toda a chamada acontece **no backend**; a chave `GEMINI_API_KEY` nunca
  aparece no HTML, no JavaScript enviado ao navegador, nem em nenhum log de
  frontend.
- O prompt de sistema (`assistant/prompt.py`) inclui o conteúdo integral do
  trabalho acadêmico como contexto, para que a IA possa responder perguntas
  sobre o próprio trabalho sem inventar dados. Diferente da API da OpenAI,
  a Gemini API não usa uma mensagem de papel "system": o prompt é passado
  via `system_instruction` em `GenerateContentConfig`, e o papel do
  assistente nos turnos da conversa é `"model"` (traduzido internamente a
  partir do `"assistant"` salvo no banco — os models Django não mudaram).
- Histórico: cada pergunta é enviada junto com as últimas 30 mensagens da
  conversa (`AI_CONVERSATION_HISTORY_LIMIT`), para manter contexto entre
  perguntas na mesma conversa.
- Tratamento de erros usando as exceções específicas do SDK oficial
  (`google.genai.errors.ClientError` para respostas 4xx — diferenciando
  401/403, 429 e 404 pelo atributo `.code` —, `google.genai.errors.ServerError`
  para 5xx, `google.genai.errors.APIError` como base genérica, e
  `httpx.HTTPError` para falhas de conexão/timeout do transporte usado
  internamente pelo SDK), sempre traduzidas para mensagens amigáveis e
  nunca expondo a chave ou detalhes internos:
  - limite de requisições (429) → "Muitas perguntas em sequência. Aguarde alguns segundos.";
  - chave inválida/sem permissão (401/403) → "O serviço de IA está temporariamente indisponível para este projeto.";
  - erro no servidor do Gemini (5xx) → "O serviço de IA está temporariamente indisponível. Tente novamente em instantes.";
  - qualquer outra falha (rede, modelo inexistente, resposta vazia/bloqueada etc.) → "Não foi possível enviar sua pergunta." (o chat continua funcionando normalmente e o usuário pode tentar de novo).
- Todas as mensagens (pergunta do usuário e resposta da IA) são persistidas
  em `assistant.Message`, vinculadas à `assistant.Conversation` do usuário
  autenticado.
- **Autorização:** todo endpoint de conversa filtra sempre por
  `Conversation.objects.filter(id=..., user=request.user)` — nunca apenas
  pelo `id` recebido do JavaScript. Um usuário não consegue ler, responder
  ou excluir conversas de outro usuário (tentativas retornam `404`).

## Integração com a Brevo (e-mail)

Usa o **SDK oficial da Brevo** (`pip install brevo-python`, `import brevo`)
em `accounts/emailing.py` — nenhuma chamada manual via `requests` é feita
para a API da Brevo.

É a única via de entrega do código de recuperação de senha (ver seção
acima). Sem `BREVO_API_KEY`/`BREVO_SENDER_EMAIL` configuradas no `.env`, o
restante do site funciona normalmente, mas o fluxo de "esqueci minha senha"
retorna erro ao tentar enviar o código (nunca usa o código como fallback
visível).

Erros específicos da API são tratados via as exceções do SDK oficial
(`brevo.UnauthorizedError` — 401, `brevo.ForbiddenError` — 403,
`brevo.TooManyRequestsError` — 429, `brevo.BadRequestError` — 400,
`brevo.InternalServerError` — 500, `brevo.core.api_error.ApiError` como
base genérica, e `httpx.HTTPError` para falhas de conexão/timeout do
transporte HTTP usado internamente pelo SDK), todos logados no servidor
para diagnóstico e nunca expostos ao usuário final.

## Páginas e rotas

| Rota                         | Descrição                                   | Protegida |
|-------------------------------|----------------------------------------------|:---------:|
| `/`                            | Login                                        | não       |
| `/cadastro/`                   | Criar conta                                  | não       |
| `/recuperar-senha/`            | Recuperação de senha (3 etapas)              | não       |
| `/apresentacao/`               | Identificação acadêmica / capa               | sim       |
| `/conceito/`                   | Conceito da área                             | sim       |
| `/conceitos/`                  | Principais conceitos estudados               | sim       |
| `/competencias/`               | Competências para começar                    | sim       |
| `/porta-de-entrada/`           | Porta de entrada na área (estágio → sênior)  | sim       |
| `/brasil/`                     | A área no Brasil (LinkedIn + Brasscom)       | sim       |
| `/surpreendeu/`                | O que surpreendeu a equipe                   | sim       |
| `/ia/`                         | Chat com o assistente de IA                  | sim       |
| `/admin/`                      | Django Admin                                 | sim (staff) |

Endpoints JSON do chat (todos exigem login e validam o dono da conversa):

```
GET    /ia/api/conversas/
POST   /ia/api/conversas/
DELETE /ia/api/conversas/<uuid>/
GET    /ia/api/conversas/<uuid>/mensagens/
POST   /ia/api/perguntar/
```

Endpoints JSON da recuperação de senha:

```
POST /recuperar-senha/solicitar-codigo/
POST /recuperar-senha/verificar-codigo/
POST /recuperar-senha/redefinir/
```

## Assets / imagens

Os arquivos SVG/CSS/fontes do projeto original foram portados. **Cinco
imagens** (logo UNIPÊ em duas variantes, dois prints de busca no LinkedIn e
o mapa/infográfico da Brasscom) eram hospedadas no CDN interno do Lovable e
não estavam disponíveis no repositório entregue — por isso, **placeholders
gerados localmente** (com o mesmo tamanho/proporção esperados pelo layout)
foram colocados em `static/img/`, claramente identificados como
"IMAGEM ILUSTRATIVA — SUBSTITUIR":

```
static/img/unipe-logo.png          (logo institucional — fundo claro)
static/img/unipe-logo-light.png    (logo institucional — fundo escuro/sidebar)
static/img/linkedin-brasil.png     (print: busca de vagas back-end no Brasil)
static/img/linkedin-paraiba.png    (print: busca de vagas back-end na Paraíba)
static/img/brasscom-mapa.png       (mapa/infográfico do relatório Brasscom)
```

**Para restaurar a fidelidade visual total**, basta substituir esses 5
arquivos pelos originais (mesmo nome de arquivo, em `static/img/`) —
nenhuma alteração de código é necessária. O favicon (`favicon.png`) já é o
arquivo original, pois estava presente no repositório.

## Configuração das APIs externas

O projeto tem duas integrações externas, ambas via SDK oficial e ambas
opcionais no sentido de que **o restante do site funciona normalmente sem
elas** — só a funcionalidade específica de cada uma fica indisponível.

### `GEMINI_API_KEY` / `GEMINI_MODEL` — necessárias para a IA

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
```

- Sem essa chave, todas as páginas continuam funcionando normalmente; só o
  chat de IA (`/ia/`) retorna a mensagem "Não foi possível enviar sua
  pergunta." ao tentar responder.
- Gere a chave gratuitamente no **Google AI Studio**, em
  <https://aistudio.google.com/apikey>, e cole em `GEMINI_API_KEY` no
  `.env` (nunca no código).
- `GEMINI_MODEL` aceita qualquer modelo de texto disponível na Gemini API.
  O padrão do projeto é `gemini-3.6-flash` — um modelo **estável (GA)**,
  com bom equilíbrio entre qualidade de resposta, latência e custo,
  adequado para um chatbot de texto (evite apontar para modelos com sufixo
  `-preview`/`-experimental`, que não têm garantia de disponibilidade).
  Para trocar o modelo no futuro, basta alterar essa variável no `.env` —
  nenhuma alteração de código é necessária.

### `BREVO_API_KEY` / `BREVO_SENDER_EMAIL` / `BREVO_SENDER_NAME` — necessárias para a recuperação de senha

```env
BREVO_API_KEY=
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=Desenvolvimento Back-end — UNIPÊ
```

- Sem essas variáveis, cadastro, login, logout, IA e todas as páginas de
  conteúdo continuam funcionando normalmente; só o fluxo de "esqueci minha
  senha" retorna erro ao tentar enviar o código (ele nunca é exibido na
  tela como alternativa).
- Crie uma conta em <https://www.brevo.com>, gere uma chave de API
  transacional em **SMTP & API → API Keys**, e cole em `BREVO_API_KEY`.
- `BREVO_SENDER_EMAIL` precisa ser um remetente **validado** na sua conta
  Brevo (Brevo exige verificação de domínio ou de remetente antes de
  permitir o envio — sem isso, a API responde `403 Forbidden` e o backend
  trata esse erro corretamente, sem enviar o e-mail nem mentir sucesso).
- `BREVO_SENDER_NAME` é apenas o nome de exibição do remetente.

## Deploy no PythonAnywhere

Passo a passo para publicar este projeto em uma conta do
[PythonAnywhere](https://www.pythonanywhere.com/).

1. **Criar a conta** em pythonanywhere.com (o plano gratuito já é
   suficiente para rodar o projeto; contas gratuitas têm uma allowlist de
   acesso externo — se `GEMINI_API_KEY`/`BREVO_API_KEY` não funcionarem em
   um plano gratuito, verifique se `generativelanguage.googleapis.com` e `api.brevo.com`
   precisam ser liberados nessa allowlist, ou considere um plano pago, que
   tem acesso externo irrestrito).

2. **Enviar o código** — pela aba **Files**, faça upload do `.zip` deste
   projeto e extraia-o (ou clone via `git clone` em um **Bash console**, se
   o projeto estiver em um repositório Git), preferencialmente em
   `/home/SEU_USUARIO/academy-ascii-django`.

3. **Criar um virtualenv** em um **Bash console**:
   ```bash
   cd ~/academy-ascii-django
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   (troque `python3.12` pela versão de Python disponível na sua conta, se
   necessário).

4. **Criar a Web App** — aba **Web** → **Add a new web app** → escolha
   **Manual configuration** (não escolha o wizard automático de Django) →
   selecione a mesma versão de Python do virtualenv criado.

5. **Configurar o virtualenv da Web App** — na seção **Virtualenv** da aba
   **Web**, informe o caminho completo, ex.:
   `/home/SEU_USUARIO/academy-ascii-django/venv`.

6. **Criar o `.env` de produção** — pela aba **Files**, crie
   `/home/SEU_USUARIO/academy-ascii-django/.env` a partir do
   `.env.example`, preenchendo com valores reais:
   ```env
   SECRET_KEY=gere-uma-chave-aleatoria-longa-e-secreta
   DEBUG=False
   ALLOWED_HOSTS=SEU_USUARIO.pythonanywhere.com
   CSRF_TRUSTED_ORIGINS=https://SEU_USUARIO.pythonanywhere.com
   SECURE_SSL_REDIRECT=False
   GEMINI_API_KEY=sua-chave-real-do-gemini
   GEMINI_MODEL=gemini-3.6-flash
   BREVO_API_KEY=sua-chave-real-da-brevo
   BREVO_SENDER_EMAIL=remetente-verificado@seudominio.com
   BREVO_SENDER_NAME=Desenvolvimento Back-end — UNIPÊ
   ```
   (gere uma `SECRET_KEY` forte com, por exemplo,
   `python -c "import secrets; print(secrets.token_urlsafe(50))"`).

7. **Rodar as migrations** no mesmo Bash console (com o virtualenv ativo):
   ```bash
   python manage.py migrate
   ```

8. **Rodar o `collectstatic`**:
   ```bash
   python manage.py collectstatic --noinput
   ```
   Isso reúne todo o CSS/JS/imagens em `staticfiles/`.

9. **Configurar o WSGI** — aba **Web** → link do arquivo WSGI (algo como
   `/var/www/seuusuario_pythonanywhere_com_wsgi.py`) → apague o conteúdo de
   exemplo e substitua por:
   ```python
   import os
   import sys

   path = "/home/SEU_USUARIO/academy-ascii-django"
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

   from config.wsgi import application
   ```
   (o projeto já inclui um `config/wsgi.py` padrão do Django — não é
   necessário criar nem modificar esse arquivo, apenas apontar para ele).

10. **Configurar arquivos estáticos** — na seção **Static files** da aba
    **Web**, adicione um mapeamento:
    - **URL:** `/static/`
    - **Directory:** `/home/SEU_USUARIO/academy-ascii-django/staticfiles`

11. **(Opcional) Criar um superusuário** para acessar `/admin/`:
    ```bash
    python manage.py createsuperuser
    ```

12. **Recarregar a Web App** — botão verde **Reload** no topo da aba
    **Web**.

13. **Verificar o domínio** — acesse
    `https://SEU_USUARIO.pythonanywhere.com/` e confirme que a tela de
    login aparece corretamente, com CSS e imagens carregando.

14. **Verificar os logs** em caso de erro — aba **Web** → **Log files**
    (`Error log` mostra exceções do Django/WSGI; `Server log` mostra
    problemas de nível mais baixo do servidor).

15. **Testar os fluxos completos** já em produção: cadastro, login,
    páginas protegidas, chat de IA (com `GEMINI_API_KEY` real) e
    recuperação de senha (com `BREVO_API_KEY` real e um remetente
    validado) — só nesse ambiente é possível validar de fato as chamadas
    ao Gemini e à Brevo, já que muitos ambientes de desenvolvimento/sandbox
    bloqueiam acesso direto a `generativelanguage.googleapis.com`/`api.brevo.com`.

**Notas importantes:**
- Nunca defina `DEBUG=True` na Web App de produção.
- `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` já são lidos do `.env`
  (`config/settings.py`) — não é necessário editar código Python para
  apontar para o domínio do PythonAnywhere, apenas o `.env`.
- O banco continua sendo SQLite (`db.sqlite3`, criado junto ao projeto na
  primeira `migrate`) — nenhum PostgreSQL/MySQL é necessário.
- Sempre que atualizar o código (novo upload/`git pull`), rode novamente
  `migrate` e `collectstatic` se houver mudanças de modelo ou de estáticos,
  e clique em **Reload** na aba **Web**.

## Estrutura de diretórios

```
academy-ascii-django/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/                    # settings, urls, wsgi/asgi
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                  # usuário, login, cadastro, recuperação de senha
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── validators.py
│   └── emailing.py
│
├── presentation/               # conteúdo acadêmico + 7 páginas + nav da sidebar
│   ├── content.py
│   ├── context_processors.py
│   ├── views.py
│   └── urls.py
│
├── assistant/                  # conversas, mensagens, IA
│   ├── models.py
│   ├── prompt.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── app_base.html           # shell com sidebar + drawer mobile
│   ├── 404.html
│   ├── 500.html
│   ├── accounts/
│   ├── presentation/
│   ├── assistant/
│   └── partials/                # sidebar, InfoCard, DocImage, Callout
│
└── static/
    ├── css/styles.css           # tokens de design (OKLCH), utilitários
    ├── js/                      # app.js, toast.js, ia.js
    └── img/                     # logos, prints, favicon
```

## Diferenças conscientes em relação ao original

Por instrução explícita do escopo desta migração, alguns pontos de
**tecnologia** (não de comportamento visível) foram conscientemente
adaptados, sempre preservando o resultado final para o usuário:

- **Frontend:** React/TanStack Start → Django Templates + JavaScript puro.
  As mesmas classes utilitárias (Tailwind) foram reaproveitadas via CDN,
  configurado para usar os mesmos tokens de cor/raio do CSS original.
- **Autenticação/banco:** Supabase (Postgres + Auth) → modelo de usuário
  customizado do Django + SQLite. O comportamento (login por e-mail, hash
  de senha, sessão) é equivalente.
- **IA:** gateway de IA da Lovable (Gemini) → SDK oficial do Google Gemini
  (`from google import genai`, `genai.Client(...)`, modelo padrão
  `gemini-3.6-flash`), usado diretamente em vez de através de um gateway
  intermediário. O projeto passou por uma etapa intermediária usando a API
  da OpenAI antes desta migração final para o Gemini; nenhum resquício
  dessa etapa permanece no código. O prompt de sistema, o histórico e o
  tratamento de erros foram preservados.
- **Recuperação de senha:** o comportamento original do Lovable exibia o
  código diretamente na tela (projeto sem provedor de e-mail configurado).
  Nesta versão Django, por exigência explícita de segurança do
  responsável pelo projeto, esse comportamento foi **substituído**: o
  código nunca é exposto ao frontend e é entregue exclusivamente por
  e-mail via SDK oficial da Brevo (`import brevo`). Essa é a única
  divergência funcional (não apenas tecnológica) desta migração em
  relação ao comportamento original, e foi feita deliberadamente.
- **Assets faltantes:** 5 imagens hospedadas fora do repositório original
  foram substituídas por placeholders locais (ver seção
  [Assets](#assets--imagens)) até que os arquivos reais sejam fornecidos.

Nenhuma funcionalidade do projeto original foi removida, resumida ou
substituída por uma versão simplificada, exceto a exibição do código de
recuperação de senha na tela, deliberadamente removida por motivo de
segurança conforme instrução explícita.
