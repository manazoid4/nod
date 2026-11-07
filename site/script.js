// Closes the mobile menu after a link is chosen, so in-page jumps are not hidden behind it.
document.querySelectorAll(".mobile-menu a").forEach(link =>
  link.addEventListener("click", () => link.closest("details").removeAttribute("open")));

// Hero film: plays muted only while on screen, and never for people who ask for reduced motion
// (they get the poster plus controls instead).
const still = window.matchMedia("(prefers-reduced-motion: reduce)");
document.querySelectorAll("video[data-autoplay]").forEach(video => {
  if (still.matches || !("IntersectionObserver" in window)) { video.controls = true; return; }
  new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) video.play().catch(() => { video.controls = true; });
    else video.pause();
  }, { threshold: 0.4 }).observe(video);
});
