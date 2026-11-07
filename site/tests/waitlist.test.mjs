import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import test from 'node:test';

process.env.RESEND_API_KEY = 're_test_key';
process.env.RESEND_SEGMENT_ID = 'seg_piblo';
process.env.SIGNUP_NOTIFY_EMAIL = 'owner@example.com';
const { default: handler } = await import('../api/waitlist.js');

function fakeReq(body, { json = true, method = 'POST' } = {}) {
  const req = new EventEmitter();
  req.method = method;
  req.headers = json
    ? { 'content-type': 'application/json', accept: 'application/json' }
    : { 'content-type': 'application/x-www-form-urlencoded', accept: 'text/html' };
  req.destroy = () => {};
  setImmediate(() => {
    if (body !== undefined) req.emit('data', Buffer.from(json ? JSON.stringify(body) : new URLSearchParams(body).toString()));
    req.emit('end');
  });
  return req;
}

function fakeRes() {
  return {
    statusCode: 200, headers: {}, body: '',
    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
    end(chunk) { if (chunk) this.body += chunk; return this; },
  };
}

function recordingFetch(status = 200, text = '') {
  const calls = [];
  const impl = async (url, init) => {
    calls.push({ url, headers: init.headers, body: JSON.parse(init.body) });
    return { ok: status < 300, status, text: async () => text };
  };
  return { calls, impl };
}

test('a consenting valid email goes into the Piblo segment only', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: ' Ali@Example.co.uk ', first_name: ' Ali ', consent: true }), res, f.impl);
  assert.equal(res.statusCode, 200);
  assert.equal(f.calls.length, 2, 'contact, then the owner alert');
  assert.equal(f.calls[0].url, 'https://api.resend.com/contacts');
  assert.deepEqual(f.calls[0].body, { email: 'ali@example.co.uk', first_name: 'Ali', unsubscribed: false, segments: [{ id: 'seg_piblo' }] });
});

test('owner alert goes from the Piblo sender to the configured inbox', async () => {
  const f = recordingFetch();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), fakeRes(), f.impl);
  const mail = f.calls[1];
  assert.equal(mail.url, 'https://api.resend.com/emails');
  assert.equal(mail.body.from, 'Piblo <signups@mazworks.uk>');
  assert.deepEqual(mail.body.to, ['owner@example.com']);
});

test('a failed alert never breaks the signup', async () => {
  const impl = async (url) => (url.endsWith('/emails') ? { ok: false, status: 403, text: async () => '' } : { ok: true, status: 200, text: async () => '' });
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), res, impl);
  assert.equal(res.statusCode, 200);
});

test('no alert address configured means no alert, signup still works', async () => {
  const saved = process.env.SIGNUP_NOTIFY_EMAIL;
  delete process.env.SIGNUP_NOTIFY_EMAIL;
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), res, f.impl);
  process.env.SIGNUP_NOTIFY_EMAIL = saved;
  assert.equal(res.statusCode, 200);
  assert.equal(f.calls.length, 1);
});

test('no consent, no contact', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk' }), res, f.impl);
  assert.equal(res.statusCode, 400);
  assert.equal(JSON.parse(res.body).reason, 'no-consent');
  assert.equal(f.calls.length, 0);
});

test('a bad email is refused before anything reaches Resend', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'not-an-email', consent: true }), res, f.impl);
  assert.equal(res.statusCode, 400);
  assert.equal(f.calls.length, 0);
});

test('old honeypot name (cached pages) is still treated as a bot', async () => {
  const f = recordingFetch(); const res = fakeRes();
  await handler(fakeReq({ email: 'bot@example.com', consent: true, nod_hp_field: 'spam' }), res, f.impl);
  assert.equal(f.calls.length, 0);
  assert.equal(res.statusCode, 200);
});

test('honeypot looks successful but sends nothing', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'bot@example.com', consent: true, piblo_hp_field: 'spam' }), res, f.impl);
  assert.equal(res.statusCode, 200);
  assert.equal(f.calls.length, 0);
});

test('duplicate signup counts as success', async () => {
  const f = recordingFetch(409, 'Contact already exists');
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), res, f.impl);
  assert.equal(res.statusCode, 200);
});

test('Resend failure is reported, not hidden', async () => {
  const f = recordingFetch(500, 'boom');
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), res, f.impl);
  assert.equal(res.statusCode, 502);
});

test('missing segment refuses rather than dumping into the shared list', async () => {
  const saved = process.env.RESEND_SEGMENT_ID;
  delete process.env.RESEND_SEGMENT_ID;
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true }), res, f.impl);
  process.env.RESEND_SEGMENT_ID = saved;
  assert.equal(res.statusCode, 502);
  assert.equal(f.calls.length, 0);
});

test('no-JS form post redirects back to the form', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: 'yes' }, { json: false }), res, f.impl);
  assert.equal(res.statusCode, 303);
  assert.equal(res.headers.location, '/?subscribed=1#waitlist');
});

test('oversized body is rejected', async () => {
  const f = recordingFetch();
  const res = fakeRes();
  await handler(fakeReq({ email: 'ali@example.co.uk', consent: true, first_name: 'x'.repeat(5000) }), res, f.impl);
  assert.equal(res.statusCode, 413);
  assert.equal(f.calls.length, 0);
});

test('GET is not allowed', async () => {
  const res = fakeRes();
  await handler(fakeReq(undefined, { method: 'GET' }), res, recordingFetch().impl);
  assert.equal(res.statusCode, 405);
});
