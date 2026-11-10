#include "phone_input.h"

#include <phone_text.h>

#include <Arduino.h>

#include <algorithm>
#include <ctime>
#include <string>
#include <utility>
#include <vector>

#include "../apps/common.h"
#include "../net/host_worker.h"
#include "../net/mazhost.h"
#include "alerts.h"
#include "approvals.h"
#include "notify.h"
#include "settings.h"
#include "shell.h"

namespace maz {
namespace phone {
namespace {

// Core accepts at most 20 pending phone-text messages. Leave spare space for
// acknowledgements already sent but not confirmed when the network drops.
constexpr size_t kAckCap = 24;
constexpr uint32_t kAckTtlMs = 120000;
constexpr time_t kClockValidFrom = 1704067200;  // 2024-01-01: wall clock usable

struct PendingAck {
    std::string id;
    std::string status;
    uint32_t queuedAt;
};
phone_text::SeenIds gSeen;  // a repeated client id is never inserted twice
std::vector<PendingAck> gAcks;
uint32_t gNextAckAttempt = 0;

void enqueueAck(const std::string& id, const char* status) {
    if (id.empty()) return;
    if (gAcks.size() >= kAckCap) {
        // This can only occur after prolonged network trouble / repeated floods.
        // A removed record will expire on Core; never report it as acknowledged.
        gAcks.erase(gAcks.begin());
        notify::post(Note::Warn, "Phone text", "ACK backlog full");
    }
    gAcks.push_back({id, status, millis()});
}

}  // namespace

void onTextInput(const host::AgentEvent& ev) {
    phone_text::Mode mode = phone_text::Mode::Insert;
    if (!phone_text::validId(ev.textInputId.c_str()) ||
        !phone_text::parseMode(ev.textInputMode.c_str(), mode) ||
        ev.text.empty())
        return;
    const std::string& id = ev.textInputId;
    if (gSeen.seen(id.c_str())) return;  // duplicate delivery: never insert twice
    const time_t nowWall = time(nullptr);
    if (!phone_text::fresh(ev.eventTs, nowWall, nowWall >= kClockValidFrom)) return;  // never late
    gSeen.add(id.c_str());

    shell::wake();
    // Overlays own the screen: phone text is never inserted under one, and so
    // can never approve or answer an alert either.
    apps::TextField* field = apps::TextField::phoneTarget();
    if (approvals::active() || alerts::active() ||
        !field || !apps::TextField::phoneTargetFresh(millis())) {
        notify::post(Note::Info, "Phone text", "open a text field first");
        enqueueAck(id, "no_field");
        shell::invalidate();
        return;
    }
    const phone_text::Status st = field->applyPhone(ev.text, mode);
    if (st == phone_text::Status::TooLong) {
        notify::post(Note::Warn, "Phone text", "too long for this field");
        enqueueAck(id, "too_long");
    } else if (st == phone_text::Status::Unsupported) {
        notify::post(Note::Warn, "Phone text", "letters Piblo can't show");
        enqueueAck(id, "unsupported");
    } else {
        enqueueAck(id, "inserted");
    }
    shell::invalidate();
}

void update() {
    if (host_worker::state() == host_worker::State::Done &&
        host_worker::jobKind() == host_worker::JobKind::TextAck) {
        host_worker::TextAckResult r;
        if (host_worker::takeTextAckResult(r)) {
            if (r.ok) {
                // Remove only the exact acknowledgement confirmed by Core.
                const auto it = std::find_if(gAcks.begin(), gAcks.end(),
                                             [&](const PendingAck& a) { return a.id == r.id; });
                if (it != gAcks.end()) gAcks.erase(it);
                gNextAckAttempt = 0;
            } else {
                gNextAckAttempt = millis() + 1500;  // retry transient failures
            }
        }
    }
    // Core discards text after two minutes; do not retain stale ACKs forever
    // if the host was unavailable or the record has expired.
    const uint32_t now = millis();
    gAcks.erase(std::remove_if(gAcks.begin(), gAcks.end(),
                              [now](const PendingAck& a) {
                                  return static_cast<uint32_t>(now - a.queuedAt) > kAckTtlMs;
                              }), gAcks.end());
    if (gAcks.empty() || host_worker::state() != host_worker::State::Idle) return;
    if (!host::configured() || static_cast<int32_t>(now - gNextAckAttempt) < 0) return;
    const auto& front = gAcks.front();
    // Keep it queued until the worker confirms success; submit alone is not delivery.
    host_worker::submitTextAck(front.id, front.status);
}

}  // namespace phone
}  // namespace maz
