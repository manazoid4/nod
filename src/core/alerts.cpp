#include "alerts.h"

#include <algorithm>
#include <string>
#include <vector>

#include "../audio/sfx.h"
#include "../net/host_worker.h"
#include "../ui/buddy_face.h"
#include "../ui/theme.h"
#include "notify.h"
#include "quiet.h"
#include "shell.h"
#include "sys.h"

namespace maz {
namespace alerts {

using namespace theme;
namespace ap = alert_policy;

namespace {
constexpr size_t   MAX_QUEUE = 4;
constexpr uint8_t  MAX_REPEATS = 6;
constexpr uint32_t PULSE_MS = 500;

struct Alert {
    std::string id, kind, title, body;
    ap::Priority prio = ap::Priority::Normal;
    uint8_t  actions = ap::ACT_ACK;
    uint32_t arrivedAt = 0, lastSoundAt = 0;
    uint8_t  repeats = 0;
};

struct Pending { std::string id, action; uint8_t tries = 0; bool submitted = false; };

std::vector<Alert>   gQueue;
std::vector<Pending> gOut;  // answers waiting for the host worker (ack/snooze outcome -> Core)

void sound(Alert& a) {
    a.lastSoundAt = millis();
    if (!ap::shouldSound(static_cast<uint8_t>(quiet::level()), a.prio)) return;
    sfx::alertPattern(ap::rule(a.prio), ap::forced(a.prio));
}

void answer(const char* action) {
    if (gQueue.empty()) return;
    const Alert a = gQueue.front();
    gQueue.erase(gQueue.begin());
    gOut.push_back({a.id, action, 0, false});
    shell::invalidate();
}

uint16_t colourFor(ap::Priority p) {
    return p == ap::Priority::Urgent ? ERR : p == ap::Priority::High ? WARN : p == ap::Priority::Low ? DIM : ACCENT2;
}
}  // namespace

bool active() { return !gQueue.empty(); }

void onEvent(const host::AgentEvent& ev) {
    if (ev.alertId.empty() || ev.title.empty()) return;
    for (const Alert& q : gQueue) if (q.id == ev.alertId) return;  // already on screen
    Alert a;
    a.id = ev.alertId;
    a.kind = ev.alertKind;
    a.title = ev.title.substr(0, 60);
    a.body = ev.body.substr(0, 200);
    a.prio = ap::parsePriority(ev.priority.c_str());
    a.actions = ev.alertActions ? ev.alertActions : ap::ACT_ACK;
    a.arrivedAt = millis();
    if (gQueue.size() >= MAX_QUEUE) gQueue.pop_back();  // flood: the newest replaces the last queued one, older ones stay answerable
    gQueue.push_back(a);
    shell::wake();
    shell::invalidate();
    if (gQueue.size() == 1 || a.prio == ap::Priority::Urgent) sound(gQueue.back());
}

void update() {
    // 1. Collect our own worker result (approvals.cpp never takes this kind).
    if (host_worker::state() == host_worker::State::Done &&
        host_worker::jobKind() == host_worker::JobKind::BuddyAlertAct) {
        host_worker::BuddyAlertActResult r;
        if (host_worker::takeBuddyAlertActResult(r) && !gOut.empty()) {
            Pending& p = gOut.front();
            if (r.ok) {
                const bool snooze = p.action == "snooze";
                gOut.erase(gOut.begin());
                sfx::skipNextNote();
                notify::post(Note::Info, snooze ? "Snoozed" : "Acknowledged", snooze ? "Buddy will nag again in 10 min" : "");
            } else if (++p.tries > 2) {
                gOut.erase(gOut.begin());
                sfx::skipNextNote();
                notify::post(Note::Warn, "Hub unreachable", "answer not saved");
            } else {
                p.submitted = false;
            }
        }
    }
    // 2. Send the next answer when the worker is free.
    if (!gOut.empty() && !gOut.front().submitted && host_worker::state() == host_worker::State::Idle &&
        host::configured() && Sys.wifiConnected)
        gOut.front().submitted = host_worker::submitBuddyAlertAct(gOut.front().id, gOut.front().action);

    // 3. Buddy animation: repaint ~8 fps while an alert is up (the shell only repaints every 250 ms by default).
    static uint32_t lastPaint = 0;
    if (!gQueue.empty() && millis() - lastPaint > 120) { lastPaint = millis(); shell::invalidate(); }

    // 4. Re-sound an unanswered alert on its own schedule (priority table).
    if (gQueue.empty()) return;
    Alert& a = gQueue.front();
    const uint16_t every = ap::rule(a.prio).repeatSec;
    if (every && a.repeats < MAX_REPEATS && millis() - a.lastSoundAt > every * 1000u) {
        ++a.repeats;
        sound(a);
    }
}

bool handleKey(const KeyEvent& e) {
    if (gQueue.empty()) return false;
    if (!e.down) return true;
    if (e.code == KEY_ENTER || e.code == KEY_A) answer("ack");
    else if (e.code == KEY_S && (gQueue.front().actions & ap::ACT_SNOOZE)) answer("snooze");
    else if (e.code == KEY_ESC) { gQueue.erase(gQueue.begin()); shell::invalidate(); }  // hide locally, Core outcome stays open
    return true;
}

void render(M5Canvas& g) {
    if (gQueue.empty()) return;
    const Alert& a = gQueue.front();
    const uint32_t now = millis();
    const ap::Rule& rule = ap::rule(a.prio);
    const uint16_t c = colourFor(a.prio);

    // "LED": pulsing screen edge for rule.flashes pulses (or until answered when urgent).
    const bool pulsing = rule.flashes == ap::FLASH_UNTIL_ACK || now - a.arrivedAt < rule.flashes * PULSE_MS;
    if (pulsing && ((now / (PULSE_MS / 2)) % 2) == 0) {
        g.drawRect(0, 0, SCREEN_W, SCREEN_H, c);
        g.drawRect(1, 1, SCREEN_W - 2, SCREEN_H - 2, c);
        g.drawRect(2, 2, SCREEN_W - 4, SCREEN_H - 4, c);
    }

    const int x = 4, y = 18, w = SCREEN_W - 8, h = 100;
    g.fillRoundRect(x, y, w, h, 4, PANEL);
    g.drawRoundRect(x, y, w, h, 4, c);
    buddy_face::draw(g, x + 34, y + 46, 24, ap::moodFor(a.prio, a.kind == "task_done"), now);

    const char* prio = a.prio == ap::Priority::Urgent ? "URGENT" : a.prio == ap::Priority::High ? "HIGH"
                     : a.prio == ap::Priority::Low ? "LOW" : "";
    std::string head = a.kind;
    for (char& ch : head) ch = static_cast<char>(toupper(static_cast<unsigned char>(ch)));
    if (*prio) head += std::string(" / ") + prio;
    g.setTextDatum(top_left);
    g.setFont(&fonts::Font0);
    g.setTextColor(c, PANEL);
    g.drawString(head.c_str(), x + 72, y + 5);
    if (gQueue.size() > 1) {
        char m[12];
        snprintf(m, sizeof(m), "+%u more", static_cast<unsigned>(gQueue.size() - 1));
        g.setTextDatum(top_right);
        g.drawString(m, x + w - 6, y + 5);
        g.setTextDatum(top_left);
    }
    g.setFont(&fonts::Font2);
    g.setTextColor(TEXT, PANEL);
    const std::string t1 = a.title.substr(0, 19), t2 = a.title.size() > 19 ? a.title.substr(19, 19) : "";
    g.drawString(t1.c_str(), x + 72, y + 17);
    if (!t2.empty()) g.drawString(t2.c_str(), x + 72, y + 33);
    g.setFont(&fonts::Font0);
    g.setTextColor(DIM, PANEL);
    const int by = t2.empty() ? y + 36 : y + 52;
    for (int line = 0; line < 3 && static_cast<size_t>(line) * 26 < a.body.size(); ++line)
        g.drawString(a.body.substr(static_cast<size_t>(line) * 26, 26).c_str(), x + 72, by + line * 11);

    g.setTextColor(ACCENT, PANEL);
    g.drawString((a.actions & ap::ACT_SNOOZE) ? "ENT/A ack  S snooze  ESC hide" : "ENT/A ack  ESC hide", x + 6, y + h - 12);
}

}  // namespace alerts
}  // namespace maz
