import { Icon } from './ui';
import { formatCode, pairingCardText, type PairDecision, type PairRequest } from '../lib/pairing';

/**
 * "Piblo wants to connect. Check Piblo shows 482 913." with [Allow] [Not mine].
 * The person compares the two screens; nothing here approves anything on its own.
 */
export function PairingCard({
  request,
  busy,
  notice,
  onDecide,
}: {
  request: PairRequest;
  busy?: boolean;
  notice?: string | null;
  onDecide(decision: PairDecision): void;
}) {
  const { title, body } = pairingCardText(request);
  const id = `pair-${request.request_id}`;
  return (
    <section className="card pair-card" aria-labelledby={id} data-request={request.request_id}>
      <div className="row pair-head">
        <span className="pair-mark" aria-hidden="true">
          <Icon name="plug" size={20} />
        </span>
        <div className="grow">
          <h2 id={id}>{title}</h2>
          <p className="sub">
            {body} <strong className="pair-code">{formatCode(request.code)}</strong>.
          </p>
        </div>
      </div>
      {notice && <p className="pair-notice" role="status">{notice}</p>}
      <div className="row wrap">
        <button className="btn primary" disabled={busy} onClick={() => onDecide('allow')}>
          <Icon name="check" size={16} /> Allow
        </button>
        <button className="btn" disabled={busy} onClick={() => onDecide('deny')}>
          Not mine
        </button>
      </div>
    </section>
  );
}

/** One card per pending request, oldest first. */
export function PairingList({
  requests,
  busy,
  notice,
  onDecide,
}: {
  requests: PairRequest[];
  busy?: string | null;
  notice?: string | null;
  onDecide(requestId: string, decision: PairDecision): void;
}) {
  return (
    <div className="stack">
      {requests.map((r) => (
        <PairingCard key={r.request_id} request={r} busy={busy === r.request_id} notice={notice} onDecide={(d) => onDecide(r.request_id, d)} />
      ))}
    </div>
  );
}
