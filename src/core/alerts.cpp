#include "alerts.h"

#include <string.h>

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
// Fixed buffers, no heap: this overlay must stay small (firmware size gate) and never fragment.
constexpr uint8_t  MAX_QUEUE = 3;
constexpr uint32_t PULSE_MS = 500;

struct Alert {
    char     id[16], kind[12], title[61], body[201];
    ap::Priority prio;
    uint8_t  actions;
    uint32_t arrivedAt;
};

Alert   gQ[MAX_QUEUE];
uint8_t gN = 0;
// One answer waiting for a free worker slot (ack/snooze -> Core). Keys are ignored until it is sent.
struct { char id[16]; bool snooze, busy; } gOut;

void cp(char* dst, size_t n, const std::string& s) {
    size_t len = s.size() < n - 1 ? s.size() : n - 1;
    if (len < s.size()) while (len && (static_cast<uint8_t>(s[len]) & 0xC0) == 0x80) --len;  // never cut a UTF-8 char
    memcpy(dst, s.data(), len);
    dst[len] = 0;
}
void drop() { for (uint8_t i = 0; i + 1 < gN; ++i) gQ[i] = gQ[i + 1]; --gN; shell::invalidate(); }

void sound(Alert& a) {
    if (ap::shouldSound(static_cast<uint8_t>(quiet::level()), a.prio))
        sfx::alertPattern(ap::rule(a.prio), ap::forced(a.prio));
}

// Wrap `s` into rows of `w` chars starting at `x,y`.
void rows(M5Canvas& g, const char* s, int w, int x, int y, int maxRows, int step) {
    char buf[40];
    for (int r = 0; r < maxRows && static_cast<int>(strlen(s)) > r * w; ++r) {
        strncpy(buf, s + r * w, w);
        buf[w] = 0;
        g.drawString(buf, x, y + r * step);
    }
}
}  // namespace

bool active() { return gN > 0; }

void onEvent(const host::AgentEvent& ev) {
    if (ev.alertId.empty() || ev.title.empty()) return;
    for (uint8_t i = 0; i < gN; ++i) if (!strcmp(ev.alertId.c_str(), gQ[i].id)) return;  // already on screen
    if (gN >= MAX_QUEUE) --gN;  // flood: newest replaces the last queued one
    Alert& a = gQ[gN++];
    cp(a.id, sizeof(a.id), ev.alertId); cp(a.kind, sizeof(a.kind), ev.alertKind);
    cp(a.title, sizeof(a.title), ev.title); cp(a.body, sizeof(a.body), ev.body);
    a.prio = ap::parsePriority(ev.priority.c_str());
    a.actions = ev.alertActions ? ev.alertActions : ap::ACT_ACK;
    a.arrivedAt = millis();
    if (a.prio >= ap::Priority::High) shell::wake();  // low/normal never light the screen
    shell::invalidate();
    if (gN == 1 || a.prio == ap::Priority::Urgent) sound(a);
}

void update() {
    // Fire-and-forget: approvals.cpp collects the worker result (alert ids are ignored there).
    if (gOut.busy && host_worker::state() == host_worker::State::Idle && host::configured() && Sys.wifiConnected)
        gOut.busy = !host_worker::submitBuddyDecide(gOut.id, gOut.snooze ? "snooze" : "ack");
    if (!gN) return;
    // Buddy animation: repaint ~8 fps (the shell repaints every 250 ms by default).
    static uint32_t lastPaint = 0;
    if (millis() - lastPaint > 120) { lastPaint = millis(); shell::invalidate(); }
}

// True only for keys this overlay uses; everything else falls through to the shell.
bool handleKey(const KeyEvent& e) {
    if (!gN) return false;
    const bool ack = e.code == KEY_ENTER || e.code == KEY_A;
    const bool snooze = e.code == KEY_S && (gQ[0].actions & ap::ACT_SNOOZE);
    if (!ack && !snooze && e.code != KEY_ESC) return false;
    if (!e.down) return true;
    if (e.code != KEY_ESC) {
        if (gOut.busy) return true;  // previous answer not sent yet
        memcpy(gOut.id, gQ[0].id, sizeof(gOut.id));
        gOut.snooze = snooze; gOut.busy = true;
    }
    drop();  // Esc hides locally; Core's outcome stays open
    return true;
}

void render(M5Canvas& g) {
    if (!gN) return;
    const Alert& a = gQ[0];
    const uint32_t now = millis();
    const ap::Rule& rule = ap::rule(a.prio);
    const uint16_t c = a.prio == ap::Priority::Urgent ? ERR : a.prio == ap::Priority::High ? WARN : a.prio == ap::Priority::Low ? DIM : ACCENT2;

    // "LED": pulsing screen edge for rule.flashes pulses (or until answered when urgent).
    if ((rule.flashes == ap::FLASH_UNTIL_ACK || now - a.arrivedAt < rule.flashes * PULSE_MS) && ((now / (PULSE_MS / 2)) & 1) == 0)
        g.drawRect(0, 0, SCREEN_W, SCREEN_H, c);

    const int x = 4, y = 18, w = SCREEN_W - 8, h = 100;
    g.fillRoundRect(x, y, w, h, 4, PANEL);
    g.drawRoundRect(x, y, w, h, 4, c);
    buddy_face::draw(g, x + 34, y + 46, 24, ap::moodFor(a.prio, !strcmp(a.kind, "task_done")), now);

    g.setTextDatum(top_left);
    g.setFont(&fonts::Font0);
    g.setTextColor(c, PANEL);
    g.drawString(a.kind, x + 72, y + 4);
    g.setFont(&fonts::Font2);
    g.setTextColor(TEXT, PANEL);
    rows(g, a.title, 19, x + 72, y + 17, 2, 16);
    g.setFont(&fonts::Font0);
    g.setTextColor(DIM, PANEL);
    rows(g, a.body, 26, x + 72, strlen(a.title) > 19 ? y + 52 : y + 36, 2, 11);
    g.setTextColor(ACCENT, PANEL);
    g.drawString((a.actions & ap::ACT_SNOOZE) ? "A ack  S snooze  ESC hide" : "A ack  ESC hide", x + 6, y + h - 12);
}

}  // namespace alerts
}  // namespace maz
