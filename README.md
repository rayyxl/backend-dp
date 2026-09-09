# Desenvolvimento Back-end — Apresentação UNIPÊ

Réplica funcional e visual, em **Python + Django**, do projeto acadêmico
originalmente gerado com **Lovable** (React 19 + TanStack Start + Supabase),
disponível em `academy-ascii`. O objetivo desta versão é reproduzir o mais
fielmente possível a experiência do usuário do projeto original — layout,
cores, tipografia, fluxos de navegação e funcionalidades — usando uma stack
100% Django.

> **Aplicação publicada:** https://backend-dp-umber.vercel.app/
> Hospedada na **Vercel**, com banco de dados **Supabase** (PostgreSQL
> gerenciado).

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
- [Deploy na Vercel](#deploy-na-vercel)
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

A aplicação está publicada na **Vercel** e usa o **Supabase** (PostgreSQL
gerenciado) como banco de dados, tanto em desenvolvimento quanto em
produção. Acesso: **https://backend-dp-umber.vercel.app/**.

## Arquitetura

- **Backend:** Django (views + `JsonResponse`, sem Django REST Framework —
  não era necessário para o volume de endpoints do projeto).
- **Frontend:** Django Templates + Tailwind CSS (via CDN, configurado para
  usar exatamente os mesmos tokens de cor/raio do projeto original) + CSS
  próprio (`static/css/styles.css`) + JavaScript puro (sem framework).
- **Banco de dados:** **Supabase** (PostgreSQL gerenciado), acessado
  diretamente via `DATABASE_URL` (driver `psycopg`/`psycopg2`, sem uso do
  SDK/Auth da Supabase). O uso do Supabase é necessário porque a aplicação
  roda na Vercel como funções serverless, sem sistema de arquivos
  persistente — um banco local como SQLite não seria viável em produção.
- **Hospedagem:** **Vercel** (deploy automático a cada `git push`).
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
Equivale à junção de `auth.users` + `public.profiles` do Supabase Auth no
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

Todos esses models são persistidos no **Supabase** (PostgreSQL), tanto em
desenvolvimento quanto em produção.

O conteúdo acadêmico (textos, dados da Brasscom, etc.) **não** é modelado em
banco de dados porque, no projeto original, também é conteúdo estático
embutido no frontend (`src/content/presentation.ts`) — aqui ele foi portado
integralmente para `presentation/content.py`, mantendo o mesmo texto.

## Instalação

Antes de começar, crie um projeto gratuito em [supabase.com](https://supabase.com)
e copie a *connection string* do banco (aba **Project Settings → Database**,
formato `postgresql://usuario:senha@host:porta/nome_do_banco`) — ela será
usada como `DATABASE_URL` no passo 4.

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
# edite o .env e preencha SECRET_KEY, DATABASE_URL (connection string do
# Supabase), GEMINI_API_KEY, BREVO_* (opcional)

# 5. Rode as migrations (aplicadas diretamente no Supabase)
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

DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash

BREVO_API_KEY=
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=Desenvolvimento Back-end — UNIPÊ
```

- `SECRET_KEY`: gere uma string aleatória (ex.: `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
- `DATABASE_URL`: connection string do projeto **Supabase** (PostgreSQL) —
  obrigatória tanto em desenvolvimento quanto em produção, já que este
  projeto não usa SQLite. Copie-a em **Project Settings → Database** no
  painel do Supabase.
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
python manage.py migrate          # aplicar migrations no Supabase
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
  SHA-256** é gravado no banco Supabase (`PasswordResetCode.code_hash`) —
  nunca o código em texto puro, nunca em log.
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
  em `assistant.Message` (no Supabase), vinculadas à `assistant.Conversation`
  do usuário autenticado.
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

O projeto tem duas integrações externas opcionais no sentido de que **o
restante do site funciona normalmente sem elas** — só a funcionalidade
específica de cada uma fica indisponível — além da conexão obrigatória com
o Supabase, que é o banco de dados do projeto.

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

### `DATABASE_URL` — obrigatória (banco de dados)

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
```

- Diferente das integrações acima, esta **não é opcional**: sem uma
  `DATABASE_URL` válida apontando para um projeto **Supabase**, a
  aplicação não sobe, pois este projeto não usa SQLite nem qualquer outro
  banco local.
- Crie um projeto gratuito em <https://supabase.com> e copie a connection
  string em **Project Settings → Database**.

## Deploy na Vercel

A aplicação está publicada na Vercel e pode ser acessada em:
**https://backend-dp-umber.vercel.app/**

Como a Vercel executa o Django como **funções serverless**, sem sistema de
arquivos persistente entre invocações, o banco de dados é o **Supabase**
(PostgreSQL gerenciado) tanto em desenvolvimento quanto em produção — não
há `db.sqlite3` neste projeto.

Passo a passo para publicar (ou reproduzir) este deploy:

1. **Criar um projeto no Supabase** — em <https://supabase.com>, crie um
   projeto novo e copie a connection string do banco (aba **Project
   Settings → Database**), no formato
   `postgresql://usuario:senha@host:porta/nome_do_banco`. Esse valor será
   usado como `DATABASE_URL`.

2. **Criar a conta na Vercel** — em <https://vercel.com>, crie uma conta
   (o plano gratuito Hobby é suficiente) e conecte-a ao repositório Git do
   projeto (GitHub/GitLab/Bitbucket).

3. **Importar o projeto** — no dashboard da Vercel, clique em **Add New →
   Project** e selecione o repositório `academy-ascii-django`. A Vercel
   detecta automaticamente que é um projeto Python.

4. **Garantir um `vercel.json`** na raiz do projeto, apontando as
   requisições para o WSGI do Django, por exemplo:
   ```json
   {
     "builds": [
       { "src": "config/wsgi.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/static/(.*)", "dest": "/static/$1" },
       { "src": "/(.*)", "dest": "config/wsgi.py" }
     ]
   }
   ```
   (ajuste os caminhos conforme a versão do builder Python em uso; o
   importante é que toda requisição chegue à `application` exportada por
   `config/wsgi.py`).

5. **Servir os arquivos estáticos** — como a Vercel não mantém um
   `staticfiles/` persistente entre deploys da mesma forma que um servidor
   tradicional, o projeto usa **WhiteNoise** (`pip install whitenoise`,
   middleware adicionado em `config/settings.py`) para servir CSS/JS/
   imagens diretamente pela própria aplicação Django.

6. **Configurar as variáveis de ambiente** — na aba **Settings →
   Environment Variables** do projeto na Vercel, cadastre:
   ```env
   SECRET_KEY=gere-uma-chave-aleatoria-longa-e-secreta
   DEBUG=False
   ALLOWED_HOSTS=backend-dp-umber.vercel.app
   CSRF_TRUSTED_ORIGINS=https://backend-dp-umber.vercel.app
   DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
   GEMINI_API_KEY=sua-chave-real-do-gemini
   GEMINI_MODEL=gemini-3.6-flash
   BREVO_API_KEY=sua-chave-real-da-brevo
   BREVO_SENDER_EMAIL=remetente-verificado@seudominio.com
   BREVO_SENDER_NAME=Desenvolvimento Back-end — UNIPÊ
   ```

7. **Rodar as migrations no Supabase** — como a Vercel não oferece um
   console interativo persistente, rode as migrations localmente (ou em um
   pipeline de CI), apontando `DATABASE_URL` para o mesmo projeto Supabase
   usado em produção:
   ```bash
   export DATABASE_URL="postgresql://usuario:senha@host:porta/nome_do_banco"
   python manage.py migrate
   ```

8. **Fazer o deploy** — qualquer `git push` para a branch conectada
   (normalmente `main`) dispara automaticamente um novo build e deploy na
   Vercel; o progresso pode ser acompanhado na aba **Deployments**.

9. **(Opcional) Criar um superusuário** — como não há shell persistente em
   produção, crie o superusuário localmente (ou via um management command
   executado uma única vez), com `DATABASE_URL` apontando para o Supabase
   de produção:
   ```bash
   python manage.py createsuperuser
   ```

10. **Verificar o domínio** — acesse
    **https://backend-dp-umber.vercel.app/** e confirme que a tela de
    login aparece corretamente, com CSS e imagens carregando.

11. **Verificar os logs em caso de erro** — na aba **Deployments** do
    projeto na Vercel, abra o deploy específico e consulte **Functions /
    Logs** para ver exceções do Django e falhas de build.

12. **Testar os fluxos completos** já em produção: cadastro, login,
    páginas protegidas, chat de IA (com `GEMINI_API_KEY` real) e
    recuperação de senha (com `BREVO_API_KEY` real e um remetente
    validado).

**Notas importantes:**
- Nunca defina `DEBUG=True` no ambiente de produção da Vercel.
- `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` já são lidos das variáveis de
  ambiente (`config/settings.py`) — não é necessário editar código Python
  para apontar para o domínio da Vercel, apenas as variáveis de ambiente
  do projeto.
- O banco é o **Supabase** (PostgreSQL) tanto em desenvolvimento quanto em
  produção — não há arquivo `db.sqlite3` neste projeto.
- Como as funções da Vercel são efêmeras (sem disco persistente entre
  invocações), migrations e criação de superusuário são feitas
  localmente/via CI, sempre apontando para o mesmo Supabase usado em
  produção.
- Sempre que atualizar o código, um novo `git push` já dispara um novo
  deploy automaticamente na Vercel — não há um botão "Reload" manual como
  em outros provedores.

## Estrutura de diretórios

```
academy-ascii-django/
├── manage.py
├── requirements.txt
├── vercel.json                # configuração de build/rotas da Vercel
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
- **Autenticação:** Supabase Auth (projeto original) → autenticação nativa
  do Django, com modelo de usuário customizado (login por e-mail, hash de
  senha PBKDF2, sessão). O comportamento é equivalente.
- **Banco de dados:** continua sendo o **Supabase** em ambas as versões —
  porém, no projeto original, o Supabase era consumido via SDK (Auth +
  Postgres); nesta versão Django, o Supabase é usado apenas como Postgres
  gerenciado, acessado diretamente via `DATABASE_URL`, sem uso do SDK/Auth
  da Supabase.
- **Hospedagem:** ambiente do Lovable → **Vercel** (deploy automático via
  Git, Django rodando como funções serverless), mantendo o mesmo Supabase
  como banco de dados. Aplicação publicada em
  <https://backend-dp-umber.vercel.app/>.
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

Nenhuma funcionalidade do projeto original foi removida, resumida ou
substituída por uma versão simplificada, exceto a exibição do código de
recuperação de senha na tela, deliberadamente removida por motivo de
segurança conforme instrução explícita.
