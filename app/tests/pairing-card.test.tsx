import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { PairingList, PairingCard } from '../src/components/PairingCard';
import { EXPIRED_TEXT, type PairRequest } from '../src/lib/pairing';

const req = (over: Partial<PairRequest> = {}): PairRequest => ({
  request_id: 'req-482913',
  code: '482913',
  name: 'Piblo',
  device_id: 'piblo-a1b2',
  ip: '192.168.1.42',
  age_s: 6,
  ...over,
});

describe('pairing card', () => {
  it('shows the code to compare and both choices', () => {
    const html = renderToStaticMarkup(<PairingCard request={req()} onDecide={() => {}} />);
    expect(html).toContain('Piblo wants to connect.');
    expect(html).toContain('Check Piblo shows');
    expect(html).toContain('482 913');
    expect(html).toContain('Allow');
    expect(html).toContain('Not mine');
  });

  it('never claims a connection before the person decides', () => {
    const html = renderToStaticMarkup(<PairingCard request={req()} onDecide={() => {}} />);
    expect(html).not.toContain('Connected');
    expect(html).not.toContain('disabled');
  });

  it('disables both buttons while an answer is on its way', () => {
    const html = renderToStaticMarkup(<PairingCard request={req()} busy onDecide={() => {}} />);
    expect(html.match(/disabled/g)).toHaveLength(2);
  });

  it('shows what happened when the request expired', () => {
    const html = renderToStaticMarkup(<PairingCard request={req()} notice={EXPIRED_TEXT} onDecide={() => {}} />);
    expect(html).toContain(EXPIRED_TEXT);
  });

  it('renders one card per waiting device, oldest first', () => {
    const html = renderToStaticMarkup(
      <PairingList requests={[req({ request_id: 'a', name: 'Piblo', age_s: 60 }), req({ request_id: 'b', code: '111222', age_s: 3 })]} onDecide={() => {}} />,
    );
    expect(html.match(/wants to connect/g)).toHaveLength(2);
    expect(html.indexOf('482 913')).toBeLessThan(html.indexOf('111 222'));
  });
});
