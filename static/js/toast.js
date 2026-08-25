/**
 * Réplica minimalista do <Toaster richColors position="top-center" /> (sonner)
 * usado no projeto original para toast.success(...) / toast.error(...).
 */
(function () {
  function show(message, variant) {
    const root = document.getElementById("toast-root");
    if (!root) return;

    const colors = {
      success: "border-transparent bg-[oklch(0.62_0.15_150)] text-white",
      error: "border-transparent bg-destructive text-destructive-foreground",
    };

    const el = document.createElement("div");
    el.className =
      "card-soft pointer-events-auto rounded-lg px-4 py-3 text-sm font-medium shadow-[var(--shadow-lift)] " +
      (colors[variant] || "");
    el.textContent = message;
    root.appendChild(el);

    requestAnimationFrame(() => {
      el.style.transition = "opacity .2s ease, transform .2s ease";
      el.style.opacity = "1";
    });

    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateY(-6px)";
      setTimeout(() => el.remove(), 200);
    }, 3600);
  }

  window.toast = {
    success: (message) => show(message, "success"),
    error: (message) => show(message, "error"),
  };
})();
