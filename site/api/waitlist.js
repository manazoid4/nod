// Waitlist signup for the Nod site. Ported from the Maz Meats subscribe function:
// contacts go into the Nod Resend segment (RESEND_SEGMENT_ID), the owner alert is
// sent from the verified mazworks.uk domain. Server-side so the API key never
// reaches a browser, and the form works without JavaScript (303 redirect).
const CONTACTS_URL = 'https://api.resend.com/contacts';
const EMAILS_URL = 'https://api.resend.com/emails';
// Resend stores contacts silently, so each signup is also emailed to the owner.
// The destination lives only in Vercel (SIGNUP_NOTIFY_EMAIL); unset means no alert.
const NOTIFY_FROM = 'Nod <signups@mazworks.uk>';
const MAX_BODY_BYTES = 2048;
const TIMEOUT_MS = 10000;

// Deliberately loose: the goal is to reject typos and junk, not to be an RFC.
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,255}\.[^\s@]{2,}$/;

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error('body too large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function parseBody(raw, type = '') {
  if (type.includes('application/json')) {
    try { return JSON.parse(raw) ?? {}; } catch { return {}; }
  }
  return Object.fromEntries(new URLSearchParams(raw));
}

function reply(req, res, status, result) {
  res.setHeader('cache-control', 'no-store, max-age=0');
  res.setHeader('x-content-type-options', 'nosniff');
  if ((req.headers.accept || '').includes('application/json')) {
    res.statusCode = status;
    res.setHeader('content-type', 'application/json; charset=utf-8');
    return res.end(JSON.stringify(result));
  }
  // No JavaScript: send the visitor back to the form with the outcome in the URL.
  res.statusCode = 303;
  res.setHeader('location', `/?subscribed=${result.ok ? '1' : '0'}#waitlist`);
  return res.end();
}

export async function addContact(email, firstName, fetchImpl = fetch) {
  const apiKey = process.env.RESEND_API_KEY || '';
  const segmentId = process.env.RESEND_SEGMENT_ID || '';
  // Without a segment the contact would land in the shared account list, so refuse.
  if (!apiKey || !segmentId) return { ok: false, reason: 'unconfigured' };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetchImpl(CONTACTS_URL, {
      method: 'POST',
      headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
      body: JSON.stringify({ email, ...(firstName && { first_name: firstName }), unsubscribed: false, segments: [{ id: segmentId }] }),
      signal: controller.signal,
    });
    if (response.ok) return { ok: true };
    // Signing up twice is not an error from the visitor's side: they are on the list.
    const detail = await response.text().catch(() => '');
    if (response.status === 409 || /already exists/i.test(detail)) return { ok: true };
    return { ok: false, reason: 'rejected' };
  } catch {
    return { ok: false, reason: controller.signal.aborted ? 'timeout' : 'network' };
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Best effort: a failed alert must never turn a real signup into an error for
 * the visitor, because the contact is already saved in Resend.
 */
export async function notifyOwner(email, firstName, fetchImpl = fetch) {
  const apiKey = process.env.RESEND_API_KEY || '';
  const to = process.env.SIGNUP_NOTIFY_EMAIL || '';
  if (!apiKey || !to) return false;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetchImpl(EMAILS_URL, {
      method: 'POST',
      headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: NOTIFY_FROM,
        to: [to],
        reply_to: email,
        subject: `New Nod waitlist signup: ${email}`,
        text: `${firstName ? `${firstName} <${email}>` : email} just joined the Nod waitlist.\n\nThey are saved in Resend under the Nod segment.`,
      }),
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

export default async function handler(req, res, fetchImpl = fetch) {
  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('allow', 'POST');
    return res.end();
  }

  let body;
  try {
    body = parseBody(await readBody(req), req.headers['content-type']);
  } catch {
    return reply(req, res, 413, { ok: false, reason: 'too-large' });
  }

  // Honeypot: real visitors never see this field, so anything in it is a bot.
  // Unusual field name so browser autofill never fills it and drops a real signup.
  if (typeof body.nod_hp_field === 'string' && body.nod_hp_field.trim() !== '') {
    return reply(req, res, 200, { ok: true });
  }

  const firstName = typeof body.first_name === 'string' ? body.first_name.trim().slice(0, 80) : '';
  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
  if (!EMAIL.test(email)) return reply(req, res, 400, { ok: false, reason: 'invalid-email' });
  // Consent is the lawful basis for the list (see /privacy), so it must be ticked.
  if (body.consent !== 'yes' && body.consent !== true) return reply(req, res, 400, { ok: false, reason: 'no-consent' });

  const result = await addContact(email, firstName, fetchImpl);
  // Awaited, not fired-and-forgotten: the function can be frozen once it replies.
  if (result.ok) await notifyOwner(email, firstName, fetchImpl);
  return reply(req, res, result.ok ? 200 : 502, result);
}
