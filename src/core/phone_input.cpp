#include "phone_input.h"

#include <phone_text.h>

#include <Arduino.h>

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

constexpr size_t kAckCap = 4;
constexpr time_t kClockValidFrom = 1704067200;  // 2024-01-01: wall clock usable

phone_text::SeenIds gSeen;  // a repeated client id is never inserted twice
std::vector<std::pair<std::string, std::string>> gAcks;  // pending (id, status)

void enqueueAck(const std::string& id, const char* status) {
    if (id.empty()) return;
    if (gAcks.size() >= kAckCap) gAcks.erase(gAcks.begin());  // oldest ack lost on flood
    gAcks.emplace_back(id, status);
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
    } else {
        enqueueAck(id, "inserted");
    }
    shell::invalidate();
}

void update() {
    if (host_worker::state() == host_worker::State::Done &&
        host_worker::jobKind() == host_worker::JobKind::TextAck) {
        host_worker::TextAckResult r;
        host_worker::takeTextAckResult(r);  // fire-and-forget: the phone polls GET
    }
    if (gAcks.empty() || host_worker::state() != host_worker::State::Idle) return;
    if (!host::configured()) return;  // queued acks flush when the link is back
    const auto& front = gAcks.front();
    if (host_worker::submitTextAck(front.first, front.second)) gAcks.erase(gAcks.begin());
}

}  // namespace phone
}  // namespace maz
