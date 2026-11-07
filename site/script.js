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

// Waitlist form: posts to /api/waitlist (Resend). Without JavaScript the form posts natively
// and the API redirects back with ?subscribed=1 or 0, handled below.
const waitlist = document.getElementById("waitlist-form");
const waitlistStatus = waitlist?.querySelector(".waitlist-status");
const setWaitlistStatus = (text, ok) => {
  waitlistStatus.textContent = text;
  waitlistStatus.classList.toggle("ok", ok);
};
waitlist?.addEventListener("submit", async function (e) {
  e.preventDefault();
  const button = this.querySelector("button[type=submit]");
  const data = Object.fromEntries(new FormData(this));
  if (!data.first_name?.trim() || !data.email?.trim() || !data.consent) {
    return setWaitlistStatus("Please add your name, email and tick the box.", false);
  }
  button.disabled = true;
  setWaitlistStatus("Sending...", false);
  try {
    const res = await fetch("/api/waitlist", {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify(data),
    });
    const out = await res.json().catch(() => ({}));
    if (res.ok && out.ok) {
      this.reset();
      setWaitlistStatus("You're on the list. We'll only email you about Piblo.", true);
    } else {
      setWaitlistStatus(out.reason === "invalid-email" ? "That email address doesn't look right." : "Sorry, that didn't go through. Please try again in a minute.", false);
    }
  } catch {
    setWaitlistStatus("Sorry, that didn't go through. Please check your connection and try again.", false);
  }
  button.disabled = false;
});
if (waitlistStatus) {
  const result = new URLSearchParams(location.search).get("subscribed");
  if (result === "1") setWaitlistStatus("You're on the list. We'll only email you about Piblo.", true);
  if (result === "0") setWaitlistStatus("Sorry, that didn't go through. Please try again.", false);
}
