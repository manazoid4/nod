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
