// Piblo - phone keyboard text: pure insert logic for POST /buddy/text.
//
// The Android companion sends longer messages from a phone keyboard (or its
// speech recogniser) over piblo-proto v1. The Core forwards them as
// /buddy/events ring entries of kind "text_input". This header is the single
// place that turns untrusted phone text into field text, and it is pure (no
// hardware, no globals) so firmware/nod/tests can pin the contract on a PC:
//
//   * Phone text is ALWAYS literal characters. It is never read as keys,
//     shortcuts or commands, and it can never approve anything.
//   * Non-printable bytes (newline, ESC, control codes) are dropped, never
//     turned into separators or key events.
//   * Text that does not fit the field is rejected whole (TooLong); nothing
//     is partially inserted, so the phone's ack is truthful.
//   * Mode "send" inserts only. It never synthesises ENTER, so it can never
//     submit a form or approve a prompt. The submit stays a human keypress.
//   * A queued message older than kTtlSeconds (2 minutes) is dropped and
//     never inserted late.
#pragma once
#include <stdint.h>
#include <string>
#include <string.h>

namespace maz {
namespace phone_text {

constexpr size_t kMaxTextChars = 500;   // Core validation: 1..500 chars
constexpr size_t kMaxIdChars   = 64;    // client uuid + slack
constexpr int64_t kTtlSeconds  = 120;   // 2 minutes, then drop
constexpr int kMaxSeenIds = 8;          // firmware-side dedupe ring

enum class Mode : uint8_t { Insert, Replace, Send };
enum class Status : uint8_t { Inserted, NoField, TooLong, Unsupported };

// The device font is ASCII only. Any byte >= 0x80 (UTF-8 accents, emoji,
// non-Latin scripts) rejects the whole message so the phone is told the
// truth instead of seeing "inserted" for text with letters silently missing.
inline bool hasNonAscii(const std::string& s) {
    for (char c : s)
        if (static_cast<uint8_t>(c) >= 0x80) return true;
    return false;
}

inline bool parseMode(const char* s, Mode& out) {
    if (!s) return false;
    if (!strcmp(s, "insert"))  { out = Mode::Insert;  return true; }
    if (!strcmp(s, "replace")) { out = Mode::Replace; return true; }
    if (!strcmp(s, "send"))    { out = Mode::Send;    return true; }
    return false;
}

// Printable 0x20..0x7E only. Everything else is dropped, never interpreted.
inline bool printable(char c) {
    const uint8_t u = static_cast<uint8_t>(c);
    return u >= 0x20 && u <= 0x7E;
}

// Sanitize `in` into `out`, dropping non-printables. `out.len` caps the
// result; excess is reported via `dropped` but never inserted anywhere.
inline void sanitize(const std::string& in, std::string& out, size_t& dropped) {
    out.clear();
    dropped = 0;
    for (size_t i = 0; i < in.size(); ++i) {
        if (printable(in[i])) out.push_back(in[i]);
        else ++dropped;
    }
}

// Apply one phone message to `dst` at `cursor` (clamped to dst size).
// Returns NoField when `focused` is false, Unsupported when it holds any
// non-ASCII byte, TooLong when the whole message does not fit, Inserted
// otherwise. On anything but Inserted `dst` is untouched.
// On Inserted, `cursor` moves to just after the inserted text.
inline Status applyPhoneText(std::string& dst, size_t limit, size_t& cursor,
                             Mode mode, const std::string& phone, bool focused) {
    if (!focused) return Status::NoField;
    if (hasNonAscii(phone)) return Status::Unsupported;
    std::string clean;
    size_t dropped = 0;
    sanitize(phone, clean, dropped);
    if (cursor > dst.size()) cursor = dst.size();
    if (mode == Mode::Replace) {
        if (clean.size() > limit) return Status::TooLong;
        dst = clean;
        cursor = dst.size();
        return Status::Inserted;
    }
    // Insert and Send are identical here: literal insert, never submit.
    if (dst.size() + clean.size() > limit) return Status::TooLong;
    dst.insert(cursor, clean);
    cursor += clean.size();
    return Status::Inserted;
}

// Freshness: a message older than the TTL must never be inserted late.
// When the device clock is not yet valid (`nowValid` false) only age can
// be judged from the Core stamp, so treat it as fresh rather than losing
// text the user just typed.
inline bool fresh(int64_t eventTs, int64_t now, bool nowValid) {
    if (!nowValid) return true;
    if (eventTs <= 0) return false;
    return (now - eventTs) <= kTtlSeconds;
}

// A valid dedupe id is non-empty and bounded. The Core validates uuids on
// intake; the firmware only needs a bounded key for its seen-set.
inline bool validId(const char* s) {
    if (!s || !s[0]) return false;
    size_t n = 0;
    while (s[n]) {
        if (!printable(s[n])) return false;
        ++n;
        if (n > kMaxIdChars) return false;
    }
    return true;
}

// Fixed dedupe ring: the same client id is never inserted twice, even if
// the event is delivered twice (Core restart, poll retry, ...). Pure and
// bounded: holds the last kMaxSeenIds ids.
struct SeenIds {
    char ids[kMaxSeenIds][kMaxIdChars + 1];
    uint8_t next = 0;
    uint8_t count = 0;
    SeenIds() { memset(ids, 0, sizeof(ids)); }
    bool seen(const char* id) const {
        for (uint8_t i = 0; i < count; ++i)
            if (!strcmp(ids[i], id)) return true;
        return false;
    }
    void add(const char* id) {
        if (seen(id)) return;
        strncpy(ids[next], id, kMaxIdChars);
        ids[next][kMaxIdChars] = 0;
        next = static_cast<uint8_t>((next + 1) % kMaxSeenIds);
        if (count < kMaxSeenIds) ++count;
    }
};

}  // namespace phone_text
}  // namespace maz
