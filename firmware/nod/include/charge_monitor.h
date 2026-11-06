// Nod CHARGING MODE - decides "is it charging / full / running on battery"
// from battery-voltage samples, because the Cardputer does not reliably report
// charging (especially under M5Launcher). Optional VBUS hint overrides when the
// firmware can read it. Pure logic: feed samples, read state. No hardware calls.
#pragma once
#include <stdint.h>
#include "battery_curve.h"

namespace nod {

enum class PowerState : uint8_t { Unknown, OnBattery, Charging, Full };

class ChargeMonitor {
public:
    static const int kCap = 24;                  // samples kept
    static const uint32_t kSampleMs = 10000;     // one sample per 10 s
    static const uint32_t kMinWindowMs = 90000;  // need 90 s before judging by trend
    static constexpr float kRiseMvPerMin = 3.0f; // >= this => charging
    static constexpr float kFallMvPerMin = -2.0f;// <= this => on battery
    static const int kFullMv = 4150;

    // vbus: -1 unknown, 0 absent, 1 present.
    void feed(uint32_t nowMs, int mv, int vbus = -1) {
        _mv = mv; _vbus = vbus;
        if (_n == 0 || nowMs - _t[(_head + kCap - 1) % kCap] >= kSampleMs) {
            _t[_head] = nowMs; _v[_head] = mv; _head = (_head + 1) % kCap;
            if (_n < kCap) _n++;
        }
        update(nowMs);
    }
    PowerState state() const { return _state; }
    bool charging() const { return _state == PowerState::Charging || _state == PowerState::Full; }
    int  millivolts() const { return _mv; }
    // Estimated percent. While charging it is capped at 99 until Full is proven.
    uint8_t percent() const {
        uint8_t p = voltageToPercent(_mv);
        if (_state == PowerState::Charging && p > 99) p = 99;
        if (_state == PowerState::Full) p = 100;
        return p;
    }
    // Minutes to full from the OBSERVED rise; -1 if not enough data. No assumed capacity.
    int etaMinutes() const {
        if (_state != PowerState::Charging) return -1;
        float s = slopeMvPerMin();
        if (s < 1.0f) return -1;
        int left = kFullMv - _mv;
        if (left <= 0) return 0;
        // voltage rise slows near the top; pad 1.6x so we under-promise.
        return (int)(left / s * 1.6f + 0.5f);
    }
    float slopeMvPerMin() const {  // least squares over stored samples
        if (_n < 4) return 0;
        double st = 0, sv = 0, stt = 0, stv = 0;
        uint32_t t0 = _t[(_head + kCap - _n) % kCap];
        for (int i = 0; i < _n; i++) {
            int k = (_head + kCap - _n + i) % kCap;
            double t = (_t[k] - t0) / 60000.0, v = _v[k];
            st += t; sv += v; stt += t * t; stv += t * v;
        }
        double d = _n * stt - st * st;
        return d < 1e-9 ? 0.0f : (float)((_n * stv - st * sv) / d);
    }
    uint32_t windowMs() const {
        return _n < 2 ? 0 : _t[(_head + kCap - 1) % kCap] - _t[(_head + kCap - _n) % kCap];
    }

private:
    void update(uint32_t) {
        if (_vbus == 0) { _state = PowerState::OnBattery; _fullSince = 0; return; }
        const bool trend = windowMs() >= kMinWindowMs;
        const float s = slopeMvPerMin();
        if (_vbus == 1) {
            if (_mv >= kFullMv && trend && s < 0.5f) _state = PowerState::Full;
            else if (_state != PowerState::Full || s > 1.0f) _state = PowerState::Charging;
            return;
        }
        if (!trend) return;  // unknown VBUS, not enough data: keep previous state
        if (s >= kRiseMvPerMin) { _state = PowerState::Charging; }
        else if (s <= kFallMvPerMin) { _state = PowerState::OnBattery; }
        else if (_state == PowerState::Charging && _mv >= kFullMv) { _state = PowerState::Full; }
        else if (_state == PowerState::Unknown) { _state = PowerState::OnBattery; }
    }
    uint32_t _t[kCap] = {};
    int      _v[kCap] = {};
    int      _head = 0, _n = 0, _mv = 0, _vbus = -1;
    uint32_t _fullSince = 0;
    PowerState _state = PowerState::Unknown;
};

// What the screen should do in charging mode. Firmware applies this each frame.
struct ChargeScreen {
    uint8_t backlight;    // 0-255
    bool    screenOn;
    uint16_t refreshMs;   // how often to redraw
    const char* title;    // plain-language status
    const char* hint;
};

inline ChargeScreen chargeScreenPolicy(PowerState st, uint32_t nowMs, uint32_t lastKeyMs) {
    const bool awake = (nowMs - lastKeyMs) < 8000;  // any key wakes for 8 s
    switch (st) {
        case PowerState::Charging:
            return {awake ? (uint8_t)180 : (uint8_t)25, true, awake ? (uint16_t)500 : (uint16_t)2000,
                    "Charging", "Any key wakes   ESC exits"};
        case PowerState::Full:
            return {awake ? (uint8_t)180 : (uint8_t)0, awake, (uint16_t)2000,
                    "Fully charged", "Safe to unplug"};
        case PowerState::OnBattery:
            return {200, true, 1000, "On battery", "Plug in USB-C to charge"};
        default:
            return {200, true, 1000, "Checking power...", "Give it a minute"};
    }
}

}  // namespace nod
