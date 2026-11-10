#include "sfx.h"

#include <M5Unified.h>
#include <tone_seq.h>

#include "../core/settings.h"
#include "../core/quiet.h"
#include "live.h"
#include "voice.h"

namespace maz {
namespace sfx {

namespace {
// Multi-note chirps (alerts, approvals, alarms) are queued and stepped from loop() by update(), so
// the UI never sleeps in delay() while they play, and they still sound in the order raised. Only
// recStart/recStop stay synchronous: their order against the microphone starting is the point.
nod::ToneSeq gSeq;

// `force` exists so an alarm the user asked for (Focus complete) still fires
// with UI sounds muted — muting chirps is not the same as muting alarms.
bool audible(bool force) {
    return (Cfg.uiSounds && quiet::level() != quiet::Level::Silent) || force;
}
void play(float hz, uint32_t ms, bool force = false) {
    if (!audible(force)) return;
    // tone() auto-starts the speaker; while the mic owns the shared codec that
    // would fight the capture. Silence beats corrupting a recording.
    const auto st = voice::state();
    if (st == voice::State::Listening || st == voice::State::Paused) return;
    if (live::micActive()) return;  // a tone would restart the codec and kill the live mic
    M5.Speaker.tone(hz, ms);
}
// Single-note UI clicks stay quiet while a queued chirp is sounding, so a keypress cannot cut it.
void click(float hz, uint32_t ms) {
    if (!gSeq.playing(millis())) play(hz, ms);
}
void note(float hz, uint16_t ms, bool force = false, uint16_t slot = 0) {
    if (audible(force)) gSeq.push(static_cast<uint16_t>(hz), ms, force, slot);
}
void pair(float a, float b, uint16_t ms, bool force = false) {
    note(a, ms, force);
    note(b, ms, force);
}
void pairNow(float a, float b, uint32_t ms) {  // synchronous: see gSeq comment
    gSeq.clear();  // queued chirps would only be dropped once the mic is live
    play(a, ms);
    delay(ms);
    play(b, ms);
}
}  // namespace

void update() {
    nod::ToneStep s;
    if (gSeq.poll(millis(), s) && s.hz) play(s.hz, s.ms, s.force);
}

void boot()      { pair(660.f, 990.f, 70); }
void select()    { click(1200.f, 8); }
void confirm()   { click(1600.f, 18); }
void recStart()  { pairNow(880.f, 1320.f, 40); }
void recStop()   { pairNow(1320.f, 880.f, 40); }
// Not decoration: these let you know a remote session actually opened or was
// cleared without staring at the screen while walking around with the device.
void lineOpen()  { pair(440.f, 660.f, 55); }
void lineClose() { pair(660.f, 330.f, 55); }
void saved()     { click(1760.f, 45); }
void error()     { pair(300.f, 200.f, 90); }

void approval()  { pair(880.f, 1480.f, 90, /*force=*/true); }

void alertPattern(const alert_policy::Rule& r, bool force) {
    for (uint8_t i = 0; i < r.toneCount && i < alert_policy::MAX_TONES; ++i)
        note(r.tones[i].hz, r.tones[i].ms, force);
}

// Called right before notify::post(Success): the toast's generic "saved" beep
// is skipped once so only the agent chirp plays.
bool gSkipNextNote = false;
void agentDone() { gSkipNextNote = true; pair(880.f, 1175.f, 50); }
void skipNextNote() { gSkipNextNote = true; }

void timerDone() {
    for (int i = 0; i < 3; ++i) note(1200.f, 120, /*force=*/true, /*slot=*/160);
}

void forNote(Note kind) {
    if (gSkipNextNote) { gSkipNextNote = false; return; }
    switch (kind) {
        case Note::Success: saved(); break;
        case Note::Warn:    click(700.f, 60); break;
        case Note::Error:   error(); break;
        default:            click(1000.f, 20); break;
    }
}

}  // namespace sfx
}  // namespace maz
