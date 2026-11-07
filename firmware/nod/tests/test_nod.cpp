#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "../include/charge_monitor.h"
#include "../include/home_layout.h"
#include "../include/talk_home.h"
#include "../include/nod_theme.h"
using namespace nod;
static int fails = 0, checks = 0;
#define CHECK(c) do { checks++; if (!(c)) { fails++; printf("FAIL line %d: %s\n", __LINE__, #c); } } while (0)

static void feedRun(ChargeMonitor& m, uint32_t& t, int startMv, float mvPerMin, int minutes, int vbus = -1) {
    for (int s = 0; s < minutes * 6; s++) {
        t += 10000;
        m.feed(t, startMv + (int)(mvPerMin * (s / 6.0f)), vbus);
    }
}

int main() {
    // battery curve
    CHECK(voltageToPercent(3000) == 0); CHECK(voltageToPercent(4300) == 100);
    CHECK(voltageToPercent(3840) == 50);
    for (int mv = 3000; mv < 4300; mv += 5) CHECK(voltageToPercent(mv) <= voltageToPercent(mv + 5)); // monotonic

    // rising voltage, VBUS unknown => Charging (the M5Launcher case)
    { ChargeMonitor m; uint32_t t = 0; feedRun(m, t, 3700, 6.0f, 5);
      CHECK(m.state() == PowerState::Charging); CHECK(m.etaMinutes() > 0); CHECK(m.percent() <= 99); }
    // falling voltage => OnBattery
    { ChargeMonitor m; uint32_t t = 0; feedRun(m, t, 3900, -3.0f, 5);
      CHECK(m.state() == PowerState::OnBattery); CHECK(m.etaMinutes() == -1); }
    // too little data => stays Unknown, never guesses
    { ChargeMonitor m; uint32_t t = 0; feedRun(m, t, 3700, 6.0f, 1);
      CHECK(m.state() == PowerState::Unknown); }
    // noise on a flat battery must not flip to Charging
    { ChargeMonitor m; uint32_t t = 0; for (int i = 0; i < 60; i++) { t += 10000; m.feed(t, 3800 + (i % 2 ? 4 : -4)); }
      CHECK(m.state() != PowerState::Charging); }
    // full detection with VBUS, plateau at 4.17V
    { ChargeMonitor m; uint32_t t = 0; feedRun(m, t, 4170, 0.0f, 5, 1);
      CHECK(m.state() == PowerState::Full); CHECK(m.percent() == 100); }
    // VBUS removed => immediately OnBattery
    { ChargeMonitor m; uint32_t t = 0; feedRun(m, t, 3700, 6.0f, 5, 1); CHECK(m.state() == PowerState::Charging);
      t += 10000; m.feed(t, 3900, 0); CHECK(m.state() == PowerState::OnBattery); }
    // screen policy: dim while charging, wakes on key, off when full
    { ChargeScreen a = chargeScreenPolicy(PowerState::Charging, 100000, 0);
      ChargeScreen b = chargeScreenPolicy(PowerState::Charging, 100000, 98000);
      CHECK(a.backlight < b.backlight); CHECK(a.refreshMs > b.refreshMs);
      ChargeScreen f = chargeScreenPolicy(PowerState::Full, 100000, 0); CHECK(!f.screenOn && f.backlight == 0); }

    // display profiles
    CHECK(findProfile("nope") == nullptr); CHECK(&profileOrDefault("garbage") == &kProfiles[0]);
    CHECK(!kProfiles[0].verified);  // we have not physically verified anything yet

    // home layout: every profile gets 4 cards, inside bounds, no overlap, big enough to read
    for (int p = 0; p < kProfileCount; p++) {
        const DisplayProfile& d = kProfiles[p]; CHECK(profileUsable(d));
        HomeLayout L = computeHome(d.w, d.h);
        for (int i = 0; i < CARD_COUNT; i++) {
            const Rect& r = L.cards[i];
            CHECK(r.x >= 0 && r.y >= L.statusBar.h && r.x + r.w <= d.w && r.y + r.h <= L.footer.y);
            CHECK(r.w >= 90 && r.h >= 40);
            for (int j = i + 1; j < CARD_COUNT; j++) {
                const Rect& q = L.cards[j];
                CHECK(r.x + r.w <= q.x || q.x + q.w <= r.x || r.y + r.h <= q.y || q.y + q.h <= r.y);
            }
        }
    }
    // firmware body area on the stock panel: y 15..121 (status 15, hints 14)
    { Rect g[CARD_COUNT]; computeGrid({0, 15, 240, 106}, g);
      for (int i = 0; i < CARD_COUNT; i++) {
        CHECK(g[i].y >= 15 && g[i].y + g[i].h <= 121 && g[i].x + g[i].w <= 240);
        CHECK(g[i].w >= 100 && g[i].h >= 40);
      } }
    CHECK(moveSelection(CARD_SUBTITLES, 'R') == CARD_ROUTINES);
    CHECK(moveSelection(CARD_ROUTINES, 'D') == CARD_MORE);
    CHECK(moveSelection(CARD_SUBTITLES, 'L') == CARD_SUBTITLES);

    // ---- talk circle Home ----
    // state machine: full happy path, barge-in, text-only reply, ESC from every state
    CHECK(talkStep(TALK_IDLE, EV_MIC_OPEN) == TALK_LISTENING);
    CHECK(talkStep(TALK_LISTENING, EV_MIC_CLOSE) == TALK_THINKING);
    CHECK(talkStep(TALK_THINKING, EV_REPLY_PLAY) == TALK_SPEAKING);
    CHECK(talkStep(TALK_SPEAKING, EV_REPLY_DONE) == TALK_IDLE);
    CHECK(talkStep(TALK_THINKING, EV_REPLY_DONE) == TALK_IDLE);
    CHECK(talkStep(TALK_SPEAKING, EV_MIC_OPEN) == TALK_LISTENING);
    CHECK(talkStep(TALK_IDLE, EV_MIC_CLOSE) == TALK_IDLE);
    CHECK(talkStep(TALK_LISTENING, EV_REPLY_PLAY) == TALK_LISTENING);
    for (int s = 0; s <= TALK_SPEAKING; s++) {
        CHECK(talkStep((TalkState)s, EV_CANCEL) == TALK_IDLE);
        CHECK(talkStep((TalkState)s, EV_FAIL) == TALK_IDLE);
    }
    CHECK(talkFromSources(false, false, false) == TALK_IDLE);
    CHECK(talkFromSources(false, false, true) == TALK_THINKING);
    CHECK(talkFromSources(false, true, true) == TALK_SPEAKING);
    CHECK(talkFromSources(true, true, true) == TALK_LISTENING);
    // animation helpers stay inside their bounds
    for (uint32_t ms = 0; ms < 20000; ms += 37) {
        const int rr = idleRingRadius(44, ms);
        CHECK(rr >= 47 && rr <= 49);
        CHECK(arcStartDeg(ms) >= 0 && arcStartDeg(ms) < 360);
    }
    CHECK(levelRingRadius(44, -5) == 47 && levelRingRadius(44, 5000) == 52 && levelRingRadius(44, 500) == 49);
    // layout: everything inside the stock 240x135 body (y 15..121), circle ~90 px, nothing overlaps
    { const TalkHomeLayout L = computeTalkHome({0, 15, 240, 106});
      CHECK(L.r * 2 >= 84 && L.r * 2 <= 92);
      CHECK(L.cx - L.r - RING_MAX >= 0 && L.cy - L.r - RING_MAX >= 15 && L.cy + L.r + RING_MAX <= 121);
      for (int i = 0; i < 3; i++) {
        const Rect& b = L.btn[i];
        CHECK(b.x >= L.cx + L.r + RING_MAX && b.x + b.w <= 240 && b.y >= 15 && b.y + b.h <= 121);
        CHECK(b.w >= 100 && b.h >= 24);
        if (i) CHECK(b.y >= L.btn[i - 1].y + L.btn[i - 1].h);
      }
      CHECK(L.sentence.y >= L.btn[2].y + L.btn[2].h && L.sentence.y + L.sentence.h <= 121);
      // pinned: preview/talk.html hard-codes these numbers
      CHECK(L.cx == 56 && L.cy == 68 && L.r == 44);
      CHECK(L.btn[0].x == 112 && L.btn[0].w == 122 && L.btn[0].h == 26);
      CHECK(L.btn[0].y == 19 && L.btn[1].y == 49 && L.btn[2].y == 79 && L.sentence.y == 109); }
    // focus walk
    CHECK(moveTalkFocus(FOCUS_TALK, 'R') == FOCUS_SAVE);
    CHECK(moveTalkFocus(FOCUS_SAVE, 'D') == FOCUS_TODAY);
    CHECK(moveTalkFocus(FOCUS_MORE, 'D') == FOCUS_MORE);
    CHECK(moveTalkFocus(FOCUS_SAVE, 'U') == FOCUS_SAVE);
    CHECK(moveTalkFocus(FOCUS_MORE, 'L') == FOCUS_TALK);
    CHECK(moveTalkFocus(FOCUS_TALK, 'D') == FOCUS_TALK);
    // theme: brand constants convert correctly
    CHECK(theme::rgb565(0xFFFFFF) == 0xFFFF && theme::rgb565(0x000000) == 0);
    CHECK(theme::rgb565(0xFF5A36) == 0xFAC6 && theme::TALK != theme::LIVE);
    CHECK(theme::mix(0x000000, 0xFFFFFF, 128) == 0x7F7F7F);
    printf("%d checks, %d failed\n", checks, fails);
    return fails ? 1 : 0;
}
