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

/* Proposed experience switcher. This is a concept illustration, not a live API. */
(() => {
  const concepts = {
    learn: {
      overline: "CONCEPT 01 / YOUR VIDEO LIBRARY",
      heading: "Your saved videos.<br><em>Finally useful.</em>",
      text: "Instead of just saving a Reel, imagine searching what was said, shown and demonstrated—then asking NOD to turn the best parts into a useful brief.",
      steps: ["Import an accessible video", "Understand speech, scenes and text", "Ask NOD, with original sources"],
      badge: "KNOWLEDGE CARD", title: "A lesson worth keeping.",
      line1: "What was shown, explained and why it matters",
      line2: "Original video + timestamps retained", action: "ASK NOD ABOUT THIS"
    },
    make: {
      overline: "CONCEPT 02 / REEL TO 3D PRINT",
      heading: "Find the file.<br><em>Make the thing.</em>",
      text: "Spot a useful 3D print in a video. NOD could search for a legitimately shared STL/3MF, verify the match, prepare a slice and let you choose when to print.",
      steps: ["Identify the creator and candidate model", "Confirm file, licence and printer profile", "Preview the slice and approve the start"],
      badge: "PRINT PREPARATION", title: "Matched model found?",
      line1: "Verify original STL/3MF against the video",
      line2: "Printer check + slice preview before start", action: "REVIEW MODEL & PRINT"
    }
  };
  const buttons = Array.from(document.querySelectorAll("[data-future]"));
  const panel = document.getElementById("future-panel");
  const targets = {
    overline: document.getElementById("future-overline"),
    heading: document.getElementById("future-heading"),
    text: document.getElementById("future-text"),
    steps: document.getElementById("future-steps"),
    badge: document.getElementById("future-art-badge"),
    title: document.getElementById("future-art-title"),
    line1: document.getElementById("future-art-line1"),
    line2: document.getElementById("future-art-line2"),
    action: document.getElementById("future-art-action")
  };
  function setConcept(name) {
    const item = concepts[name];
    if (!item || !panel || Object.values(targets).some(x => !x)) return;
    targets.overline.textContent = item.overline;
    targets.heading.innerHTML = item.heading; // static authored strings only, never user HTML
    targets.text.textContent = item.text;
    targets.steps.replaceChildren(...item.steps.map((step, i) => {
      const li = document.createElement("li");
      const number = document.createElement("span");
      number.textContent = String(i + 1).padStart(2, "0");
      li.append(number, document.createTextNode(step));
      return li;
    }));
    ["badge","title","line1","line2","action"].forEach(key => { targets[key].textContent = item[key]; });
    buttons.forEach(button => {
      const active = button.dataset.future === name;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
      button.tabIndex = active ? 0 : -1;
    });
    panel.setAttribute("aria-labelledby", "future-tab-" + name);
  }
  buttons.forEach((button, i) => {
    button.addEventListener("click", () => setConcept(button.dataset.future));
    button.addEventListener("keydown", ev => {
      let next = i;
      if (ev.key === "ArrowRight" || ev.key === "ArrowDown") next = (i + 1) % buttons.length;
      else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") next = (i - 1 + buttons.length) % buttons.length;
      else if (ev.key === "Home") next = 0;
      else if (ev.key === "End") next = buttons.length - 1;
      else return;
      ev.preventDefault();
      setConcept(buttons[next].dataset.future);
      buttons[next].focus();
    });
  });
})();
