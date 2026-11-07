// Nod Home, talk-circle version: pure logic (no hardware) so it is unit tested
// on a PC. The firmware draws; this decides WHAT to draw and WHERE.
#pragma once
#include <stdint.h>
#include "home_layout.h"  // Rect

namespace nod {

// ---- talk state machine ------------------------------------------------
enum TalkState : uint8_t { TALK_IDLE, TALK_LISTENING, TALK_THINKING, TALK_SPEAKING };
enum TalkEvent : uint8_t {
    EV_MIC_OPEN,    // mic starts (also barge-in while speaking)
    EV_MIC_CLOSE,   // mic stops, audio goes to Core
    EV_REPLY_PLAY,  // first reply audio starts
    EV_REPLY_DONE,  // reply finished (or text-only reply arrived)
    EV_CANCEL,      // ESC
    EV_FAIL         // link or job error
};

inline TalkState talkStep(TalkState s, TalkEvent e) {
    if (e == EV_CANCEL || e == EV_FAIL) return TALK_IDLE;  // ESC works at every stage
    switch (s) {
        case TALK_IDLE:
        case TALK_SPEAKING: return e == EV_MIC_OPEN ? TALK_LISTENING : (e == EV_REPLY_DONE ? TALK_IDLE : s);
        case TALK_LISTENING: return e == EV_MIC_CLOSE ? TALK_THINKING : s;
        case TALK_THINKING: return e == EV_REPLY_PLAY ? TALK_SPEAKING : (e == EV_REPLY_DONE ? TALK_IDLE : s);
    }
    return TALK_IDLE;
}

// What the circle shows right now, from what the firmware can observe.
// Mic beats playback beats a pending job.
inline TalkState talkFromSources(bool micLive, bool playing, bool jobBusy) {
    return micLive ? TALK_LISTENING : playing ? TALK_SPEAKING : jobBusy ? TALK_THINKING : TALK_IDLE;
}

// ---- animation (all integer, cheap) ------------------------------------
inline int triangle(uint32_t ms, uint32_t period, int amp) {  // 0..amp..0
    const uint32_t p = ms % period, half = period / 2;
    return (int)((p < half ? p : period - p) * (uint32_t)amp / half);
}
// Idle: a ring 3..5 px outside the circle, breathing over 3.2 s.
inline int idleRingRadius(int r, uint32_t ms) { return r + 3 + triangle(ms, 3200, 2); }
// Listening/speaking: ring follows level (0..1000 = 0..1.0), 3..8 px outside.
inline int levelRingRadius(int r, int level1000) {
    if (level1000 < 0) level1000 = 0;
    if (level1000 > 1000) level1000 = 1000;
    return r + 3 + level1000 * 5 / 1000;
}
// Thinking: start angle (deg) of a 90-degree arc, one turn per 1.2 s.
inline int arcStartDeg(uint32_t ms) { return (int)((ms % 1200) * 360 / 1200); }

// ---- layout ------------------------------------------------------------
// Circle on the left, three buttons (Save, Today, More) on the right, one
// sentence line under them (link trouble or "1-4 quick").
enum TalkFocus : uint8_t { FOCUS_TALK, FOCUS_SAVE, FOCUS_TODAY, FOCUS_MORE, FOCUS_COUNT };
static const char* const kTalkButton[3] = {"Save", "Today", "More"};

struct TalkHomeLayout {
    int16_t cx, cy, r;  // circle; ring never exceeds r + RING_MAX
    Rect btn[3];
    Rect sentence;
};
constexpr int RING_MAX = 8;

inline TalkHomeLayout computeTalkHome(Rect body) {
    TalkHomeLayout L;
    L.r = (int16_t)(body.h / 2 - RING_MAX - 1);  // 106 px body -> 44 (88 px circle)
    L.cx = (int16_t)(body.x + 4 + L.r + RING_MAX);
    L.cy = (int16_t)(body.y + body.h / 2);
    const int16_t colX = (int16_t)(L.cx + L.r + RING_MAX + 4);
    const int16_t colW = (int16_t)(body.x + body.w - 6 - colX);
    const int16_t gap = 4, line = 10;
    const int16_t bh = (int16_t)((body.h - 6 - line - 3 * gap) / 3);
    for (int i = 0; i < 3; i++) L.btn[i] = {colX, (int16_t)(body.y + 4 + i * (bh + gap)), colW, bh};
    L.sentence = {colX, (int16_t)(L.btn[2].y + bh + gap), colW, line};
    return L;
}

// Focus: 0 = circle, 1..3 = Save/Today/More. LEFT/RIGHT cross, UP/DOWN walk the column.
inline TalkFocus moveTalkFocus(TalkFocus f, char dir /* 'L','R','U','D' */) {
    if (dir == 'L') return FOCUS_TALK;
    if (dir == 'R') return f == FOCUS_TALK ? FOCUS_SAVE : f;
    if (f == FOCUS_TALK) return f;
    if (dir == 'U') return f > FOCUS_SAVE ? (TalkFocus)(f - 1) : f;
    if (dir == 'D') return f < FOCUS_MORE ? (TalkFocus)(f + 1) : f;
    return f;
}

}  // namespace nod
