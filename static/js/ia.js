/**
 * Lógica do chat de IA — réplica em JS puro do comportamento de
 * src/routes/_authenticated/ia.tsx (que usava TanStack Query + Supabase).
 *
 * Endpoints Django equivalentes:
 *   GET    /ia/api/conversas/                       -> lista de conversas do usuário logado
 *   POST   /ia/api/conversas/                        -> cria uma nova conversa
 *   DELETE /ia/api/conversas/<id>/                    -> exclui uma conversa (só se for do usuário)
 *   GET    /ia/api/conversas/<id>/mensagens/          -> lista de mensagens da conversa
 *   POST   /ia/api/perguntar/                         -> envia pergunta e recebe resposta da IA
 *
 * A autorização (cada usuário só acessa as próprias conversas) é sempre
 * validada no backend (accounts autenticado via sessão do Django), nunca
 * apenas pelo id enviado pelo JavaScript.
 */
(function () {
  const root = document.querySelector("[data-ia-root]");
  if (!root) return;

  const URLS = {
    conversations: "/ia/api/conversas/",
    conversationDetail: (id) => `/ia/api/conversas/${id}/`,
    messages: (id) => `/ia/api/conversas/${id}/mensagens/`,
    ask: "/ia/api/perguntar/",
  };

  const listEl = document.querySelector("[data-conversation-list]");
  const messagesEl = document.querySelector("[data-messages]");
  const emptyStateEl = document.querySelector("[data-empty-state]");
  const pendingEl = document.querySelector("[data-pending]");
  const scrollAnchor = document.querySelector("[data-scroll-anchor]");
  const askForm = document.querySelector("[data-ask-form]");
  const questionInput = document.querySelector("#question");
  const sendButton = document.querySelector("[data-send-button]");
  const newChatButton = document.querySelector("[data-new-chat]");

  let activeId = null;
  let conversations = [];
  let sending = false;

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function scrollToEnd() {
    scrollAnchor?.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  // ---------------------------------------------------------------------
  // Renderização do histórico (sidebar)
  // ---------------------------------------------------------------------

  function renderConversationList() {
    if (!conversations.length) {
      listEl.innerHTML =
        '<li class="px-3 py-2 text-sm text-muted-foreground">Nenhuma conversa ainda.</li>';
      return;
    }

    listEl.innerHTML = conversations
      .map((conversation) => {
        const active = conversation.id === activeId;
        return `
          <li class="group flex items-center gap-1" data-conversation-item data-id="${conversation.id}">
            <button type="button" data-select-conversation
              class="flex-1 truncate rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                active ? "bg-primary-soft font-medium text-primary" : "text-muted-foreground hover:bg-muted"
              }">
              ${escapeHtml(conversation.title)}
            </button>
            <button type="button" data-delete-conversation aria-label="Excluir conversa ${escapeHtml(conversation.title)}"
              class="rounded-md p-2 text-muted-foreground transition-colors hover:bg-destructive-soft hover:text-destructive">
              <i data-lucide="trash-2" class="size-4"></i>
            </button>
          </li>`;
      })
      .join("");

    refreshIcons();
  }

  // ---------------------------------------------------------------------
  // Renderização das mensagens
  // ---------------------------------------------------------------------

  function renderMessages(messages) {
    messagesEl.querySelectorAll("[data-message]").forEach((el) => el.remove());

    emptyStateEl.classList.toggle("hidden", messages.length > 0);

    const fragmentHtml = messages
      .map((message) => {
        const isUser = message.role === "user";
        return `
          <div class="flex ${isUser ? "justify-end" : "justify-start"}" data-message>
            <div class="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
              isUser ? "bg-primary text-primary-foreground" : "card-soft text-foreground"
            }">${escapeHtml(message.content)}</div>
          </div>`;
      })
      .join("");

    pendingEl.insertAdjacentHTML("beforebegin", fragmentHtml);
    scrollToEnd();
  }

  function setPending(isPending) {
    pendingEl.classList.toggle("hidden", !isPending);
    if (isPending) {
      emptyStateEl.classList.add("hidden");
      scrollToEnd();
    }
  }

  // ---------------------------------------------------------------------
  // Carregamento de dados
  // ---------------------------------------------------------------------

  async function loadConversations() {
    try {
      const data = await apiFetch(URLS.conversations, { method: "GET" });
      conversations = data.conversations || [];
      if (!activeId && conversations.length > 0) {
        activeId = conversations[0].id;
      }
      renderConversationList();
      if (activeId) {
        await loadMessages(activeId);
      } else {
        renderMessages([]);
      }
    } catch (err) {
      window.toast?.error(err.message);
    }
  }

  async function loadMessages(conversationId) {
    try {
      const data = await apiFetch(URLS.messages(conversationId), { method: "GET" });
      renderMessages(data.messages || []);
    } catch (err) {
      window.toast?.error(err.message);
    }
  }

  async function createConversation() {
    const conversation = await apiFetch(URLS.conversations, { method: "POST" });
    conversations = [conversation, ...conversations];
    activeId = conversation.id;
    renderConversationList();
    renderMessages([]);
    return conversation.id;
  }

  // ---------------------------------------------------------------------
  // Ações do usuário
  // ---------------------------------------------------------------------

  newChatButton.addEventListener("click", async () => {
    newChatButton.disabled = true;
    try {
      await createConversation();
    } catch (err) {
      window.toast?.error(err.message);
    } finally {
      newChatButton.disabled = false;
    }
  });

  listEl.addEventListener("click", async (event) => {
    const item = event.target.closest("[data-conversation-item]");
    if (!item) return;
    const id = item.dataset.id;

    if (event.target.closest("[data-delete-conversation]")) {
      try {
        await apiFetch(URLS.conversationDetail(id), { method: "DELETE" });
        conversations = conversations.filter((c) => c.id !== id);
        if (activeId === id) {
          activeId = conversations.length ? conversations[0].id : null;
        }
        renderConversationList();
        if (activeId) {
          await loadMessages(activeId);
        } else {
          renderMessages([]);
        }
        window.toast?.success("Conversa excluída.");
      } catch (err) {
        window.toast?.error(err.message);
      }
      return;
    }

    if (event.target.closest("[data-select-conversation]")) {
      if (id === activeId) return;
      activeId = id;
      renderConversationList();
      await loadMessages(id);
    }
  });

  document.querySelectorAll("[data-suggestion]").forEach((button) => {
    button.addEventListener("click", () => submit(button.textContent.trim()));
  });

  askForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submit(questionInput.value);
  });

  questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit(questionInput.value);
    }
  });

  async function submit(text) {
    const value = (text || "").trim();
    if (!value || sending) return;

    questionInput.value = "";
    sending = true;
    updateSendButton();

    try {
      const conversationId = activeId || (await createConversation());

      // Mostra a pergunta do usuário imediatamente (otimista), como no original.
      renderMessages([
        ...currentRenderedMessages(),
        { role: "user", content: value },
      ]);
      setPending(true);

      const result = await apiFetch(URLS.ask, {
        method: "POST",
        body: JSON.stringify({ conversationId, question: value }),
      });

      setPending(false);
      await Promise.all([loadMessages(conversationId), loadConversations()]);
      void result;
    } catch (err) {
      setPending(false);
      window.toast?.error(err.message || "Não foi possível enviar.");
      await loadMessages(activeId);
    } finally {
      sending = false;
      updateSendButton();
    }
  }

  function currentRenderedMessages() {
    return Array.from(messagesEl.querySelectorAll("[data-message]")).map((el) => {
      const isUser = el.classList.contains("justify-end");
      return { role: isUser ? "user" : "assistant", content: el.textContent.trim() };
    });
  }

  function updateSendButton() {
    sendButton.disabled = sending || !questionInput.value.trim();
    sendButton.querySelector("[data-icon-idle]").classList.toggle("hidden", sending);
    sendButton.querySelector("[data-icon-loading]").classList.toggle("hidden", !sending);
  }

  questionInput.addEventListener("input", updateSendButton);

  // ---------------------------------------------------------------------
  // Inicialização
  // ---------------------------------------------------------------------

  loadConversations();
  updateSendButton();
})();
