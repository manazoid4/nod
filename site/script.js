// Closes the mobile menu after a link is chosen, so in-page jumps are not hidden behind it.
document.querySelectorAll(".mobile-menu a").forEach(link =>
  link.addEventListener("click", () => link.closest("details").removeAttribute("open")));
