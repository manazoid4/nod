// CHARGING MODE - a calm, readable screen for when the Cardputer is plugged in.
// Big percent, plain-language status, honest time-to-full, dims itself, any key
// wakes it, ESC leaves. Opens by itself when charging starts at Home.
#include <charge_monitor.h>

#include <cstdio>

#include "../core/settings.h"
#include "../core/shell.h"
#include "../core/sys.h"
#include "apps.h"
#include "common.h"

namespace maz {
namespace apps {

using namespace theme;

namespace {

class ChargingApp final : public App {
public:
    const char* id() const override { return "charge"; }
    const char* title() const override { return "Charging"; }
    const char* hints() const override { return "Any key wakes   ESC exit"; }

    void onEnter() override { _lastKey = millis(); apply(); }
    void onExit() override { M5.Display.setBrightness(Cfg.brightness < 8 ? 8 : Cfg.brightness); }

    bool onKey(const KeyEvent& e) override {
        if (e.down) { _lastKey = millis(); apply(); invalidate(); }
        return false;  // let the shell handle ESC
    }

    void update() override {
        if (millis() - _lastPaint > _policy.refreshMs) { _lastPaint = millis(); apply(); invalidate(); }
    }

    std::string contextSnapshot() const override {
        char b[48]; snprintf(b, sizeof(b), "Battery %d%%, %s", Sys.batteryPct, _policy.title);
        return b;
    }

    void render(M5Canvas& g) override {
        g.fillScreen(BG);
        if (!_policy.screenOn) return;
        const bool full = Sys.powerState == (uint8_t)nod::PowerState::Full;
        const bool chg  = Sys.powerState == (uint8_t)nod::PowerState::Charging;
        const uint16_t col = full ? OK : (chg ? WARN : TEXT);
        char big[8];
        snprintf(big, sizeof(big), "%d%%", full ? 100 : (Sys.batteryPct < 0 ? 0 : Sys.batteryPct));
        g.setTextDatum(middle_center);
        g.setTextColor(col, BG);
        g.setTextSize(4);
        g.drawString(big, SCREEN_W / 2, 40);
        g.setTextSize(2);
        g.setTextColor(TEXT, BG);
        g.drawString(_policy.title, SCREEN_W / 2, 80);
        g.setTextSize(1);
        g.setTextColor(DIM, BG);
        char line[40];
        if (chg && Sys.chargeEtaMin > 0) snprintf(line, sizeof(line), "about %d min to full", Sys.chargeEtaMin);
        else snprintf(line, sizeof(line), "%s", _policy.hint);
        g.drawString(line, SCREEN_W / 2, 100);
        ui::progress(g, 40, 112, SCREEN_W - 80, 6, full ? 1.f : (Sys.batteryPct < 0 ? 0.f : Sys.batteryPct / 100.f), col);
    }

private:
    void apply() {
        _policy = nod::chargeScreenPolicy((nod::PowerState)Sys.powerState, millis(), _lastKey);
        M5.Display.setBrightness(_policy.screenOn ? _policy.backlight : 0);
    }
    nod::ChargeScreen _policy = nod::chargeScreenPolicy(nod::PowerState::Unknown, 0, 0);
    uint32_t _lastKey = 0, _lastPaint = 0;
};

}  // namespace

App* makeCharging() { return new ChargingApp(); }

}  // namespace apps
}  // namespace maz
