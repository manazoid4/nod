"""Regression tests for the firmware DSP, ported 1:1 from the C++ integer math.

Mirrors (keep in sync, the firmware has no host harness):
- src/audio/limiter.h  -> _soft_limit
- src/audio/live.cpp   -> _fade_in / _fade_out / _ramp (kFade = 80)

Division is C-style truncation toward zero, not Python floor: use _c_div.
The C++ soft limiter computes in 32-bit float; Python doubles differ by at
most 1 LSB near the knee, so value assertions carry a +/-1 tolerance while
the hard ceiling stays exact.
"""

from __future__ import annotations

import math

K_KNEE = 0.6 * 32768.0
K_ROOM = 0.3 * 32768.0
K_FADE = 80
CEILING = int(0.9 * 32768.0)  # the limiter must never emit past this


def _c_div(a: int, b: int) -> int:
    """C integer division: truncates toward zero (Python // floors)."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _trunc(x: float) -> int:
    return math.trunc(x)


def _soft_limit(samples: list[int]) -> list[int]:
    out = []
    for s in samples:
        a = -float(s) if s < 0 else float(s)
        if a <= K_KNEE:
            out.append(s)
            continue
        t = (a - K_KNEE) / K_ROOM
        y = K_KNEE + K_ROOM * (t / (1.0 + t))
        out.append(_trunc(-y if s < 0 else y))
    return out


def _fade_in(block: list[int]) -> list[int]:
    out = list(block)
    for i in range(min(K_FADE, len(out))):
        out[i] = _c_div(out[i] * i, K_FADE)
    return out


def _fade_out(block: list[int]) -> list[int]:
    n = len(block)
    f = min(n, K_FADE)
    out = list(block)
    for i in range(f):
        out[n - f + i] = _c_div(out[n - f + i] * (f - 1 - i), f)
    return out


def _ramp(last: int) -> list[int]:
    return [_c_div(last * (K_FADE - 1 - i), K_FADE) for i in range(K_FADE)]


def test_silence_stays_silent():
    assert _soft_limit([0] * 256) == [0] * 256
    assert _fade_in([0] * K_FADE) == [0] * K_FADE
    assert _fade_out([0] * K_FADE) == [0] * K_FADE
    assert _ramp(0) == [0] * K_FADE


def test_no_sample_exceeds_ceiling():
    # worst case: alternating full-scale square wave
    square = [32767 if i % 2 == 0 else -32768 for i in range(4096)]
    out = _soft_limit(square)
    assert max(abs(v) for v in out) <= CEILING


def test_below_knee_passes_through_unchanged():
    quiet = [((i * 37) % 9000) - 4500 for i in range(2048)]  # |v| <= 4500 < knee
    assert _soft_limit(quiet) == quiet


def test_limiter_is_monotonic_and_stable():
    amps = list(range(19661, 32769)) + list(range(-32768, -19660))
    out = _soft_limit(amps)
    pos = [v for a, v in zip(amps, out) if a > 0]
    neg = [v for a, v in zip(amps, out) if a < 0]
    assert pos == sorted(pos), "positive gain curve must not fold back"
    assert neg == sorted(neg), "negative gain curve must not fold back"
    for a, v in zip(amps, out):
        assert abs(v) <= abs(a), "limiter must never add gain"


def test_full_scale_tone_passes_at_expected_level():
    # 1 kHz at 16 kHz rate, full-scale sine
    tone = [int(32767.0 * math.sin(2 * math.pi * 1000.0 * i / 16000.0)) for i in range(16000)]
    out = _soft_limit(tone)
    peak = max(out)
    # peak input maps through the knee: t=(32767-19660.8)/9830.4 -> y ~ 25278
    assert 25277 <= peak <= 25279, f"unexpected full-scale peak {peak}"
    assert peak <= CEILING
    # the fundamental survives: exact DFT bin for 1 kHz at 16 kHz (16 samples/cycle)
    re = sum(v * math.cos(-2 * math.pi * i * 1000 / 16000) for i, v in enumerate(out))
    im = sum(v * math.sin(-2 * math.pi * i * 1000 / 16000) for i, v in enumerate(out))
    fund = 2.0 * math.hypot(re, im) / len(out)
    fund_in = 2.0 * math.hypot(
        sum(v * math.cos(-2 * math.pi * i * 1000 / 16000) for i, v in enumerate(tone)),
        sum(v * math.sin(-2 * math.pi * i * 1000 / 16000) for i, v in enumerate(tone)),
    ) / len(tone)
    assert fund >= 0.75 * fund_in, f"fundamental collapsed: {fund:.0f} vs {fund_in:.0f}"


def test_fades_are_monotonic_and_end_at_zero():
    body = [20000] * 256
    fin = _fade_in(body)
    assert fin[0] == 0
    assert all(b >= a for a, b in zip(fin, fin[1:])), "fade-in must rise monotonically"
    assert fin[K_FADE - 1] == _c_div(20000 * (K_FADE - 1), K_FADE)  # last faded sample
    assert fin[K_FADE] == 20000  # first sample past the fade window is untouched

    fout = _fade_out(body)
    assert fout[-1] == 0
    assert all(b <= a for a, b in zip(fout, fout[1:])), "fade-out must fall monotonically"

    r = _ramp(-29491)
    assert r[-1] == 0
    mags = [abs(v) for v in r]
    assert all(b <= a for a, b in zip(mags, mags[1:])), "ramp must decay monotonically"
    assert r[0] == _c_div(-29491 * (K_FADE - 1), K_FADE)


def test_fades_match_c_sign_semantics_for_negative_audio():
    # C truncation toward zero: -10000*40/80 must be -5000, not floor -5000/-5001 cases
    assert _c_div(-10000 * 40, K_FADE) == -5000
    assert _c_div(-10001 * 40, K_FADE) == -5000  # -500050/80 -> -5000 (trunc), not -5001
    fin = _fade_in([-10000] * K_FADE)
    mags = [abs(v) for v in fin]
    assert all(b >= a for a, b in zip(mags, mags[1:])), "fade-in must grow toward the signal"
    assert fin[0] == 0
