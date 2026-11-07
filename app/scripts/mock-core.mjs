// A small stand-in for Nod Core so the app can be developed and screenshotted without Python or hardware.
// Usage: node scripts/mock-core.mjs [--offline-device]   (prints the env the app needs)
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export function startMock({ port = 18787, token = 'mock-token-123', deviceOnline = true } = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'nod-mock-'));
  fs.writeFileSync(path.join(dir, '.env'), `MAZ_TOKEN=${token}\nMAZ_PORT=${port}\nMAZ_DEFAULT_ROUTE=local\nMAZ_GROQ_API_KEY=x\n`);
  const now = () => Math.floor(Date.now() / 1000);
  const db = {
    beam: [{ id: 'b1', text: 'https://example.com/read-later', direction: 'to_pocket', created: now() - 4000, kind: 'link' }],
    dumps: [
      { id: 'd1', summary: 'Call the printer about the invoice before Friday', status: 'new', project: 'admin', created: new Date().toISOString(), source: 'device' },
      { id: 'd2', summary: 'Idea: a weekly digest of everything saved from the Nod', status: 'claimed', claimed_by: 'agent', project: 'nod', created: new Date().toISOString(), source: 'flow' },
      { id: 'd3', summary: 'Book dentist', status: 'done', project: 'personal', created: new Date().toISOString(), source: 'device' },
    ],
    pending: [{ id: 'p1', tool: 'Bash', summary: 'git push origin core/desktop-app', project: 'nod-core', left: 84 }],
    needs: [
      { id: 'pr-1', tier: 'prs', title: 'UNPROVEN: Nod Core desktop app', project: 'nod', age: 7200, detail: '' },
      { id: 'act-1', tier: 'actions', title: 'Approve the launch copy', project: 'handoff', age: 90000, detail: '' },
    ],
    halted: false,
    focus: { state: 'idle', muted: false, remaining_s: 0 },
    session: 0,
  };
  const frame = () => {
    const w = 240, h = 135, b = Buffer.alloc(w * h * 2);
    const put = (x, y, r, g, bl) => { const v = ((r >> 3) << 11) | ((g >> 2) << 5) | (bl >> 3); const o = (y * w + x) * 2; b[o] = v & 255; b[o + 1] = v >> 8; };
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) put(x, y, 20, 18, 15);
    for (let y = 0; y < 20; y++) for (let x = 0; x < w; x++) put(x, y, 229, 83, 45);
    for (let i = 0; i < 5; i++) for (let y = 34 + i * 18; y < 44 + i * 18; y++) for (let x = 14; x < 14 + 80 + ((i * 53) % 110); x++) put(x, y, 200, 190, 175);
    return b;
  };
  const json = (res, code, body) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(body)); };
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://x');
    const p = url.pathname;
    let body = '';
    for await (const c of req) body += c;
    const data = body ? JSON.parse(body) : {};
    if (p === '/health' && req.headers.authorization !== `Bearer ${token}`) return json(res, 200, { ok: true, name: 'nod Core', version: '1.0.2' });
    if (req.headers.authorization !== `Bearer ${token}`) return json(res, 401, { detail: 'authentication_required' });
    if (p === '/health') return json(res, 200, { ok: true, name: 'nod Core', version: '1.0.2', llm: { local: true, local_model: 'qwen3.5:4b', local_model_installed: true, local_engine: 'ollama' }, fw_latest: { version: '1.0.2' } });
    if (p === '/core/device') return json(res, 200, deviceOnline
      ? { device: { ok: true, version: '1.0.2', fw_build: 'a1b2c3d4e5f6', battery: 82, app: 'HOME' }, online: true, hub_fw: { version: '1.0.3', sha: 'ffeeddccbbaa', size: 1200000 }, update_available: true, last_report: { stage: 'ok' } }
      : { device: { ok: false, error: 'cardputer_unreachable' }, online: false, hub_fw: null, update_available: false });
    if (p === '/core/cardputer/screen') { if (!deviceOnline) return json(res, 503, { detail: 'cardputer_unreachable' }); res.writeHead(200, { 'content-type': 'application/octet-stream' }); return res.end(frame()); }
    if (p === '/core/cardputer/action') return json(res, 200, { ok: true, status: 200, text: 'ok' });
    if (p === '/core/update/check') return json(res, 200, { ok: true });
    if (p === '/beam/history') return json(res, 200, { ok: true, messages: [...db.beam].reverse() });
    if (p === '/beam/to-pocket') { const m = { id: 'b' + (db.beam.length + 1), text: data.text, direction: 'to_pocket', created: now(), kind: 'text' }; db.beam.push(m); return json(res, 200, { ok: true, queued: true, message: m }); }
    if (p === '/needs' && req.method === 'GET') return json(res, 200, { count: db.needs.length, items: db.needs });
    if (p.startsWith('/needs/')) { db.needs = db.needs.filter((n) => n.id !== p.split('/')[2]); return json(res, 200, { ok: true }); }
    if (p === '/buddy/pending') return json(res, 200, { ok: true, pending: db.pending });
    if (p === '/buddy/decide') { db.pending = []; return json(res, 200, { ok: true }); }
    if (p === '/buddy/today') return json(res, 200, { ok: true, done: 7, needs: 2, errors: 0, approved: 3, denied: 1, agents: [{ source: 'claude', done: 5 }], last: { text: 'Finished the desktop app build' } });
    if (p === '/buddy/halt') { if (req.method === 'POST') db.halted = !!data.on; return json(res, 200, { ok: true, halted: db.halted, until: db.halted ? new Date(Date.now() + 900000).toISOString() : null }); }
    if (p === '/work/today') return json(res, 200, { items: [{ item_id: 'w1', action: 'Send the follow-up to the first client', reason: 'Stored follow-up or deadline is due now.' }] });
    if (p === '/focus/state') return json(res, 200, db.focus);
    if (p === '/focus/start') { db.focus = { state: 'running', task: data.task, remaining_s: data.minutes * 60, muted: true }; return json(res, 200, db.focus); }
    if (p === '/focus/end') { db.focus = { state: 'idle', muted: false, remaining_s: 0 }; return json(res, 200, db.focus); }
    if (p === '/pc/action') return json(res, 200, { ok: true, reply: 'Done' });
    if (p === '/dumps' && req.method === 'GET') return json(res, 200, { dumps: url.searchParams.get('status') ? db.dumps.filter((d) => d.status === url.searchParams.get('status')) : db.dumps });
    if (p === '/dumps') { db.dumps.unshift({ id: 'd' + (db.dumps.length + 1), summary: data.text, status: 'new', project: null, created: new Date().toISOString(), source: 'web' }); return json(res, 200, { dump_id: 'x' }); }
    if (p.endsWith('/done')) { const d = db.dumps.find((x) => x.id === p.split('/')[2]); if (d) d.status = 'done'; return json(res, 200, { ok: true }); }
    if (p === '/library/search') return json(res, 200, { results: [{ id: 'l1', kind: 'web', url: 'https://example.com/a', author: 'example', snippet: 'A [saved] article about calm software', project: null }] });
    if (p === '/models') return json(res, 200, { local: true, local_engine: 'ollama', local_model: 'qwen3.5:4b', local_model_installed: true, backup_model: 'lfm2.5-8b', default_route: 'local', last_route: { provider: 'ollama' } });
    if (p === '/voices') return json(res, 200, { ok: true, current: 'v1', current_name: 'Adrian', voices: [{ name: 'Adrian', reference_id: 'v1', description: 'Warm, steady', current: true }, { name: 'Maya', reference_id: 'v2', description: 'Bright and quick' }, { name: 'Theo', reference_id: 'v3', description: 'Low and calm' }] });
    if (p === '/session/start') return json(res, 200, { session_id: 's' + ++db.session });
    if (p === '/turn/text') return json(res, 200, { reply: 'Start with the follow-up to your first client, then clear the two items waiting on you.', provider: 'ollama' });
    if (p === '/pair/start') return json(res, 200, { code: 'K7Q2-M9XD', expires_in_seconds: 300 });
    if (p === '/diagnostics') return json(res, 200, { ok: true, cardputer: { connected: deviceOnline } });
    json(res, 404, { detail: 'not_found' });
  });
  return new Promise((resolve) => server.listen(port, '127.0.0.1', () => resolve({ dir, port, token, close: () => server.close() })));
}

if (process.argv[1] && process.argv[1].endsWith('mock-core.mjs')) {
  const m = await startMock({ deviceOnline: !process.argv.includes('--offline-device') });
  console.log(`mock Core on ${m.port}; run the app with:\nNOD_CORE_DIR=${m.dir} NOD_CORE_PORT=${m.port}`);
}
