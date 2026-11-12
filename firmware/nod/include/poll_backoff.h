// Piblo - poll back-off while Core is unreachable.
//
// A laptop that sleeps or a Core that is stopped makes every poll burn a connect timeout (1.8 s of
// radio on) for nothing. Each consecutive failure doubles the wait up to a cap; one success resets
// the caller's counter, so a Core that comes back is noticed within `cap`. Pure logic for PC tests.
#pragma once
#include <stdint.h>

namespace nod {

inline uint32_t backoffMs(uint32_t baseMs, uint8_t fails, uint32_t capMs) {
    if (capMs < baseMs) capMs = baseMs;  // never poll faster than the caller's own cadence
    uint32_t d = baseMs;
    for (uint8_t i = 0; i < fails && d < capMs; ++i) d = d > capMs / 2 ? capMs : d * 2;
    return d < capMs ? d : capMs;
}

}  // namespace nod
