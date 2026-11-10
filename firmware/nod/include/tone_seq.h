// Piblo - non-blocking tone sequencer.
//
// Alert/approval/alarm chirps used to play with delay() between notes, freezing the UI loop for
// up to ~0.5 s (docs/ALERTS.md). This keeps the queue and timing as pure logic (no hardware, no
// globals) so firmware/nod/tests can check it on a PC; src/audio/sfx.cpp feeds it to
// M5.Speaker.tone() from main loop().
#pragma once
#include <stdint.h>

namespace nod {

struct ToneStep {
    uint16_t hz;    // 0 = rest
    uint16_t ms;    // how long the note sounds
    uint16_t slot;  // how long the step occupies the timeline (>= ms; the rest is a gap)
    bool     force; // play even when UI sounds are muted
};

class ToneSeq {
public:
    static constexpr uint8_t CAP = 8;

    void clear() { _head = _n = 0; _busy = false; }

    // Appends a note; false (dropped) when full. slot 0 means "same as ms".
    bool push(uint16_t hz, uint16_t ms, bool force = false, uint16_t slot = 0) {
        if (_n >= CAP) return false;
        _q[(_head + _n++) % CAP] = ToneStep{hz, ms, static_cast<uint16_t>(slot < ms ? ms : slot), force};
        return true;
    }

    // Call every loop. Returns true once per step, with the note to start now in `out`.
    bool poll(uint32_t now, ToneStep& out) {
        if (_busy && static_cast<int32_t>(now - _until) < 0) return false;
        if (_n == 0) { _busy = false; return false; }
        out = _q[_head];
        _head = (_head + 1) % CAP;
        --_n;
        _busy = true;
        _until = now + out.slot;
        return true;
    }

    // True while a queued/sounding note still owns the speaker (UI clicks should stay quiet).
    bool playing(uint32_t now) const { return _n > 0 || (_busy && static_cast<int32_t>(now - _until) < 0); }

private:
    ToneStep _q[CAP] = {};
    uint8_t  _head = 0, _n = 0;
    bool     _busy = false;
    uint32_t _until = 0;
};

}  // namespace nod
