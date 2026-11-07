// Closes the mobile menu after a link is chosen, so in-page jumps are not hidden behind it.
document.querySelectorAll(".mobile-menu a").forEach(link =>
  link.addEventListener("click", () => link.closest("details").removeAttribute("open")));

// Hero film: plays muted only while on screen, never for people who ask for reduced motion
// (they get the poster). Controls are always shown; once someone pauses it, it stays paused.
const still = window.matchMedia("(prefers-reduced-motion: reduce)");
document.querySelectorAll("video[data-autoplay]").forEach(video => {
  if (still.matches || !("IntersectionObserver" in window)) return;
  let visible = false;
  const watcher = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) video.play().catch(() => {}); else video.pause();
  }, { threshold: 0.4 });
  video.addEventListener("pause", () => { if (visible) watcher.disconnect(); });
  watcher.observe(video);
});

// Waitlist form: builds a mailto link from the fields so the form works as a real signup
// while we build automated backend integration. The email includes name, message and consent.
document.getElementById("waitlist-form")?.addEventListener("submit", function (e) {
  e.preventDefault();
  const name = this.querySelector('input[name="name"]').value.trim();
  const email = this.querySelector('input[name="email"]').value.trim();
  const consent = this.querySelector('input[name="consent"]').checked;
  if (!name || !email || !consent) return;
  const subject = encodeURIComponent("NOD launch updates — " + name);
  const body = encodeURIComponent(
    "Hi,\n\nPlease keep me updated about NOD.\n\nName: " + name +
    "\nEmail: " + email +
    "\n\nI consent to receiving NOD updates by email.\n\n" +
    "(This is a pre-addressed email. An automated signup is coming.)"
  );
  window.location.href = "mailto:info@mazworks.uk?subject=" + subject + "&body=" + body;
  this.querySelector(".waitlist-status").textContent = "✓ Email app opened. Send the message and you are on the list.";
  this.querySelector(".waitlist-status").classList.add("ok");
});
