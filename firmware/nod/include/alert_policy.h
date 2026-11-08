// Piblo - alert policy: ONE table mapping alert priority -> sound, LED/flash, Buddy mood.
//
// Pure (no hardware, no globals) so firmware/nod/tests can check it on a PC.
// Sounds are original tone sequences played with M5.Speaker.tone().
#pragma once
#include <stdint.h>
#include <string.h>

namespace maz {
namespace alert_policy {

enum class Priority : uint8_t { Low, Normal, High, Urgent };
enum class Mood : uint8_t { Idle, Working, Celebrating, Sleeping, NeedsAttention };

struct Tone { uint16_t hz; uint16_t ms; };

constexpr uint8_t MAX_TONES = 4;
constexpr uint8_t FLASH_UNTIL_ACK = 255;

struct Rule {
    Tone    tones[MAX_TONES];
    uint8_t toneCount;
    uint8_t flashes;       // screen-edge "LED" pulses; FLASH_UNTIL_ACK = keeps pulsing until answered
    Mood    mood;
};

// priority -> pattern. The single source of truth for how an alert feels.
constexpr Rule RULES[4] = {
    /* Low    */ {{{660, 40}, {0, 0}, {0, 0}, {0, 0}},          1, 0, Mood::Idle},
    /* Normal */ {{{880, 60}, {1175, 60}, {0, 0}, {0, 0}},      2, 2, Mood::NeedsAttention},
    /* High   */ {{{880, 70}, {1175, 70}, {1480, 90}, {0, 0}},  3, 4, Mood::NeedsAttention},
    /* Urgent */ {{{1480, 90}, {988, 90}, {1480, 90}, {988, 90}}, 4, FLASH_UNTIL_ACK, Mood::NeedsAttention},
};

inline Priority parsePriority(const char* s) {
    if (!s) return Priority::Normal;
    if (!strcmp(s, "low")) return Priority::Low;
    if (!strcmp(s, "high")) return Priority::High;
    if (!strcmp(s, "urgent")) return Priority::Urgent;
    return Priority::Normal;
}

inline const Rule& rule(Priority p) { return RULES[static_cast<uint8_t>(p)]; }

// A finished task is good news, whatever its priority.
inline Mood moodFor(Priority p, bool taskDone) { return taskDone ? Mood::Celebrating : rule(p).mood; }

// quietLevel: 0 Normal, 1 Quiet, 2 Silent (quiet::Level). Quiet drops low/normal,
// Silent drops everything except urgent. Approvals are not alerts: they keep their
// own forced chirp (sfx::approval) and never go through this function.
inline bool shouldSound(uint8_t quietLevel, Priority p) {
    if (quietLevel == 0) return true;
    if (quietLevel == 1) return p == Priority::High || p == Priority::Urgent;
    return p == Priority::Urgent;
}

// Urgent alarms are forced through a muted UI-sound setting, like the Focus alarm.
inline bool forced(Priority p) { return p == Priority::Urgent; }

// Action bitmask used on the device: which keys the overlay offers.
constexpr uint8_t ACT_ACK = 1, ACT_SNOOZE = 2;

}  // namespace alert_policy
}  // namespace maz
