(() => {
  const buttons = [...document.querySelectorAll("[data-filter]")];
  const sections = [...document.querySelectorAll("[data-phase-section]")];
  const visibleCount = document.getElementById("visible-count");
  function show(stage) {
    buttons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.filter === stage)));
    let count = 0;
    sections.forEach(section => {
      const visible = stage === "all" || section.dataset.phaseSection === stage;
      section.hidden = !visible;
      if (visible) count += section.querySelectorAll(".work-row").length;
    });
    if (visibleCount) visibleCount.textContent = String(count);
  }
  buttons.forEach(button => button.addEventListener("click", () => show(button.dataset.filter)));
  show("all");
})();