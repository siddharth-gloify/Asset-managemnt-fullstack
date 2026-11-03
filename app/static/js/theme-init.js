/* Applies the saved theme before first paint (official Preline snippet, docs/preline/dark-mode.html).
   Defaults to light the first time; the header toggle switches via Preline's theme switch. */
(function () {
  if (!localStorage.getItem("hs_theme")) localStorage.setItem("hs_theme", "light");
  const html = document.querySelector("html");
  const isLightOrAuto =
    localStorage.getItem("hs_theme") === "light" ||
    (localStorage.getItem("hs_theme") === "auto" && !window.matchMedia("(prefers-color-scheme: dark)").matches);
  const isDarkOrAuto =
    localStorage.getItem("hs_theme") === "dark" ||
    (localStorage.getItem("hs_theme") === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  if (isLightOrAuto && html.classList.contains("dark")) html.classList.remove("dark");
  else if (isDarkOrAuto && html.classList.contains("light")) html.classList.remove("light");
  else if (isDarkOrAuto && !html.classList.contains("dark")) html.classList.add("dark");
  else if (isLightOrAuto && !html.classList.contains("light")) html.classList.add("light");
})();
