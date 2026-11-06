#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "../include/charge_monitor.h"
#include "../include/home_layout.h"
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
    CHECK(moveSelection(CARD_SUBTITLES, 'R') == CARD_ROUTINES);
    CHECK(moveSelection(CARD_ROUTINES, 'D') == CARD_MORE);
    CHECK(moveSelection(CARD_SUBTITLES, 'L') == CARD_SUBTITLES);
    printf("%d checks, %d failed\n", checks, fails);
    return fails ? 1 : 0;
}
