(() => {
  const scenarios = {
    ask: {
      label: "01 / ASK",
      heading: "What's next?",
      description: "Get a quick answer from your connected AI.",
      action: "HOLD TO SPEAK",
      detail: "Hold a key, ask a question, and hear or read a reply from the AI connected to your computer."
    },
    capture: {
      label: "02 / CAPTURE",
      heading: "Keep that thought.",
      description: "Record an idea before it disappears.",
      action: "HOLD TO CAPTURE",
      detail: "Save a quick voice note for later. Automatic tasks and reminders are still being developed."
    },
    approve: {
      label: "03 / APPROVE",
      heading: "Your call.",
      description: "A sensitive agent action needs your decision.",
      action: "REVIEW → APPROVE / DENY",
      detail: "See an action request and choose what happens. The complete NOD approval flow is still being tested."
    }
  };
  const buttons = [...document.querySelectorAll("[data-preview]")];
  function switchTo(name) {
    const item = scenarios[name];
    if (!item) return;
    const put = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    put("display-label", item.label);
    put("display-heading", item.heading);
    put("display-description", item.description);
    put("display-action", item.action);
    put("preview-copy", item.detail);
    buttons.forEach(button => {
      const selected = button.dataset.preview === name;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-selected", String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    const panel = document.getElementById("preview-detail");
    if (panel) panel.setAttribute("aria-labelledby", "tab-" + name);
  }
  buttons.forEach((button, index) => {
    button.addEventListener("click", () => switchTo(button.dataset.preview));
    button.addEventListener("keydown", event => {
      const count = buttons.length;
      let target;
      if (event.key === "ArrowRight" || event.key === "ArrowDown") target = (index + 1) % count;
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") target = (index + count - 1) % count;
      else if (event.key === "Home") target = 0;
      else if (event.key === "End") target = count - 1;
      else return;
      event.preventDefault();
      switchTo(buttons[target].dataset.preview);
      buttons[target].focus();
    });
  });
})();
