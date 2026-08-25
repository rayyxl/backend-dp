/**
 * JS global da aplicação: inicializa os ícones Lucide, expõe um helper de
 * fetch com CSRF (equivalente ao cliente Supabase autenticado por sessão
 * do projeto original) e controla o drawer mobile do sidebar.
 */

function getCsrfToken() {
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input) return input.value;
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : "";
}

async function apiFetch(url, options = {}) {
  const headers = Object.assign(
    {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
      "X-Requested-With": "XMLHttpRequest",
    },
    options.headers || {},
  );
  const response = await fetch(url, Object.assign({}, options, { headers }));
  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  if (!response.ok) {
    const message = (data && data.error) || "Ocorreu um erro. Tente novamente.";
    throw new Error(message);
  }
  return data;
}

function refreshIcons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  refreshIcons();

  // Mensagem de sucesso passada de uma página para outra via redirect
  // completo (ex.: após redefinir a senha em /recuperar-senha/).
  const flash = sessionStorage.getItem("flash_success");
  if (flash && window.toast) {
    sessionStorage.removeItem("flash_success");
    window.toast.success(flash);
  }

  const openBtn = document.querySelector("[data-mobile-menu-open]");
  const closeBtn = document.querySelector("[data-mobile-menu-close]");
  const drawer = document.querySelector("[data-mobile-drawer]");

  if (openBtn && drawer) {
    openBtn.addEventListener("click", () => drawer.classList.remove("hidden"));
  }
  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => drawer.classList.add("hidden"));
  }
});
