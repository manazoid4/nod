// Nod - LiPo voltage -> percent. Header-only, no Arduino/M5 dependencies.
// Typical single-cell LiPo resting curve. While USB is charging, the cell reads
// HIGHER than its true state of charge, so percent is only an estimate then.
#pragma once
#include <stdint.h>

namespace nod {

struct CurvePoint { uint16_t mv; uint8_t pct; };
static const CurvePoint kLipoCurve[] = {
    {3270, 0},  {3610, 5},  {3690, 10}, {3710, 15}, {3730, 20}, {3750, 25},
    {3770, 30}, {3790, 35}, {3800, 40}, {3820, 45}, {3840, 50}, {3850, 55},
    {3870, 60}, {3910, 65}, {3950, 70}, {3980, 75}, {4020, 80}, {4080, 85},
    {4110, 90}, {4150, 95}, {4200, 100}};
static const int kLipoCurveLen = sizeof(kLipoCurve) / sizeof(kLipoCurve[0]);

inline uint8_t voltageToPercent(int mv) {
    if (mv <= kLipoCurve[0].mv) return 0;
    if (mv >= kLipoCurve[kLipoCurveLen - 1].mv) return 100;
    for (int i = 1; i < kLipoCurveLen; i++) {
        if (mv <= kLipoCurve[i].mv) {
            const CurvePoint& a = kLipoCurve[i - 1];
            const CurvePoint& b = kLipoCurve[i];
            return (uint8_t)(a.pct + (b.pct - a.pct) * (mv - a.mv) / (b.mv - a.mv));
        }
    }
    return 100;
}

}  // namespace nod
