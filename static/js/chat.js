// Litechat chat page behaviour. No framework; progressive enhancement over server-rendered HTML.
(function () {
  "use strict";

  // ---- Sidebar toggle (phones) ----
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    const setOpen = (open) => {
      sidebar.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };
    toggle.addEventListener("click", () => setOpen(!sidebar.classList.contains("open")));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && sidebar.classList.contains("open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }
})();
