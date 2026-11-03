/* Assetify: glue between HTMX, Preline plugins, toasts and the select-one tables. */
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

  // --- toasts: markup follows docs/preline/toasts.html (default toast) ---
  var TOAST_ICON = {
    success: { cls: "text-teal-500", path: "M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z" },
    error: { cls: "text-red-500", path: "M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z" },
    info: { cls: "text-primary", path: "M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z" },
  };
  var SVG_NS = "http://www.w3.org/2000/svg";

  function showToast(detail) {
    var area = document.getElementById("toast-area");
    if (!area || !detail || !detail.message) return;
    var type = TOAST_ICON[detail.type] ? detail.type : "info";

    var el = document.createElement("div");
    el.className = "max-w-xs w-full p-4 bg-layer border border-layer-line rounded-xl shadow-lg";
    el.setAttribute("role", "alert");
    el.setAttribute("tabindex", "-1");

    var row = document.createElement("div");
    row.className = "flex gap-x-3";

    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "shrink-0 size-4 mt-0.5 " + TOAST_ICON[type].cls);
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("fill", "currentColor");
    svg.setAttribute("aria-hidden", "true");
    var path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", TOAST_ICON[type].path);
    svg.appendChild(path);

    var text = document.createElement("div");
    text.className = "grow";
    var p = document.createElement("p");
    p.className = "text-sm text-layer-foreground";
    p.textContent = detail.message;
    text.appendChild(p);

    row.appendChild(svg);
    row.appendChild(text);
    el.appendChild(row);
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
    if (btn && !btn.disabled && btn.dataset.selected) {
      window.htmx.ajax("GET", btn.dataset.url.replace("{id}", btn.dataset.selected), {
        target: "#modal-body",
        swap: "innerHTML",
      });
      return;
    }
    var cancel = e.target.closest && e.target.closest("[data-inline-cancel]");
    if (cancel) {
      var slot = document.getElementById("inline-slot");
      if (slot) slot.innerHTML = "";
    }
  });

  // Plain-form confirmation (data-confirm="message")
  document.addEventListener("submit", function (e) {
    var msg = e.target.getAttribute && e.target.getAttribute("data-confirm");
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  // --- HTMX wiring ---
  document.body.addEventListener("toast", function (e) { showToast(e.detail); });
  document.body.addEventListener("closeModal", closeModal);

  // Re-initialise Preline plugins after every swap settles, then open the modal if it was the target.
  document.body.addEventListener("htmx:afterSettle", function (e) {
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
