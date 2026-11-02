/* Assetify: glue between HTMX, Preline, toasts and the select-one tables. */
(function () {
  "use strict";

  var MODAL = "#app-modal";

  function initPreline() {
    if (window.HSStaticMethods && window.HSStaticMethods.autoInit) {
      window.HSStaticMethods.autoInit();
    }
  }

  function modalEl() {
    return document.querySelector(MODAL);
  }

  function openModal() {
    var el = modalEl();
    if (!el || !window.HSOverlay) return;
    if (!el.classList.contains("open")) window.HSOverlay.open(el);
  }

  function closeModal() {
    var el = modalEl();
    if (el && window.HSOverlay && el.classList.contains("open")) window.HSOverlay.close(el);
  }

  var TOAST_STYLES = {
    success: "border-emerald-200 bg-emerald-50 text-emerald-800",
    error: "border-red-200 bg-red-50 text-red-800",
    info: "border-sky-200 bg-sky-50 text-sky-800",
  };

  function showToast(detail) {
    var area = document.getElementById("toast-area");
    if (!area || !detail || !detail.message) return;
    var type = TOAST_STYLES[detail.type] ? detail.type : "info";
    var el = document.createElement("div");
    el.setAttribute("role", type === "error" ? "alert" : "status");
    el.className =
      "flex items-start gap-3 rounded-xl border p-3 shadow-lg text-sm " + TOAST_STYLES[type];
    var text = document.createElement("div");
    text.className = "grow";
    text.textContent = detail.message;
    var close = document.createElement("button");
    close.type = "button";
    close.setAttribute("aria-label", "Dismiss");
    close.className = "opacity-60 hover:opacity-100";
    close.textContent = "✕";
    close.addEventListener("click", function () { el.remove(); });
    el.appendChild(text);
    el.appendChild(close);
    area.appendChild(el);
    setTimeout(function () { el.remove(); }, type === "error" ? 8000 : 5000);
  }

  // --- single-select tables (check-in / check-out) ---
  function actionButton() { return document.getElementById("action-btn"); }

  function resetSelection() {
    var btn = actionButton();
    if (!btn) return;
    btn.disabled = true;
    delete btn.dataset.selected;
  }

  document.addEventListener("change", function (e) {
    var box = e.target.closest && e.target.closest("input.row-select");
    if (!box) return;
    var btn = actionButton();
    if (box.checked) {
      document.querySelectorAll("input.row-select").forEach(function (other) {
        if (other !== box) other.checked = false;
      });
      if (btn) { btn.dataset.selected = box.dataset.id; btn.disabled = false; }
    } else {
      resetSelection();
    }
  });

  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("#action-btn");
    if (!btn || btn.disabled || !btn.dataset.selected) return;
    var url = btn.dataset.url.replace("{id}", btn.dataset.selected);
    window.htmx.ajax("GET", url, { target: "#modal-body", swap: "innerHTML" });
  });

  // --- HTMX wiring ---
  document.body.addEventListener("toast", function (e) { showToast(e.detail); });
  document.body.addEventListener("closeModal", closeModal);

  document.body.addEventListener("htmx:afterSwap", function (e) {
    initPreline();
    var target = e.detail.target;
    if (target && target.id === "modal-body") openModal();
    if (target && target.id === "select-rows") resetSelection();
  });

  // Let 422 (validation error) responses swap in so forms re-render with inline errors.
  document.body.addEventListener("htmx:beforeSwap", function (e) {
    if (e.detail.xhr.status === 422) {
      e.detail.shouldSwap = true;
      e.detail.isError = false;
    }
  });

  document.body.addEventListener("htmx:responseError", function (e) {
    var status = e.detail.xhr.status;
    if (status === 422) return;
    var rid = e.detail.xhr.getResponseHeader("X-Request-ID");
    var msg = status === 403 ? "You are not allowed to do that."
      : status === 404 ? "That item no longer exists."
      : "Something went wrong. Please try again.";
    showToast({ type: "error", message: msg + (rid ? " (ref " + rid + ")" : "") });
  });

  document.body.addEventListener("htmx:sendError", function () {
    showToast({ type: "error", message: "Network error. Check your connection and try again." });
  });

  document.addEventListener("DOMContentLoaded", function () {
    initPreline();
    var data = document.getElementById("flash-data");
    if (data) {
      try { JSON.parse(data.textContent).forEach(showToast); } catch (err) { /* no flashes */ }
    }
  });
})();
