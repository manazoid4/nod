(() => {
  // Illustration of the intended approval flow. Pure UI, no network, no device.
  const states = {
    ask: { top: 'AGENT ASKS', title: 'Run deploy script?', copy: 'Your agent wants to run ./deploy.sh', left: 'APPROVE', right: 'STOP' },
    approved: { top: 'APPROVED', title: 'You said yes.', copy: 'The agent continues. You pressed the key.', left: 'DONE', right: '' },
    stopped: { top: 'STOPPED', title: 'You said no.', copy: 'The agent is told no. Nothing runs.', left: 'DONE', right: '' },
    timeout: { top: 'NO ANSWER', title: 'Nothing approved.', copy: 'After 60 s the agent asks in your normal terminal instead.', left: 'FALLBACK', right: '' }
  };
  const screen = document.getElementById('device-screen');
  if (!screen) return;
  const put = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  document.querySelectorAll('[data-try]').forEach((b) => b.addEventListener('click', () => {
    const s = states[b.dataset.try];
    if (!s) return;
    screen.dataset.state = b.dataset.try;
    put('screen-top', s.top); put('screen-title', s.title); put('screen-copy', s.copy); put('screen-left', s.left); put('screen-right', s.right);
  }));
})();
